"""Обработчик окна рабочего пространства."""
from PySide6.QtCore import Signal

from client.src.src.handlers.window_handlers.base import BaseWindowHandler
from client.src.gui.windows.workspace_window import WorkspaceWindow, WorkspaceSettingsWindow
from client.src.requester.requester import Requester
from client.src.gui.main_view import MainWindow
from client.src.client_model.model import Model
import client.models.common_models as cm
from common.logger import config_logger, CLIENT
from client.src.base import LOG_DIR, MAX_FILE_SIZE, MAX_BACKUP_FILES, LOGGING_LEVEL
from client.src.gui.sub_widgets.widgets import ProjectWidget

logger = config_logger(__name__, CLIENT, LOG_DIR, MAX_FILE_SIZE, MAX_BACKUP_FILES, LOGGING_LEVEL)


class WorkspaceWindowHandler(BaseWindowHandler):
    """
    Обработчик окна рабочего пространства. Управляет логикой всех разделов пространства.
    
    Управляет отображением информации о рабочем пространстве, проектах, участниках, аналитикой.
    Обрабатывает права доступа на основе роли пользователя.
    
    :var workspace_data_received: Сигнал при получении данных о рабочем пространстве.
    :var projects_data_received: Сигнал при получении данных о проектах.
    :var participants_data_received: Сигнал при получении данных об участниках.
    :var tried_to_open_project: Сигнал при попытке открыть проект.
    """
    
    workspace_data_received = Signal(dict)
    projects_data_received = Signal(list)
    participants_data_received = Signal(list)
    tried_to_open_project = Signal(int, str, int)  # project_id, project_name, workspace_id

    # Роли и их ID
    ROLE_ADMINISTRATOR = 3
    ROLE_MENTOR = 1
    ROLE_STUDENT = 2
    ROLE_TEAM_LEAD = 4
    
    def __init__(self, window: WorkspaceWindow, main_view: MainWindow, requester: Requester, model: Model,
                 workspace_id: int, workspace_name: str):
        super().__init__(window, main_view, requester, model)
        
        self._window: WorkspaceWindow = window
        self._requester = requester
        self._model = model
        self._workspace_id = workspace_id
        
        # Данные о текущем пользователе и его роли
        self._user_role_id: int = 0
        self._user_role_name: str = ""
        self._user_id: int = 0
        
        # Данные о рабочем пространстве
        self._workspace_data: dict = {}
        self._projects: list[cm.Project] = []
        self._participants: list[dict] = []
        self._project_widgets: dict[int, ProjectWidget] = {}  # Виджеты проектов по ID
        self._roles: dict[int, str] = {
            self.ROLE_MENTOR: "Наставник",
            self.ROLE_STUDENT: "Студент",
            self.ROLE_ADMINISTRATOR: "Администратор",
            self.ROLE_TEAM_LEAD: "Тимлид"
        }
        
        # Обработчик окна настроек
        self._settings_handler: WorkspaceSettingsHandler | None = None
        
        # Подключение сигналов окна
        self._window.back_pressed.connect(self._on_back_pressed)
        self._window.settings_pressed.connect(self._on_settings_pressed)
        self._window.role_change_requested.connect(self._on_role_change_requested)
        self._window.project_open_requested.connect(self._on_project_open_requested)

    def _on_back_pressed(self):
        """Обработка нажатия кнопки возврата."""
        logger.info('Back pressed in workspace window')
        # Возвращаемся на предыдущее окно через MainView
        self._main_view.go_back()

    def _on_settings_pressed(self):
        """Обработка нажатия кнопки настроек."""
        if not self._settings_handler:
            self._open_settings_window()
    
    def _open_settings_window(self):
        """Открывает окно настроек рабочего пространства как полноценное окно."""
        name = self._workspace_data.get('name', '')
        description = self._workspace_data.get('description', '')
        
        # Открываем окно настроек через MainView как полноценное окно
        settings_window = self._main_view.open_workspace_settings_window(
            self._workspace_id, name, description,
            loading_time=10  # Время загрузки в миллисекундах
        )

        # Создаём обработчик окна настроек
        self._settings_handler = WorkspaceSettingsHandler(
            settings_window, self._main_view,
            self._requester, self._model, self
        )

        # Подключаем сигналы обработчика
        self._settings_handler.closed.connect(self._on_settings_closed)

    def _on_settings_closed(self):
        """Обработка закрытия окна настроек."""
        self._settings_handler = None
    
    def _on_settings_back_pressed(self):
        """Обработка возврата из настроек (через обработчик)."""
        if self._settings_handler:
            self._settings_handler.close()

    def _on_settings_save(self, name: str, description: str):
        """
        Обработка сохранения настроек.
        
        :param name: Новое название.
        :param description: Новое описание.
        """
        access_token = self._model.get_access_token()
        request = self._requester.update_workspace(self._workspace_id, name, description, access_token)
        request.finished.connect(lambda req: self._prepare_request(req, self._on_workspace_updated))
    
    def _on_workspace_updated(self, data: dict):
        """Обработка обновления рабочего пространства."""
        logger.info(f'Workspace updated: {data}')
        if not data:
            return
        self._workspace_data['name'] = data.get('name', self._workspace_data.get('name', ''))
        self._workspace_data['description'] = data.get('description', self._workspace_data.get('description', ''))
        self._window.set_workspace_info(self._workspace_data['name'], self._workspace_data['description'])
        self._settings_handler = None
    
    def _on_role_change_requested(self, user_id: int, new_role_id: int):
        """
        Обработка запроса смены роли участника.
        
        :param user_id: ID участника.
        :param new_role_id: Новая роль.
        """
        access_token = self._model.get_access_token()
        request = self._requester.set_user_role_in_workspace(
            self._workspace_id, user_id, new_role_id, access_token)
        request.finished.connect(lambda req: self._prepare_request(req, self._on_role_changed))
    
    def _on_project_open_requested(self, project_id: int, project_name: str):
        """
        Обработка запроса открытия проекта.

        :param project_id: ID проекта.
        :param project_name: Название проекта.
        """
        logger.info(f'Opening project: {project_name} (id={project_id})')
        self.tried_to_open_project.emit(project_id, project_name, self._workspace_id)

    def _on_role_changed(self, data: dict):
        """Обработка смены роли."""
        logger.info(f'Role changed: {data}')
        self.update_state()
    
    def _on_analytics_project_changed(self, index: int):
        """
        Обработка переключения проекта в аналитике.
        
        :param index: Индекс проекта.
        """
        if index == 0:  # "Общее"
            self._load_workspace_analytics()
        else:
            project_id = self._projects[index - 1].id if index - 1 < len(self._projects) else 0
            if project_id:
                self._load_project_analytics(project_id)
    
    def _load_workspace_analytics(self):
        """Загружает аналитику рабочего пространства."""
        access_token = self._model.get_access_token()
        request = self._requester.get_workspace_analytics(self._workspace_id, access_token)
        request.finished.connect(lambda req: self._prepare_request(req, self._on_workspace_analytics_received))
    
    def _load_project_analytics(self, project_id: int):
        """
        Загружает аналитику проекта.
        
        :param project_id: ID проекта.
        """
        access_token = self._model.get_access_token()
        request = self._requester.get_project_analytics(self._workspace_id, project_id, access_token)
        request.finished.connect(lambda req: self._prepare_request(req, self._on_project_analytics_received))
    
    def _on_workspace_analytics_received(self, data: dict):
        """Обработка получения аналитики рабочего пространства."""
        avg_tasks = data.get('avg_tasks_per_user', 0)
        self._window.set_avg_tasks_value(avg_tasks)
        logger.info(f'Workspace analytics received: avg_tasks={avg_tasks}')
    
    def _on_project_analytics_received(self, data: dict):
        """Обработка получения аналитики проекта."""
        avg_tasks = data.get('avg_tasks_per_user', 0)
        self._window.set_avg_tasks_value(avg_tasks)
        logger.info(f'Project analytics received: avg_tasks={avg_tasks}')
    
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
        # Логика ограничений будет реализована после получения данных с сервера
        pass
    
    def _on_projects_received(self, data: list):
        """
        Обработка получения проектов.
        
        :param data: Данные проектов (содержит 'content' со списком проектов).
        """
        if not data:
            return

        self._projects.clear()
        self._window.clear_project_widgets()
        
        # Инициализируем словарь для хранения участников проектов
        self._project_participants = {}

        project_names = []
        projects_content = data

        for project_data in projects_content:
            project = cm.Project(**project_data)
            self._projects.append(project)
            project_names.append(project.name)
            
            # Инициализируем хранилище участников для проекта
            self._project_participants[project.id] = {'students': [], 'mentors': []}

            # Запрос студентов проекта
            access_token = self._model.get_access_token()
            students_request = self._requester.get_project_students(
                self._workspace_id, project.id, access_token, limit=100, offset=0)
            students_request.finished.connect(
                lambda req, pid=project.id: self._prepare_request(
                    req, lambda d, p=pid: self._on_project_students_received(p, d)))

            # Запрос наставников проекта
            mentors_request = self._requester.get_project_mentors(
                self._workspace_id, project.id, access_token, limit=100, offset=0)
            mentors_request.finished.connect(
                lambda req, pid=project.id: self._prepare_request(
                    req, lambda d, p=pid: self._on_project_mentors_received(p, d)))

            # Добавление виджета проекта (временные данные до получения участников)
            widget = self._window.add_project_widget(
                name=project.name,
                mentor="Загрузка...",
                students=["Загрузка..."],
                stage="Этап: Загрузка",
                project_id=project.id
            )
            self._project_widgets[project.id] = widget

        self._window.set_project_combobox(project_names)

        self.projects_data_received.emit(self._projects)
        logger.info(f'Projects loaded: {len(self._projects)} projects')
    
    def _on_project_students_received(self, project_id: int, data: list):
        """
        Обработка получения студентов проекта.

        :param project_id: ID проекта.
        :param data: Данные студентов
        """
        if not data:
            return

        if project_id in self._project_participants:
            self._project_participants[project_id]['students'] = data
            self._update_project_widget(project_id)

    def _on_project_mentors_received(self, project_id: int, data: list):
        """
        Обработка получения наставников проекта.

        :param project_id: ID проекта.
        :param data: Данные наставников
        """
        if not data:
            return

        if project_id in self._project_participants:
            self._project_participants[project_id]['mentors'] = data
            self._update_project_widget(project_id)

    def _update_project_widget(self, project_id: int):
        """
        Обновляет виджет проекта с реальными данными участников.

        :param project_id: ID проекта.
        """
        if not hasattr(self, '_project_participants') or project_id not in self._project_participants:
            return

        participants = self._project_participants[project_id]
        students = participants.get('students', [])
        mentors = participants.get('mentors', [])

        # Формируем списки имен
        student_names = [s.get('username', s.get('email', 'Unknown')) for s in students]
        mentor_names = [m.get('username', m.get('email', 'Unknown')) for m in mentors]

        # Находим проект
        project = None
        for p in self._projects:
            if p.id == project_id:
                project = p
                break

        if not project:
            return

        # Обновляем виджет проекта
        stage = "Этап: Загрузка"  # Заглушка - будет реализована позже

        for id_ in self._project_widgets:
            if id_ == project_id:
                self._project_widgets[id_].update_info(
                    mentor=', '.join(mentor_names) if mentor_names else 'Нет наставников',
                    students=student_names,
                    stage=stage
                )
                break

    def _on_participants_received(self, data: list):
        """
        Обработка получения участников.
        
        :param data: Список участников.
        """
        self._participants.clear()
        self._window.clear_participant_widgets()
        
        for participant_data in data:
            user_id = participant_data.get('user_id', 0)
            username = participant_data.get('username', 'Unknown')
            email = participant_data.get('email', 'unknown@example.com')
            role_id = participant_data.get('role_id', 0)
            role_name = self._roles.get(role_id, 'Неизвестная роль')
            project_names = participant_data.get('project_names', [])
            
            # Проверка прав на изменение роли
            can_change_role = (self._user_role_id == self.ROLE_ADMINISTRATOR)
            
            widget = self._window.add_participant_widget(
                username=username,
                email=email,
                role_name=role_name,
                role_id=role_id,
                project_names=project_names,
                can_change_role=can_change_role
            )
            
            self._participants.append(participant_data)
        
        self.participants_data_received.emit(self._participants)
        logger.info(f'Participants loaded: {len(self._participants)} participants')
    
    def update_state(self):
        """
        Обновляет состояние обработчика.
        
        Загружает данные о рабочем пространстве, роли пользователя, проектах и участниках.
        """
        logger.info(f'Updating workspace window: workspace_id={self._workspace_id}')
        
        access_token = self._model.get_access_token()
        
        # Запрос роли пользователя
        role_request = self._requester.get_user_role_in_workspace(
            self._workspace_id, self._user_id, access_token)
        role_request.finished.connect(lambda req: self._prepare_request(req, self._on_user_role_received))
        
        # Запрос проектов
        projects_request = self._requester.get_workspace_projects(
            self._workspace_id, access_token, limit=100, offset=0)
        projects_request.finished.connect(lambda req: self._prepare_request(req, self._on_projects_received))
        
        # Запрос участников
        participants_request = self._requester.get_workspace_users(
            self._workspace_id, access_token, limit=100, offset=0)
        participants_request.finished.connect(lambda req: self._prepare_request(req, self._on_participants_received))
    
    def update_data(self):
        """Обновляет данные в обработчике."""
        self.update_state()
    
    def workspace_id(self) -> int:
        """Возвращает ID рабочего пространства."""
        return self._workspace_id
    
    def user_role_id(self) -> int:
        """Возвращает ID роли пользователя."""
        return self._user_role_id
    
    def user_role_name(self) -> str:
        """Возвращает название роли пользователя."""
        return self._user_role_name


