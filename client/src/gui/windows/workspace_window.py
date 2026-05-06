"""Окно раздела конкретного рабочего пространства."""
from PySide6.QtWidgets import QVBoxLayout, QComboBox, QPushButton, QHBoxLayout, QLabel, QWidget, QSizePolicy
from PySide6.QtCore import Signal, QSize, Qt

from client.src.gui.windows.windows import BaseWindow
from client.src.ui.ui_workspace_window import Ui_WorkspaceWindow
from client.src.base import GuiLabels
from client.src.gui.sub_widgets.widgets import WorkspaceWidget, ProjectWidget
from client.src.gui.windows.workspace_settings_window import WorkspaceSettingsWindow


class WorkspaceWindow(BaseWindow):
    """
    Окно для отображения информации о рабочем пространстве.

    :var back_pressed: Сигнал, испускаемый при нажатии кнопки возврата.
    :var settings_pressed: Сигнал, испускаемый при нажатии кнопки настроек.
    :var project_clicked: Сигнал, испускаемый при клике на проект.
    :var project_open_requested: Сигнал, испускаемый при запросе открытия проекта.
    :var role_change_requested: Сигнал, испускаемый при запросе смены роли (workspace_id, user_id, role_
    """
    
    back_pressed = Signal()  # Сигнал при нажатии кнопки возврата
    settings_pressed = Signal()  # Сигнал при нажатии кнопки настроек
    project_clicked = Signal(int)  # Сигнал при клике на проект
    project_open_requested = Signal(int, str)  # Сигнал при запросе открытия проекта (project_id, project_name)
    role_change_requested = Signal(int, int, int)  # Сигнал при запросе смены роли (workspace_id, user_id, role_id)
    analytics_project_changed = Signal(int)  # Сигнал при смене проекта в аналитике

    def __init__(self, workspace_id: int, workspace_name: str):
        super().__init__()
        self._workspace_id = workspace_id
        self._workspace_name = workspace_name
        
        self._view = Ui_WorkspaceWindow()
        self._view.setupUi(self)
        
        # Подключение сигналов
        self._view.btn_back.clicked.connect(self._on_btn_back_pressed)
        self._view.btn_settings_info.clicked.connect(self._on_btn_settings_pressed)
        self._view.combobox_analytics_project.currentIndexChanged.connect(self._on_analytics_project_changed)
        self._view.btn_settings_info.setDisabled(True)  # Отключаем кнопку настроек для демки

        # Применение стилей к элементам аналитики
        from PySide6.QtGui import QFont

        # Увеличиваем шрифт label "Задач на участника в среднем:" и делаем его жирным
        avg_tasks_lbl_font = QFont("Calibri", 14, 75, False)  # 14pt, Bold (75)
        self._view.avg_tasks_lbl.setFont(avg_tasks_lbl_font)

        # Устанавливаем шрифт для значения (уже установлен как 24pt в UI)
        avg_tasks_value_lbl_font = QFont("Calibri", 28, 75, False)  # 28pt, Bold
        self._view.avg_tasks_value_lbl.setFont(avg_tasks_value_lbl_font)

        # Хранение созданных виджетов
        self._project_widgets: list[ProjectWidget] = []
        self._participant_widgets: list[ParticipantWidget] = []
        
        # Виджеты для этапов (добавляются динамически)
        self._stage_widgets: dict[str, tuple[QLabel, QComboBox]] = {}
        self._stage_layout = QVBoxLayout()
        self._view.analytics_layout.addLayout(self._stage_layout)

        # Индексы вкладок
        self._idx_projects = 0
        self._idx_analytics = 1
        self._idx_info = 2
        self._idx_participants = 3
        
    def _on_btn_back_pressed(self):
        """Обработка нажатия кнопки возврата."""
        self.back_pressed.emit()
    
    def _on_btn_settings_pressed(self):
        """Обработка нажатия кнопки настроек."""
        self.settings_pressed.emit()
    
    def _on_analytics_project_changed(self, index: int):
        """Обработка переключения проекта в аналитике."""
        # Индекс 0 - "Общее", остальные - проекты
        self.analytics_project_changed.emit(index)

    # Методы для вкладки "Проекты"
    def add_project_widget(self, name: str, mentor: str, students: list[str], 
                           stage: str = "Заглушка", project_id: int = 0) -> ProjectWidget:
        """
        Добавляет виджет проекта.
        
        :param name: Название проекта.
        :param mentor: Имя наставника.
        :param students: Список имен студентов.
        :param stage: Этап проекта.
        :param project_id: ID проекта.
        :return: Созданный виджет проекта.
        """
        widget = ProjectWidget(name, mentor, students, stage, project_id)
        widget.open_pressed.connect(lambda pid=project_id, pname=name: self.project_open_requested.emit(pid, pname))

        self._view.projects_container_layout.addWidget(widget)
        self._project_widgets.append(widget)
        
        return widget
    
    def clear_project_widgets(self):
        """Удаляет все виджеты проектов."""
        for widget in self._project_widgets:
            widget.hide()
            self._view.projects_container_layout.removeWidget(widget)
        
        self._project_widgets.clear()
    
    def set_project_combobox(self, project_names: list[str]):
        """
        Устанавливает список проектов в комбобоксе аналитики.
        
        :param project_names: Список названий проектов.
        """
        self._view.combobox_analytics_project.clear()
        self._view.combobox_analytics_project.addItem("Общее")
        for name in project_names:
            self._view.combobox_analytics_project.addItem(name)
        self._view.combobox_analytics_project.setCurrentIndex(0)

    # Методы для вкладки "Аналитика"
    def set_avg_tasks_value(self, value: float):
        """Устанавливает значение среднего числа задач на участника."""
        self._view.avg_tasks_value_lbl.setText(str(round(value, 2)))
        # Делаем значение жирным
        self._view.avg_tasks_value_lbl.setStyleSheet("font-weight: bold;")

    def clear_stage_distribution(self):
        """Очищает виджеты распределения по этапам."""
        while self._stage_layout.count():
            item = self._stage_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
        self._stage_widgets.clear()
        # Удаляем отступ снизу, если он был добавлен
        spacer_items = [i for i in range(self._stage_layout.count())
                        if self._stage_layout.itemAt(i).spacerItem()]
        for i in reversed(spacer_items):
            self._stage_layout.removeItem(self._stage_layout.itemAt(i))

    def add_stage_distribution_spacer(self):
        """Добавляет отступ снизу после строк этапов."""
        self._stage_layout.addSpacing(30)  # Отступ 30 пикселей снизу

    def add_stage_row(self, stage_name: str, count: int, project_names: list[str]):
        """
        Добавляет строку этапа в аналитику.
        :param stage_name: Название этапа (жирным).
        :param count: Число проектов.
        :param project_names: Список названий проектов для QComboBox.
        """
        from PySide6.QtWidgets import QSizePolicy

        row = QHBoxLayout()

        lbl_name = QLabel(f"<b>{stage_name}</b>: {count} проектов")
        lbl_name.setTextFormat(Qt.TextFormat.RichText)
        lbl_name.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)

        combo = QComboBox()
        combo.setEnabled(False)  # нередактируемый
        combo.addItems(project_names if project_names else ["Нет проектов"])

        # Настраиваем комбобокс для растягивания
        combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        combo.setMinimumWidth(200)  # Минимальная ширина для отображения текста

        row.addWidget(lbl_name, 0)  # Label не растягивается
        row.addWidget(combo, 1)     # Комбобокс растягивается
        row.addStretch(1)

        self._stage_layout.addLayout(row)
        self._stage_widgets[stage_name] = (lbl_name, combo)

    def update_stage_row_project_names(self, stage_name: str, project_names: list[str]):
        """
        Обновляет список проектов для строки этапа.
        :param stage_name: Название этапа.
        :param project_names: Новый список названий проектов.
        """
        from PySide6.QtWidgets import QSizePolicy

        if stage_name in self._stage_widgets:
            lbl_name, combo = self._stage_widgets[stage_name]
            # Обновляем комбобокс
            combo.clear()
            combo.addItems(project_names if project_names else ["Нет проектов"])
            # Обновляем label с количеством
            count = len(project_names) if project_names else 0
            lbl_name.setText(f"<b>{stage_name}</b>: {count} проектов")

            # Убедимся, что настройки размера сохранены
            combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            combo.setMinimumWidth(200)
            combo.setEnabled(True)
            combo.setEditable(False)

    def set_tasks_distribution_chart(self, chart_view):
        """Устанавливает виджет диаграммы распределения задач."""
        layout = self._view.tasks_distribution_layout

        # Удаляем предыдущий chart_view, если он есть
        if hasattr(self, '_chart_view') and self._chart_view:
            old_chart = self._chart_view
            layout.removeWidget(old_chart)
            old_chart.hide()
            old_chart.setParent(None)
            old_chart.deleteLater()
            self._chart_view = None

        # Удаляем QLabel-заглушку при первом вызове
        old_lbl = getattr(self._view, 'tasks_distribution_chart_lbl', None)
        if old_lbl:
            layout.removeWidget(old_lbl)
            old_lbl.hide()
            old_lbl.setParent(None)
            old_lbl.deleteLater()
            self._view.tasks_distribution_chart_lbl = None

        self._chart_view = chart_view
        chart_view.setMinimumSize(400, 300)
        layout.addWidget(chart_view)

    # Методы для вкладки "Инфо"
    def set_workspace_info(self, name: str, description: str):
        """
        Устанавливает информацию о рабочем пространстве.
        
        :param name: Название.
        :param description: Описание.
        """
        self._view.lbl_workspace_name_info.setText('Инженерная смена будущего')
        self._view.lbl_workspace_description_info.setText('РЦ "Альтаир"')
    
    # Методы для вкладки "Участники"
    def add_participant_widget(self, username: str, email: str, role_name: str,
                               role_id: int, project_names: list[str],
                               can_change_role: bool = False) -> 'ParticipantWidget':
        """
        Добавляет виджет участника.
        
        :param username: Имя пользователя.
        :param email: Email.
        :param role_name: Название роли.
        :param role_id: ID роли.
        :param project_names: Список проектов участника.
        :param can_change_role: Можно ли менять роль.
        :return: Созданный виджет участника.
        """
        widget = ParticipantWidget(username, email, role_name, role_id, 
                                   project_names, can_change_role)
        widget.role_change_requested.connect(self.role_change_requested.emit)
        
        self._view.participants_container_layout.addWidget(widget)
        self._participant_widgets.append(widget)
        
        return widget
    
    def clear_participant_widgets(self):
        """Удаляет все виджеты участников."""
        for widget in self._participant_widgets:
            widget.hide()
            self._view.participants_container_layout.removeWidget(widget)
        
        self._participant_widgets.clear()
    
    # Общие методы
    def workspace_id(self) -> int:
        """Возвращает ID рабочего пространства."""
        return self._workspace_id
    
    def get_analytics_project_index(self) -> int:
        """Возвращает текущий индекс проекта в аналитике."""
        return self._view.combobox_analytics_project.currentIndex()


