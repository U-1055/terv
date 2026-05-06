"""Окно раздела конкретного проекта."""
from PySide6.QtWidgets import (QVBoxLayout, QComboBox, QTextEdit, QDialog, QPushButton,
                               QHBoxLayout, QLabel, QWidget, QScrollArea, QMessageBox)
from PySide6.QtCore import Signal, QSize
from PySide6.QtGui import QFont

from client.src.gui.windows.windows import BaseWindow
from client.src.ui.ui_project_window import Ui_ProjectWindow
from client.src.base import GuiLabels
from client.src.gui.sub_widgets.task_card_widget import TaskCardWidget
from client.src.gui.sub_widgets.stage_widget import StageWidget
from client.src.gui.windows.task_dialog_window import TaskDialogWindow


class ProjectWindow(BaseWindow):
    """
    Окно для отображения информации о проекте.
    
    Содержит 4 вкладки: "Инфо", "План", "Задачи", "Участники".
    """
    
    back_pressed = Signal()  # Сигнал при нажатии кнопки возврата
    create_task_pressed = Signal()  # Сигнал при нажатии кнопки создания задачи
    task_edit_requested = Signal(int)  # Сигнал при запросе редактирования задачи
    task_view_requested = Signal(int)  # Сигнал при запросе просмотра задачи (read-only)
    task_status_changed = Signal(int, int)  # Сигнал при смене статуса задачи (task_id, new_status_id)
    
    # Сигналы сохранения/отмены для каждого поля
    goal_save_pressed = Signal(str)  # Передает текст цели
    goal_cancel_pressed = Signal()
    tasks_save_pressed = Signal(str)  # Передает текст задач
    tasks_cancel_pressed = Signal()
    relevance_save_pressed = Signal(str)  # Передает текст актуальности
    relevance_cancel_pressed = Signal()
    problem_save_pressed = Signal(str)  # Передает текст проблемы
    problem_cancel_pressed = Signal()
    thesis_save_pressed = Signal(str)  # Передает текст тезисов
    thesis_cancel_pressed = Signal()

    save_all_pressed = Signal()  # Нажата кнопка "Сохранить все"

    # Сигналы для работы с этапами
    request_stage_transition_pressed = Signal()
    confirm_stage_transition_pressed = Signal()
    reject_stage_transition_pressed = Signal()

    def __init__(self, project_id: int, project_name: str, workspace_id: int):
        super().__init__()
        self._project_id = project_id
        self._project_name = project_name
        self._workspace_id = workspace_id
        
        self._view = Ui_ProjectWindow()
        self._view.setupUi(self)
        
        # Подключение сигналов
        self._view.btn_back.clicked.connect(self._on_btn_back_pressed)
        self._view.btn_create_task.clicked.connect(self._on_btn_create_task_pressed)
        
        # Создание кнопок для полей инфо
        self._setup_info_buttons()

        # Хранение созданных виджетов задач
        self._task_cards: dict[int, TaskCardWidget] = {}
        
        # Хранение созданных виджетов участников
        self._participant_widgets: list[ProjectParticipantWidget] = []

        # Хранение созданных виджетов этапов
        self._stage_widgets: list[StageWidget] = []

        # Индексы вкладок
        self._idx_info = 0
        self._idx_plan = 1
        self._idx_tasks = 2
        self._idx_participants = 3

        # Состояние перехода этапов
        self._transition_requested = False

        # Настройка вкладки План
        self._setup_plan_tab()

    def _setup_info_buttons(self):
        """Подключает сигналы к кнопкам Сохранить/Отмена и Сохранить все из UI."""
        # Сохранить все
        self._view.btn_save_all.clicked.connect(self._on_save_all_pressed)

        # Цель
        self._view.btn_goal_save.clicked.connect(self._on_goal_save)
        self._view.btn_goal_cancel.clicked.connect(self._on_goal_cancel)

        # Задачи
        self._view.btn_tasks_save.clicked.connect(self._on_tasks_save)
        self._view.btn_tasks_cancel.clicked.connect(self._on_tasks_cancel)

        # Актуальность
        self._view.btn_relevance_save.clicked.connect(self._on_relevance_save)
        self._view.btn_relevance_cancel.clicked.connect(self._on_relevance_cancel)

        # Проблема
        self._view.btn_problem_save.clicked.connect(self._on_problem_save)
        self._view.btn_problem_cancel.clicked.connect(self._on_problem_cancel)

        # Тезисы
        self._view.btn_thesis_save.clicked.connect(self._on_thesis_save)
        self._view.btn_thesis_cancel.clicked.connect(self._on_thesis_cancel)

    def _on_goal_save(self):
        self.goal_save_pressed.emit(self._view.text_edit_goal.toPlainText())

    def _on_goal_cancel(self):
        self.goal_cancel_pressed.emit()

    def _on_tasks_save(self):
        self.tasks_save_pressed.emit(self._view.text_edit_tasks.toPlainText())

    def _on_tasks_cancel(self):
        self.tasks_cancel_pressed.emit()

    def _on_relevance_save(self):
        self.relevance_save_pressed.emit(self._view.text_edit_relevance.toPlainText())

    def _on_relevance_cancel(self):
        self.relevance_cancel_pressed.emit()

    def _on_problem_save(self):
        self.problem_save_pressed.emit(self._view.text_edit_problem.toPlainText())

    def _on_problem_cancel(self):
        self.problem_cancel_pressed.emit()

    def _on_thesis_save(self):
        self.thesis_save_pressed.emit(self._view.text_edit_theses.toPlainText())

    def _on_thesis_cancel(self):
        self.thesis_cancel_pressed.emit()

    def _on_save_all_pressed(self):
        self.save_all_pressed.emit()

    def _on_btn_back_pressed(self):
        """Обработка нажатия кнопки возврата."""
        self.back_pressed.emit()
    
    def _on_btn_create_task_pressed(self):
        """Обработка нажатия кнопки создания задачи."""
        self.create_task_pressed.emit()
    
    # Методы для вкладки "Инфо"
    def set_project_info(self, goal: str, tasks: str, problem: str, 
                         relevance: str, theses: str):
        """
        Устанавливает информацию о проекте.
        
        :param goal: Цель.
        :param tasks: Задачи проекта.
        :param problem: Проблема.
        :param relevance: Актуальность.
        :param theses: Основные тезисы.
        """
        self._view.text_edit_goal.setText(goal if goal else "")
        self._view.text_edit_tasks.setText(tasks if tasks else "")
        self._view.text_edit_problem.setText(problem if problem else "")
        self._view.text_edit_relevance.setText(relevance if relevance else "")
        self._view.text_edit_theses.setText(theses if theses else "")
    
    def get_project_info(self) -> dict:
        """
        Получает информацию о проекте из полей.
        
        :return: Словарь с информацией о проекте.
        """
        return {
            'goal': self._view.text_edit_goal.toPlainText(),
            'tasks': self._view.text_edit_tasks.toPlainText(),
            'problem': self._view.text_edit_problem.toPlainText(),
            'relevance': self._view.text_edit_relevance.toPlainText(),
            'theses': self._view.text_edit_theses.toPlainText()
        }

    def add_task_card(self, task_id: int, name: str, description: str,
                      creator_email: str, executor_email: str,
                      plan_start: str, plan_deadline: str,
                      status_id: int, column_index: int = 0) -> TaskCardWidget:
        """
        Добавляет карточку задачи в соответствующую колонку.

        :param task_id: ID задачи.
        :param name: Название задачи.
        :param description: Описание задачи.
        :param creator_email: Email пользователя, поручившего задачу.
        :param executor_email: Email исполнителя.
        :param plan_start: Плановая дата взятия в работу.
        :param plan_deadline: Планируемый дедлайн.
        :param status_id: ID статуса задачи.
        :param column_index: Индекс колонки (0 - Запланировано, 1 - В работе, 2 - Проверяется, 3 - Выполнено, 4 - Доработать).
        :return: Созданный виджет карточки задачи.
        """
        widget = TaskCardWidget(task_id, name, description, creator_email,
                                 executor_email, plan_start, plan_deadline, status_id)
        widget.edit_pressed.connect(lambda tid=task_id: self.task_edit_requested.emit(tid))
        widget.view_pressed.connect(lambda tid=task_id: self.task_view_requested.emit(tid))
        # Стрелка влево: предыдущий статус (минимум 1)
        widget.move_left_pressed.connect(lambda tid=task_id: self.task_status_changed.emit(tid, max(1, status_id - 1)))
        # Стрелка вправо: следующий статус с циклическим переходом 5 -> 1
        next_status = 1 if status_id >= 5 else status_id + 1
        widget.move_right_pressed.connect(lambda tid=task_id: self.task_status_changed.emit(tid, next_status))

        # Добавление в соответствующую колонку
        columns = [
            self._view.scroll_planned_contents,
            self._view.scroll_in_progress_contents,
            self._view.scroll_review_contents,
            self._view.scroll_done_contents,
            self._view.scroll_improve_contents
        ]
        
        if 0 <= column_index < len(columns):
            layout = columns[column_index].layout()
            if layout:
                layout.addWidget(widget)
        
        self._task_cards[task_id] = widget
        
        return widget
    
    def clear_task_cards(self):
        """Удаляет все карточки задач из layout и памяти."""
        for widget in self._task_cards.values():
            widget.setParent(None)
            widget.deleteLater()

        self._task_cards.clear()
    
    def get_task_card(self, task_id: int) -> TaskCardWidget | None:
        """Возвращает карточку задачи по ID."""
        return self._task_cards.get(task_id)
    
    # Общие методы
    def project_id(self) -> int:
        """Возвращает ID проекта."""
        return self._project_id
    
    def workspace_id(self) -> int:
        """Возвращает ID рабочего пространства."""
        return self._workspace_id
    
    def set_editable(self, editable: bool):
        """
        Устанавливает возможность редактирования полей.
        
        :param editable: Можно ли редактировать.
        """
        self._view.text_edit_goal.setReadOnly(not editable)
        self._view.text_edit_tasks.setReadOnly(not editable)
        self._view.text_edit_problem.setReadOnly(not editable)
        self._view.text_edit_relevance.setReadOnly(not editable)
        self._view.text_edit_theses.setReadOnly(not editable)

    # Методы для вкладки "Участники"
    def add_participant_widget(self, username: str, email: str, role_name: str,
                               can_edit: bool = False) -> 'ProjectParticipantWidget':
        """
        Добавляет виджет участника проекта.

        :param username: Имя пользователя.
        :param email: Email.
        :param role_name: Название роли.
        :param can_edit: Можно ли редактировать информацию.
        :return: Созданный виджет участника.
        """
        widget = ProjectParticipantWidget(username, email, role_name, can_edit)

        self._view.scroll_participants_contents_layout.addWidget(widget)
        self._participant_widgets.append(widget)

        return widget

    def clear_participant_widgets(self):
        """Удаляет все виджеты участников."""
        for widget in self._participant_widgets:
            widget.hide()
            self._view.scroll_participants_contents_layout.removeWidget(widget)

        self._participant_widgets.clear()

    # Методы для вкладки "План"
    def _setup_plan_tab(self):
        """Настройка вкладки 'План' с этапами проекта."""
        # Очистка старого контента
        while self._view.plan_layout.count():
            item = self._view.plan_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Верхняя панель с кнопками
        top_panel = QWidget()
        top_panel_layout = QHBoxLayout(top_panel)
        top_panel_layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_stages_title = QLabel("Этапы проекта:")
        self.lbl_stages_title.setFont(QFont("Calibri", 14, QFont.Weight.Bold))
        top_panel_layout.addWidget(self.lbl_stages_title)

        top_panel_layout.addStretch()

        self.btn_request_transition = QPushButton("Запросить переход на следующий этап")
        self.btn_request_transition.setFixedHeight(35)
        self.btn_request_transition.clicked.connect(self._on_request_transition)
        top_panel_layout.addWidget(self.btn_request_transition)

        self.btn_confirm_transition = QPushButton("Подтвердить переход")
        self.btn_confirm_transition.setFixedHeight(35)
        self.btn_confirm_transition.setVisible(False)
        self.btn_confirm_transition.clicked.connect(self._on_confirm_transition)
        top_panel_layout.addWidget(self.btn_confirm_transition)

        self.btn_reject_transition = QPushButton("Отклонить переход")
        self.btn_reject_transition.setFixedHeight(35)
        self.btn_reject_transition.setVisible(False)
        self.btn_reject_transition.clicked.connect(self._on_reject_transition)
        top_panel_layout.addWidget(self.btn_reject_transition)

        self._view.plan_layout.addWidget(top_panel)

        # Область для виджетов этапов
        self.scroll_stages = QScrollArea()
        self.scroll_stages.setWidgetResizable(True)
        self.scroll_stages_content = QWidget()
        self.scroll_stages_layout = QVBoxLayout(self.scroll_stages_content)
        self.scroll_stages_layout.setContentsMargins(0, 10, 0, 0)
        self.scroll_stages_layout.addStretch()
        self.scroll_stages.setWidget(self.scroll_stages_content)

        self._view.plan_layout.addWidget(self.scroll_stages)

    def _on_request_transition(self):
        """Обработка запроса на переход к следующему этапу."""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы действительно хотите перейти на следующий этап?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._transition_requested = True
            self.btn_request_transition.setVisible(False)
            self.btn_confirm_transition.setVisible(True)
            self.btn_reject_transition.setVisible(True)
            self.request_stage_transition_pressed.emit()

    def _on_confirm_transition(self):
        """Обработка подтверждения перехода к следующему этапу."""
        reply = QMessageBox.question(
            self,
            "Подтверждение перехода",
            "Подтвердить переход на следующий этап?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.confirm_stage_transition_pressed.emit()

    def _on_reject_transition(self):
        """Обработка отклонения перехода к следующему этапу."""
        self._transition_requested = False
        self.btn_request_transition.setVisible(True)
        self.btn_confirm_transition.setVisible(False)
        self.btn_reject_transition.setVisible(False)
        self.reject_stage_transition_pressed.emit()

    def clear_stage_widgets(self):
        """Очищает все виджеты этапов."""
        for widget in self._stage_widgets:
            widget.hide()
            self.scroll_stages_layout.removeWidget(widget)
            widget.deleteLater()
        self._stage_widgets.clear()

    def add_stage_widget(self, name: str, description: str, date_start: str,
                         date_end: str, result: str, status: str, stage_id: int = 0) -> StageWidget:
        """
        Добавляет виджет этапа.

        :param name: Название этапа.
        :param description: Полное описание этапа.
        :param date_start: Дата начала.
        :param date_end: Дата окончания.
        :param result: Планируемый результат.
        :param status: Статус этапа.
        :param stage_id: ID этапа.
        :return: Созданный виджет этапа.
        """
        widget = StageWidget(name, description, date_start, date_end, result, status, stage_id)
        self.scroll_stages_layout.insertWidget(
            self.scroll_stages_layout.count() - 1,  # Перед растягивающимся элементом
            widget
        )
        self._stage_widgets.append(widget)
        return widget

    def reset_transition_buttons(self):
        """Сбрасывает кнопки перехода к исходному состоянию."""
        self._transition_requested = False
        self.btn_request_transition.setVisible(True)
        self.btn_confirm_transition.setVisible(False)
        self.btn_reject_transition.setVisible(False)


class ProjectParticipantWidget(QWidget):
    """
    Виджет участника проекта.

    :param username: Имя пользователя.
    :param email: Email.
    :param role_name: Название роли.
    :param can_edit: Можно ли редактировать информацию.
    """

    def __init__(self, username: str, email: str, role_name: str, can_edit: bool = False):
        super().__init__()
        self._username = username
        self._email = email
        self._role_name = role_name
        self._can_edit = can_edit

        self._main_layout = QVBoxLayout()
        self._main_layout.setContentsMargins(10, 5, 10, 5)

        # Верхняя строка с именем и ролью
        self.top_layout = QHBoxLayout()

        self.lbl_username = QLabel(f"{username} ({email})")
        self.top_layout.addWidget(self.lbl_username)

        self.top_layout.addStretch(1)

        self.lbl_role = QLabel(f"Роль: {role_name}")
        self.top_layout.addWidget(self.lbl_role)

        self._main_layout.addLayout(self.top_layout)

        self.setLayout(self._main_layout)