class WorkspaceSettingsHandler(BaseWindowHandler):
    """
    Обработчик окна настроек рабочего пространства.
    
    :param parent_handler: Родительский обработчик (WorkspaceWindowHandler).
    """
    
    def __init__(self, window: WorkspaceSettingsWindow, main_view: MainWindow, 
                 requester: Requester, model: Model, parent_handler: WorkspaceWindowHandler):
        super().__init__(window, main_view, requester, model)
        
        self._window: WorkspaceSettingsWindow = window
        self._parent_handler = parent_handler
        
        # Подключение сигналов окна
        self._window.back_pressed.connect(self._on_btn_back_pressed)
        self._window.save_pressed.connect(self._on_btn_save_pressed)

    def _on_btn_back_pressed(self):
        """Обработка нажатия кнопки возврата."""
        # Возвращаемся на предыдущее окно (рабочее пространство) через MainView
        self._main_view.go_back()
        self.close()
    
    def _on_btn_save_pressed(self, name: str, description: str):
        """
        Обработка сохранения настроек.
        
        :param name: Новое название.
        :param description: Новое описание.
        """
        self._parent_handler._on_settings_save(name, description)

    def close(self):
        """Закрывает окно настроек и уведомляет родительский обработчик."""
        super().close()
        self._parent_handler._on_settings_closed()
