"""Обработчик окна проекта."""
import base64
import json

from PySide6.QtCore import Signal, QDateTime, Qt

from client.src.src.handlers.window_handlers.base import BaseWindowHandler
from client.src.gui.windows.project_window import ProjectWindow
from client.src.gui.windows.task_dialog_window import TaskDialogWindow
from client.src.requester.requester import Requester
from client.src.gui.main_view import MainWindow
from client.src.client_model.model import Model
import client.models.common_models as cm
from common.logger import config_logger, CLIENT
from client.src.base import LOG_DIR, MAX_FILE_SIZE, MAX_BACKUP_FILES, LOGGING_LEVEL
from client.src.base import _decode_user_id_from_token

logger = config_logger(__name__, CLIENT, LOG_DIR, MAX_FILE_SIZE, MAX_BACKUP_FILES, LOGGING_LEVEL)


class ProjectWindowHandler(BaseWindowHandler):
    """
    Обработчик окна проекта.
    
    Управляет отображением информации о проекте, задачами, участниками.
    Обрабатывает права доступа на основе роли пользователя.
    
    :var project_data_received: Сигнал при получении данных о проекте.
    :var tasks_data_received: Сигнал при получении данных о задачах.
    :var participants_data_received: Сигнал при получении данных об участниках проекта.
    :var stages_data_received: Сигнал при получении данных об этапах проекта.
    """

    project_data_received = Signal(dict)
    tasks_data_received = Signal(list)
    participants_data_received = Signal(list)
    stages_data_received = Signal(list)
    tried_to_return = Signal()  # Сигнал для возврата на предыдущее окно
    
    # Роли и их ID
    ROLE_ADMINISTRATOR = 4
    ROLE_MENTOR = 1
    ROLE_STUDENT = 2
    ROLE_TEAM_LEAD = 3
    
    # Статусы задач
    STATUS_PLANNED = 1  # Запланировано
    STATUS_IN_PROGRESS = 2  # В работе
    STATUS_REVIEW = 3  # Проверяется
    STATUS_DONE = 4  # Выполнено
    STATUS_IMPROVE = 5  # Доработать
    
    # Статусы этапов
    STAGE_STATUS_FINISHED = 'завершён'
    STAGE_STATUS_CURRENT = 'сейчас'
    STAGE_STATUS_FUTURE = 'планируется'

    def __init__(self, window: ProjectWindow, main_view: MainWindow, requester: Requester, model: Model,
                 project_id: int, project_name: str, workspace_id: int):
        super().__init__(window, main_view, requester, model)
        
        self._window: ProjectWindow = window
        self._requester = requester
        self._model = model
        self._project_id = project_id
        self._workspace_id = workspace_id
        
        # Данные о текущем пользователе и его роли
        self._user_role_id: int = 0
        self._user_role_name: str = ""
        self._user_id: int = _decode_user_id_from_token(self._model.get_access_token()) or 0
        self._user_email: str = ""
        
        # Данные о проекте
        self._project_data: dict = {}
        self._tasks: list[cm.WSTask] = []
        self._students: list[dict] = []  # Студенты для выбора исполнителя
        self._participants: list[dict] = []  # Участники проекта (студенты + тимлид + наставники)
        self._stages: list[dict] = []  # Этапы проекта

        # Обработчик окна диалога задачи
        self._task_dialog_handler: TaskDialogHandler | None = None
        
        # Подключение сигналов окна
        self._window.back_pressed.connect(self._on_back_pressed)
        self._window.create_task_pressed.connect(self._on_create_task_pressed)
        self._window.task_edit_requested.connect(self._on_task_edit_requested)
        self._window.task_view_requested.connect(self._on_task_view_requested)
        self._window.task_status_changed.connect(self._on_task_status_changed)

        # Подключение сигналов сохранения/отмены полей инфо
        self._window.goal_save_pressed.connect(self._on_goal_save_pressed)
        self._window.goal_cancel_pressed.connect(self._on_goal_cancel_pressed)
        self._window.tasks_save_pressed.connect(self._on_tasks_save_pressed)
        self._window.tasks_cancel_pressed.connect(self._on_tasks_cancel_pressed)
        self._window.relevance_save_pressed.connect(self._on_relevance_save_pressed)
        self._window.relevance_cancel_pressed.connect(self._on_relevance_cancel_pressed)
        self._window.problem_save_pressed.connect(self._on_problem_save_pressed)
        self._window.problem_cancel_pressed.connect(self._on_problem_cancel_pressed)
        self._window.thesis_save_pressed.connect(self._on_thesis_save_pressed)
        self._window.thesis_cancel_pressed.connect(self._on_thesis_cancel_pressed)
        self._window.save_all_pressed.connect(self._on_save_all_pressed)

        # Подключение сигналов работы с этапами
        self._window.request_stage_transition_pressed.connect(self._on_request_stage_transition)
        self._window.confirm_stage_transition_pressed.connect(self._on_confirm_stage_transition)
        self._window.reject_stage_transition_pressed.connect(self._on_reject_stage_transition)

    def _on_back_pressed(self):
        """Обработка нажатия кнопки возврата."""
        logger.info('Back pressed in project window')
        self.tried_to_return.emit()

    def _on_goal_save_pressed(self, text: str):
        self._save_project_field('goal', text)

    def _on_goal_cancel_pressed(self):
        self._reset_field('goal')

    def _on_tasks_save_pressed(self, text: str):
        self._save_project_field('tasks_description', text)

    def _on_tasks_cancel_pressed(self):
        self._reset_field('tasks_description')

    def _on_relevance_save_pressed(self, text: str):
        self._save_project_field('relevance', text)

    def _on_relevance_cancel_pressed(self):
        self._reset_field('relevance')

    def _on_problem_save_pressed(self, text: str):
        self._save_project_field('problem', text)

    def _on_problem_cancel_pressed(self):
        self._reset_field('problem')

    def _on_thesis_save_pressed(self, text: str):
        self._save_project_field('thesis', text)

    def _on_thesis_cancel_pressed(self):
        self._reset_field('thesis')

    def _on_save_all_pressed(self):
        """Обработка нажатия кнопки 'Сохранить все'."""
        access_token = self._model.get_access_token()
        info = self._window.get_project_info()
        request = self._requester.update_project(
            project_id=self._project_id,
            goal=info['goal'],
            relevance=info['relevance'],
            tasks_description=info['tasks'],
            problem=info['problem'],
            thesis=info['theses'],
            access_token=access_token
        )
        request.finished.connect(lambda req: self._prepare_request(req, self._on_all_fields_saved))

    def _on_all_fields_saved(self, _: dict):  # пустое поле, т.к. prepare_request передаёт данные в метод
        """Обработка успешного сохранения всех полей."""
        logger.info('All project fields saved')
        self._main_view.show_message('Сохранено', 'Все поля проекта успешно обновлены')
        self.update_state()

    def _save_project_field(self, field_name: str, value: str):
        """Сохраняет конкретное поле проекта на сервере."""
        access_token = self._model.get_access_token()
        info = self._window.get_project_info()
        request = self._requester.update_project(
            project_id=self._project_id,
            goal=info['goal'],
            relevance=info['relevance'],
            tasks_description=info['tasks'],
            problem=info['problem'],
            thesis=info['theses'],
            access_token=access_token
        )
        request.finished.connect(lambda req: self._prepare_request(req, lambda data: self._on_field_saved(field_name, data)))

    def _on_field_saved(self, field_name: str, data: dict):
        """Обработка успешного сохранения поля."""
        logger.info(f'Project field {field_name} saved')
        self._main_view.show_message('Сохранено', f'Поле успешно обновлено')
        self.update_state()

    def _reset_field(self, field_name: str):
        """Сбрасывает поле к исходному значению из загруженных данных проекта."""
        if not self._project_data:
            return
        field_map = {
            'goal': 'goal',
            'tasks_description': 'tasks',
            'relevance': 'relevance',
            'problem': 'problem',
            'thesis': 'theses'
        }
        ui_field_map = {
            'goal': self._window._view.text_edit_goal,
            'tasks_description': self._window._view.text_edit_tasks,
            'relevance': self._window._view.text_edit_relevance,
            'problem': self._window._view.text_edit_problem,
            'thesis': self._window._view.text_edit_theses
        }
        original_value = self._project_data.get(field_map.get(field_name, field_name), '')
        ui_field = ui_field_map.get(field_name)
        if ui_field:
            ui_field.setText(original_value)

    def _on_create_task_pressed(self):
        """Обработка нажатия кнопки создания задачи."""
        self._open_task_dialog()
    
    def _open_task_dialog(self, task_id: int | None = None, readonly: bool = False):
        """
        Открывает диалоговое окно создания/редактирования задачи.

        :param task_id: ID задачи (None для создания новой).
        :param readonly: Режим только для чтения.
        """
        # Получаем данные для диалога
        task_data = None
        if task_id:
            task = self._get_task_by_id(task_id)
            if task:
                task_data = task

        # Формируем список исполнителей (все пользователи проекта — студенты и тимлид)
        executors = [(s.get('email', ''), s.get('id', 0))
                     for s in self._students]

        # Получаем данные задачи для редактирования
        name = task_data.get('name', '') if task_data else ''
        description = task_data.get('description', '') if task_data else ''
        executor_email = task_data.get('executor_email', '') if task_data else ''

        plan_start = None
        plan_deadline = None
        if task_data:
            plan_start_str = task_data.get('plan_start_work_date')
            plan_deadline_str = task_data.get('plan_deadline')
            if plan_start_str:
                plan_start = self._parse_date_string(plan_start_str)
            if plan_deadline_str:
                plan_deadline = self._parse_date_string(plan_deadline_str)

        dialog = TaskDialogWindow(
            task_id=task_id,
            name=name,
            description=description,
            executor_email=executor_email,
            plan_start=plan_start,
            plan_deadline=plan_deadline,
            executors=executors,
            readonly=readonly,
            parent=self._main_view
        )

        self._task_dialog_handler = TaskDialogHandler(
            dialog, self._main_view, self._requester, self._model, self
        )
        self._task_dialog_handler.save_pressed.connect(self._on_task_dialog_save)

        dialog.finished.connect(self._on_task_dialog_closed)

        dialog.exec()
    
    def _on_task_dialog_save(self, data: dict):
        """
        Обработка сохранения задачи.

        :param data: Данные задачи.
        """
        access_token = self._model.get_access_token()
        task_id = data.get('task_id')

        if task_id is None:
            # Создание новой задачи
            request = self._requester.create_ws_task(
                project_id=self._project_id,
                name=data['name'],
                description=data['description'],
                executor_email=data['executor_email'],
                plan_start=data['plan_start'],
                plan_deadline=data['plan_deadline'],
                access_token=access_token
            )
            request.finished.connect(lambda req: self._prepare_request(req, self._on_task_created))
        else:
            # Редактирование существующей задачи
            request = self._requester.update_ws_task(
                task_id=task_id,
                name=data['name'],
                description=data['description'],
                executor_id=data['executor_id'],
                plan_start=data['plan_start'],
                plan_deadline=data['plan_deadline'],
                access_token=access_token
            )
            request.finished.connect(lambda req: self._prepare_request(req, self._on_task_updated))

    def _on_task_created(self, data: dict):
        """Обработка создания задачи. После создания обновляется состояние окна."""
        logger.info(f'Task created: {data}')
        self._show_task_created_message()
        self.update_state()

    def _on_task_updated(self, data: dict):
        """Обработка обновления задачи. После обновления обновляется состояние окна."""
        logger.info(f'Task updated: {data}')
        self._main_view.show_message('Сохранено', 'Задача успешно обновлена')
        self.update_state()

    def _on_task_dialog_closed(self, result):
        """Обработка закрытия диалога задачи."""
        self._task_dialog_handler = None
    
    def _on_task_edit_requested(self, task_id: int):
        """
        Обработка запроса редактирования задачи.

        :param task_id: ID задачи.
        """
        self._open_task_dialog(task_id, readonly=False)

    def _on_task_view_requested(self, task_id: int):
        """
        Обработка запроса просмотра задачи (read-only).

        :param task_id: ID задачи.
        """
        self._open_task_dialog(task_id, readonly=True)

    def _on_task_status_changed(self, task_id: int, new_status_id: int):
        """
        Обработка смены статуса задачи.
        
        :param task_id: ID задачи.
        :param new_status_id: Новый ID статуса.
        """
        access_token = self._model.get_access_token()
        print(f'NEW STATUS ID: {new_status_id}')
        request = self._requester.set_ws_task_status_id(task_id, new_status_id, access_token)
        request.finished.connect(lambda req: self._prepare_request(req, self._on_task_status_updated))
    
    def _on_task_status_updated(self, data: dict):
        """Обработка обновления статуса задачи."""
        logger.info(f'Task status updated: {data}')
        self.update_state()
    
    def _show_task_created_message(self):
        """Показывает сообщение о создании задачи."""
        self._main_view.show_message('Задача запланирована!', 'Задача успешно запланирована!')
    
    def _get_task_by_id(self, task_id: int) -> dict | None:
        """
        Получает задачу по ID.
        
        :param task_id: ID задачи.
        :return: Данные задачи или None.
        """
        for task in self._tasks:
            if task.get('id') == task_id:
                return task
        return None
    
    def _on_user_role_received(self, data: dict):
        """
        Обработка получения роли пользователя.
        
        :param data: Данные роли.
        """
        if data:
            self._user_role_id = data.get('id', 0)
            self._user_role_name = data.get('name', '')
            logger.info(f'User role: {self._user_role_name} (id={self._user_role_id})')
            self._apply_role_restrictions()
        else:
            logger.warning('User role not found')
    
    def _apply_role_restrictions(self):
        """Применяет ограничения на основе роли пользователя."""
        # Администратор - без ограничений
        # Наставник - не может удалить проект
        # Ученик, Тимлид - не могут редактировать название и описание, план
        if self._user_role_id in [self.ROLE_STUDENT, self.ROLE_TEAM_LEAD]:
            self._window.set_editable(False)
        else:
            self._window.set_editable(True)
    
    def _on_project_data_received(self, data: dict):
        """
        Обработка получения данных о проекте.
        
        :param data: Данные проекта.
        """

        if not data:
            return

        # Если пришел список проектов, берем первый
        if isinstance(data, list):
            if not data:
                return
            project_data = data[0]
        elif isinstance(data, dict):
            project_data = data
        else:
            return

        self._project_data = project_data

        # Установка информации о проекте
        self._window.set_project_info(
            goal=project_data.get('goal', ''),
            tasks=project_data.get('tasks_description', ''),
            problem=project_data.get('problem', ''),
            relevance=project_data.get('relevance', ''),
            theses=project_data.get('thesis', '')
        )

        self.project_data_received.emit(project_data)
        logger.info(f'Project data received: {project_data.get("name")}')

    def _on_tasks_received(self, data: list):
        """
        Обработка получения задач.

        :param data: Список задач.
        """
        print(f'Tasks received: {data}')
        if not data:
            return

        self._tasks.clear()
        self._window.clear_task_cards()

        for task_data in data:
            if isinstance(task_data, dict):
                self._tasks.append(task_data)

        # Собираем уникальные creator_id для получения email
        creator_ids = set()
        for task in self._tasks:
            creator_id = task.get('creator')
            print(f'Task_status: {task.get('status')}')
            if creator_id:
                creator_ids.add(creator_id)

        if creator_ids:
            access_token = self._model.get_access_token()
            request = self._requester.get_users(list(creator_ids), access_token)
            request.finished.connect(
                lambda req: self._prepare_request(req, self._on_task_creators_received)
            )
        else:
            self._create_task_cards({})

    def _on_task_creators_received(self, users_data: list):
        """
        Обработка получения данных о создателях задач.

        :param users_data: Список пользователей.
        """
        creator_emails = {}
        if isinstance(users_data, list):
            for user in users_data:
                if isinstance(user, dict):
                    creator_emails[user.get('id')] = user.get('email', 'Неизвестно')
        self._create_task_cards(creator_emails)

    def _create_task_cards(self, creator_emails: dict):
        """
        Создаёт карточки задач с полученными данными.

        :param creator_emails: Словарь creator_id -> email.
        """
        for task_data in self._tasks:
            # Определение колонки по статусу
            status_id = task_data.get('status', 1)
            column_index = status_id - 1  # Статус 1 -> колонка 0 и т.д.

            # Получение email исполнителя
            executor_email = task_data.get('executor_email', '')
            if not executor_email:
                executor_id = task_data.get('executor_id')
                if executor_id:
                    executor_email = f'ID: {executor_id}'
            if not executor_email:
                executor_email = 'Не назначен'

            # Получение email создателя
            creator_id = task_data.get('creator')
            creator_email = creator_emails.get(creator_id, 'Неизвестно')

            # Даты
            plan_start = task_data.get('plan_start_work_date', 'Не указан')
            plan_deadline = task_data.get('plan_deadline', 'Не указан')
            print(f'PLAN_START: {plan_start} | {task_data}')
            self._window.add_task_card(
                task_id=task_data.get('id', 0),
                name=task_data.get('name', ''),
                description=task_data.get('description', ''),
                creator_email=creator_email,
                executor_email=executor_email,
                plan_start=plan_start,
                plan_deadline=plan_deadline,
                status_id=status_id,
                column_index=column_index
            )

        self.tasks_data_received.emit(self._tasks)
        logger.info(f'Tasks received: {len(self._tasks)} tasks')
    
    def _on_project_users_received(self, data: list):
        """
        Обработка получения пользователей проекта.
        get_project_users возвращает project_user (студенты + тимлид).
        """
        if not data:
            self._students = []
            logger.info('Project users received: no users')
            return

        self._students = data
        logger.info(f'Project users received: {len(data)} students+teamleads')

    def _on_project_mentors_received(self, data: list):
        """
        Обработка получения наставников проекта.
        """
        if not data:
            logger.info('Project mentors received: no mentors')
            self._combine_participants([])
            return

        # Наставники добавляются к списку участников
        logger.info(f'Project mentors received: {len(data)} mentors')
        self._combine_participants(data)

    def _combine_participants(self, mentors: list):
        """
        Объединяет студентов/тимлидов и наставников в общий список участников.

        :param mentors: Список наставников.
        """
        # Создаем словарь для хранения участников по email для избежания дубликатов
        participants_dict = {}

        # Добавляем студентов и тимлидов
        for user in self._students:
            if isinstance(user, dict):
                email = user.get('email', '')
                if email:
                    participants_dict[email] = {
                        'user_id': user.get('id', 0),
                        'username': user.get('username', user.get('email', 'Unknown')),
                        'email': email,
                        'role_name': self._get_role_name(user.get('roles', [0])[0]),
                        'role_id': user.get('roles', [0])[0]
                    }

        # Добавляем наставников
        for mentor in mentors:
            if isinstance(mentor, dict):
                email = mentor.get('email', '')
                if email and email not in participants_dict:
                    participants_dict[email] = {
                        'user_id': mentor.get('id', 0),
                        'username': mentor.get('username', mentor.get('email', 'Unknown')),
                        'email': email,
                        'role_name': self._get_role_name(mentor.get('roles', [0])[0]),
                        'role_id': mentor.get('roles', [0])[0]
                    }

        # Преобразуем словарь в список
        self._participants = list(participants_dict.values())

        # Отображаем участников в окне
        self._display_participants()

    def _get_role_name(self, role_id: int) -> str:
        """
        Получает название роли по ID.

        :param role_id: ID роли.
        :return: Название роли.
        """
        roles = {
            self.ROLE_MENTOR: "Наставник",
            self.ROLE_STUDENT: "Студент",
            self.ROLE_ADMINISTRATOR: "Администратор",
            self.ROLE_TEAM_LEAD: "Тимлид"
        }
        return roles.get(role_id, "Неизвестная роль")

    def _display_participants(self):
        """
        Отображает участников проекта в окне.
        """
        self._window.clear_participant_widgets()

        for participant_data in self._participants:
            can_edit = self._user_role_id == self.ROLE_ADMINISTRATOR

            widget = self._window.add_participant_widget(
                username=participant_data.get('username', 'Unknown'),
                email=participant_data.get('email', 'unknown@example.com'),
                role_name=participant_data.get('role_name', 'Неизвестная роль'),
                can_edit=can_edit
            )

        self.participants_data_received.emit(self._participants)
        logger.info(f'Participants displayed: {len(self._participants)} participants')

    # Методы для работы с этапами
    def _on_request_stage_transition(self):
        """Обработка запроса на переход к следующему этапу."""
        logger.info('Stage transition requested')
        # Информация о запросе никуда не сохраняется, только визуальное изменение

    def _on_confirm_stage_transition(self):
        """Обработка подтверждения перехода к следующему этапу."""
        access_token = self._model.get_access_token()

        # Формируем данные для обновления этапов
        stages_update_data = []
        current_stage_index = None
        new_stage_id = None

        for i, stage in enumerate(self._stages):
            stage_update = {
                'id': stage.get('id'),
                'is_finished': stage.get('is_finished'),
                'is_current': stage.get('is_current'),
                'is_future': stage.get('is_future')
            }

            if stage.get('is_current'):
                current_stage_index = i
                # Текущий этап становится завершенным
                stage_update['is_finished'] = True
                stage_update['is_current'] = False
                stage_update['is_future'] = False
            elif current_stage_index is not None and i == current_stage_index + 1:
                # Следующий этап становится текущим
                stage_update['is_finished'] = False
                stage_update['is_current'] = True
                stage_update['is_future'] = False
                new_stage_id = stage.get('id')  # Запоминаем ID нового текущего этапа
            elif current_stage_index is not None and i > current_stage_index + 1:
                # Все последующие этапы остаются будущими
                stage_update['is_finished'] = False
                stage_update['is_current'] = False
                stage_update['is_future'] = True

            stages_update_data.append(stage_update)

        # Обновляем этапы проекта
        request = self._requester.update_project_stages(
            project_id=self._project_id,
            stages_data=stages_update_data,
            access_token=access_token
        )
        request.finished.connect(lambda req: self._prepare_request(req, self._on_stages_updated))

        # Если новый этап определён, обновляем current_stage_id проекта
        if new_stage_id is not None:
            stage_update_request = self._requester.update_project_current_stage(
                project_id=self._project_id,
                current_stage_id=new_stage_id,
                access_token=access_token
            )
            stage_update_request.finished.connect(
                lambda req: self._prepare_request(req, self._on_project_current_stage_updated)
            )

    def _on_reject_stage_transition(self):
        """Обработка отклонения перехода к следующему этапу."""
        logger.info('Stage transition rejected')
        self._window.reset_transition_buttons()

    def _on_stages_updated(self, data: dict):
        """Обработка успешного обновления этапов."""
        logger.info(f'Stages updated: {data}')
        self._main_view.show_message('Успешно', 'Переход на следующий этап выполнен')
        self._window.reset_transition_buttons()
        self.update_state()

    def _on_project_current_stage_updated(self, data: dict):
        """Обработка успешного обновления current_stage_id проекта."""
        logger.info(f'Project current_stage_id updated: {data}')
        # Данные уже обновлены в _on_stages_updated, здесь только логирование

    def _on_stages_received(self, data: list):
        """
        Обработка получения данных об этапах проекта.

        :param data: Список этапов.
        """
        if not data:
            logger.info('No stages received for project')
            return

        self._stages.clear()
        self._window.clear_stage_widgets()

        for stage_data in data:
            if isinstance(stage_data, dict):
                self._stages.append(stage_data)

        # Отображение этапов
        self._display_stages()

        self.stages_data_received.emit(self._stages)
        logger.info(f'Stages received: {len(self._stages)} stages')

    def _display_stages(self):
        """Отображает этапы проекта в окне."""
        for stage_data in self._stages:
            # Определение статуса для отображения
            if stage_data.get('is_finished'):
                status = self.STAGE_STATUS_FINISHED
            elif stage_data.get('is_current'):
                status = self.STAGE_STATUS_CURRENT
            elif stage_data.get('is_future'):
                status = self.STAGE_STATUS_FUTURE
            else:
                status = self.STAGE_STATUS_FUTURE

            # Форматирование дат
            date_start = stage_data.get('date_start', 'Не указана')
            date_end = stage_data.get('date_end', 'Не указана')

            # Преобразование дат в строковый формат
            if isinstance(date_start, str):
                date_start_str = date_start
            elif hasattr(date_start, 'strftime'):
                date_start_str = date_start.strftime('%d.%m.%Y')
            else:
                date_start_str = str(date_start) if date_start else 'Не указана'

            if isinstance(date_end, str):
                date_end_str = date_end
            elif hasattr(date_end, 'strftime'):
                date_end_str = date_end.strftime('%d.%m.%Y')
            else:
                date_end_str = str(date_end) if date_end else 'Не указана'

            # Получение полного описания из result
            description = stage_data.get('result', '')
            result = description  # Планируемый результат

            self._window.add_stage_widget(
                name=stage_data.get('name', 'Без названия'),
                description=description,
                date_start=date_start_str,
                date_end=date_end_str,
                result=result,
                status=status,
                stage_id=stage_data.get('id', 0)
            )

    @staticmethod
    def _parse_date_string(date_str: str) -> QDateTime:
        """
        Парсит строку даты в QDateTime с поддержкой нескольких форматов.

        :param date_str: Строка даты для парсинга.
        :return: QDateTime объект или невалидный QDateTime если парсинг не удался.
        """
        if not date_str:
            return QDateTime()

        # Список форматов для попытки парсинга
        date_formats = [
            Qt.ISODate,                        # 2024-01-15T10:30:00
            'yyyy-MM-dd HH:mm:ss',             # 2024-01-15 10:30:00
            'yyyy-MM-dd HH:mm:ss.zzz',         # 2024-01-15 10:30:00.123
            'yyyy-MM-dd',                       # 2024-01-15
            'dd.MM.yyyy HH:mm:ss',              # 15.01.2024 10:30:00
            'dd.MM.yyyy HH:mm',                 # 15.01.2024 10:30
            'dd.MM.yyyy',                       # 15.01.2024
        ]

        for date_format in date_formats:
            dt = QDateTime.fromString(date_str, date_format)
            if dt.isValid():
                return dt

        # Если ни один формат не подошел, возвращаем невалидный
        return QDateTime()

    def update_state(self):
        """
        Обновляет состояние обработчика.
        
        Загружает данные о проекте, роли пользователя, задачах и участниках проекта.
        """
        logger.info(f'Updating project window: project_id={self._project_id}')
        
        access_token = self._model.get_access_token()
        
        # Запрос данных проекта
        project_request = self._requester.get_project_by_id(self._project_id, access_token)
        project_request.finished.connect(lambda req: self._prepare_request(req, self._on_project_data_received))

        # Запрос роли пользователя
        role_request = self._requester.get_user_role_in_workspace(
            self._workspace_id, self._user_id, access_token)
        role_request.finished.connect(lambda req: self._prepare_request(req, self._on_user_role_received))
        
        # Запрос задач проекта
        tasks_request = self._requester.get_ws_tasks_by_project(
            self._project_id, access_token, limit=100, offset=0)
        tasks_request.finished.connect(lambda req: self._prepare_request(req, self._on_tasks_received))
        
        # Запрос пользователей проекта
        users_request = self._requester.get_project_users(
            self._project_id, access_token, limit=100, offset=0)
        users_request.finished.connect(lambda req: self._prepare_request(req, self._on_project_users_received))

        # Запрос наставников проекта
        mentors_request = self._requester.get_project_mentors(
            self._workspace_id, self._project_id, access_token, limit=100, offset=0)
        mentors_request.finished.connect(lambda req: self._prepare_request(req, self._on_project_mentors_received))

        # Запрос этапов проекта
        stages_request = self._requester.get_project_stages(
            self._project_id, access_token, limit=100, offset=0)
        stages_request.finished.connect(lambda req: self._prepare_request(req, self._on_stages_received))

    def update_data(self):
        """Обновляет данные в обработчике."""
        self.update_state()
    
    def project_id(self) -> int:
        """Возвращает ID проекта."""
        return self._project_id
    
    def workspace_id(self) -> int:
        """Возвращает ID рабочего пространства."""
        return self._workspace_id
    
    def user_role_id(self) -> int:
        """Возвращает ID роли пользователя."""
        return self._user_role_id
    
    def user_role_name(self) -> str:
        """Возвращает название роли пользователя."""
        return self._user_role_name


