from PySide6.QtCore import Signal

from client.src.gui.windows.windows import BaseWindow
from client.src.ui.ui_workspace_settings_window import Ui_WorkspaceSettingsWindow


class WorkspaceSettingsWindow(BaseWindow):
    """
    Окно настроек рабочего пространства.

    Позволяет редактировать название и описание.
    """

    back_pressed = Signal()  # Сигнал при нажатии кнопки возврата
    save_pressed = Signal(str, str)  # Сигнал при сохранении (name, description)

    def __init__(self, workspace_id: int, name: str, description: str):
        super().__init__()
        self._workspace_id = workspace_id
        self._original_name = name
        self._original_description = description

        self._view = Ui_WorkspaceSettingsWindow()
        self._view.setupUi(self)

        # Установка текущих значений
        self._view.text_edit_name.setText(name)
        self._view.text_edit_description.setText(description if description else "")

        # Подключение сигналов
        self._view.btn_back.clicked.connect(self._on_btn_back_pressed)
        self._view.btn_confirm.clicked.connect(self._on_btn_confirm_pressed)
        self._view.btn_cancel.clicked.connect(self._on_btn_cancel_pressed)

        # Отслеживание изменений
        self._view.text_edit_name.textChanged.connect(self._on_text_changed)
        self._view.text_edit_description.textChanged.connect(self._on_text_changed)

    def _on_btn_back_pressed(self):
        """Обработка нажатия кнопки возврата."""
        self.back_pressed.emit()

    def _on_btn_confirm_pressed(self):
        """Обработка нажатия кнопки подтверждения."""
        name = self._view.text_edit_name.toPlainText()
        description = self._view.text_edit_description.toPlainText()
        self.save_pressed.emit(name, description)

    def _on_btn_cancel_pressed(self):
        """Обработка нажатия кнопки отмены."""
        self._view.text_edit_name.setText(self._original_name)
        self._view.text_edit_description.setText(self._original_description)
        self._update_confirm_button()

    def _on_text_changed(self):
        """Обработка изменения текста."""
        self._update_confirm_button()

    def _update_confirm_button(self):
        """Обновляет состояние кнопки подтверждения."""
        name = self._view.text_edit_name.toPlainText()
        description = self._view.text_edit_description.toPlainText()

        has_changes = (name != self._original_name or
                       description != self._original_description)
        self._view.btn_confirm.setEnabled(has_changes)

    def workspace_id(self) -> int:
        """Возвращает ID рабочего пространства."""
        return self._workspace_id
