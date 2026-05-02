"""Окно раздела "Рабочие пространства" """
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import Signal

from client.src.gui.windows.windows import BaseWindow
from client.src.ui.ui_workspaces_list_window import Ui_WorkspacesListWindow
from client.src.base import GuiLabels
from client.src.gui.sub_widgets.widgets import WorkspaceWidget


class WorkspacesListWindow(BaseWindow):
    """
    Окно для отображения списка рабочих пространств пользователя.
    
    Содержит строку поиска и контейнер для виджетов рабочих пространств.
    """
    
    search_pressed = Signal(str)  # Сигнал при нажатии кнопки поиска. Передаёт поисковую строку.
    reset_pressed = Signal()  # Сигнал при нажатии кнопки сброса.
    workspace_clicked = Signal(int)  # Сигнал при клике на виджет рабочего пространства. Передаёт ID.
    
    def __init__(self):
        super().__init__()
        self._view = Ui_WorkspacesListWindow()
        self._view.setupUi(self)
        
        # Хранение созданных виджетов рабочих пространств
        self._workspace_widgets: list[WorkspaceWidget] = []
        
        # Подключение сигналов
        self._view.btn_search.clicked.connect(self._on_btn_search_pressed)
        self._view.btn_reset.clicked.connect(self._on_btn_reset_pressed)
        self._view.line_edit_search.returnPressed.connect(self._on_btn_search_pressed)
    
    def _on_btn_search_pressed(self):
        """Обработка нажатия кнопки поиска."""
        search_text = self._view.line_edit_search.text()
        self.search_pressed.emit(search_text)
        self._view.btn_reset.setEnabled(True)
    
    def _on_btn_reset_pressed(self):
        """Обработка нажатия кнопки сброса."""
        self._view.line_edit_search.clear()
        self.reset_pressed.emit()
        self._view.btn_reset.setEnabled(False)
    
    def add_workspace_widget(self, name: str, description: str, workspace_id: int) -> WorkspaceWidget:
        """
        Добавляет виджет рабочего пространства в список.
        
        :param name: Название рабочего пространства.
        :param description: Описание рабочего пространства.
        :param workspace_id: ID рабочего пространства.
        :return: Созданный виджет рабочего пространства.
        """
        widget = WorkspaceWidget(name, description, workspace_id)
        widget.clicked.connect(self.workspace_clicked.emit)
        
        self._view.workspaces_layout.addWidget(widget)
        self._workspace_widgets.append(widget)
        
        return widget
    
    def clear_widgets(self):
        """Удаляет все виджеты рабочих пространств из списка."""
        for widget in self._workspace_widgets:
            widget.hide()
            self._view.workspaces_layout.removeWidget(widget)
        
        self._workspace_widgets.clear()
    
    def filter_widgets(self, search_text: str):
        """
        Фильтрует виджеты по названию рабочего пространства.
        
        :param search_text: Строка поиска.
        """
        search_text_lower = search_text.lower()
        
        for widget in self._workspace_widgets:
            name = widget.name().lower()
            if search_text_lower in name:
                widget.show()
            else:
                widget.hide()
    
    def get_search_text(self) -> str:
        """Возвращает текущий текст поиска."""
        return self._view.line_edit_search.text()
    
    def set_search_text(self, text: str):
        """Устанавливает текст поиска."""
        self._view.line_edit_search.setText(text)
    
    def clear_search(self):
        """Очищает строку поиска."""
        self._view.line_edit_search.clear()
    
    def set_reset_button_enabled(self, enabled: bool):
        """Устанавливает состояние кнопки сброса."""
        self._view.btn_reset.setEnabled(enabled)