class TaskDialogHandler(BaseWindowHandler):
    """
    Обработчик диалога задачи.
    
    :param parent_handler: Родительский обработчик (ProjectWindowHandler).
    """
    
    save_pressed = Signal(dict)  # Сигнал с валидными данными задачи

    def __init__(self, window: TaskDialogWindow, main_view: MainWindow,
                 requester: Requester, model: Model, parent_handler: ProjectWindowHandler):
        super().__init__(window, main_view, requester, model)
        
        self._window = window
        self._parent_handler = parent_handler
        
        self._window.try_save_pressed.connect(self._on_try_save_pressed)

    def _on_try_save_pressed(self):
        """
        Обработка попытки сохранения задачи.
        Проверяет заполнение всех полей перед отправкой.
        """
        data = self._window.get_task_data()

        # Проверка обязательных полей
        if not data['name']:
            self._main_view.show_message('Ошибка', 'Введите название задачи')
            return
        if not data['description']:
            self._main_view.show_message('Ошибка', 'Введите описание задачи')
            return
        if not data['executor_email']:
            self._main_view.show_message('Ошибка', 'Выберите исполнителя')
            return

        self._window.accept()
        self.save_pressed.emit(data)

    def press_save(self, data: dict):
        self.save_pressed.emit(data)

    def close(self):
        """Закрывает диалог и уведомляет родительский обработчик."""
        super().close()