class ParticipantWidget(QWidget):
    """
    Виджет участника рабочего пространства.
    
    :param username: Имя пользователя.
    :param email: Email.
    :param role_name: Название роли.
    :param role_id: ID роли.
    :param project_names: Список проектов участника.
    :param can_change_role: Можно ли менять роль.
    """
    
    role_change_requested = Signal(int, int, int)  # workspace_id, user_id, role_id
    
    def __init__(self, username: str, email: str, role_name: str, role_id: int,
                 project_names: list[str], can_change_role: bool = False):
        super().__init__()
        self._username = username
        self._email = email
        self._role_name = role_name
        self._role_id = role_id
        self._project_names = project_names
        self._can_change_role = can_change_role
        
        self._main_layout = QVBoxLayout()
        self._main_layout.setContentsMargins(10, 5, 10, 5)
        
        # Верхняя строка с именем и ролью
        self.top_layout = QHBoxLayout()
        
        self.lbl_username = QLabel(f"{username} ({email})")
        self.top_layout.addWidget(self.lbl_username)
        
        self.top_layout.addStretch(1)
        
        if can_change_role:
            self.combobox_role = QComboBox()
            self.combobox_role.addItem("Наставник", 1)
            self.combobox_role.addItem("Студент", 2)
            self.combobox_role.addItem("Администратор", 3)
            self.combobox_role.addItem("Тимлид", 4)
            self.combobox_role.setCurrentText(role_name)
            self.combobox_role.setEnabled(True)
            
            self.btn_confirm = QPushButton("OK")
            self.btn_confirm.setMaximumSize(QSize(50, 25))
            self.btn_confirm.clicked.connect(self._on_role_change_confirmed)
            
            self.btn_cancel = QPushButton("X")
            self.btn_cancel.setMaximumSize(QSize(30, 25))
            self.btn_cancel.clicked.connect(self._on_role_change_cancelled)
            
            self.top_layout.addWidget(self.combobox_role)
            self.top_layout.addWidget(self.btn_confirm)
            self.top_layout.addWidget(self.btn_cancel)
        else:
            self.lbl_role = QLabel(f"Роль: {role_name}")
            self.top_layout.addWidget(self.lbl_role)
        
        self._main_layout.addLayout(self.top_layout)
        
        # Строка с проектами
        self.projects_layout = QHBoxLayout()
        self.lbl_projects = QLabel(f"")
        self.projects_layout.addWidget(self.lbl_projects)
        self.projects_layout.addStretch(1)
        self._main_layout.addLayout(self.projects_layout)
        
        self.setLayout(self._main_layout)
    
    def _on_role_change_confirmed(self):
        """Обработка подтверждения смены роли."""
        new_role_id = self.combobox_role.currentData()
        self.role_change_requested.emit(0, 0, new_role_id)  # ID будут установлены в обработчике
    
    def _on_role_change_cancelled(self):
        """Обработка отмены смены роли."""
        self.combobox_role.setCurrentText(self._role_name)
