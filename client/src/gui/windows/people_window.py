"""Окно раздела "Люди" """
from PySide6.QtWidgets import QVBoxLayout

from client.src.gui.windows.windows import BaseWindow
from client.src.ui.ui_people_window import Ui_Form
from client.src.base import GuiLabels
from test.client_test.utils.window import setup_gui
from client.src.gui.sub_widgets.widgets import UserWidget


class PeopleWindow(BaseWindow):
    """Окно для поиска пользователей."""

    def __init__(self):
        super().__init__()
        self._view = Ui_Form()
        self._view.setupUi(self)
        self._users_layout = QVBoxLayout()
        self._view.scrollArea.setWidget(self._view.scrollAreaWidgetContents)
        self._view.scrollAreaWidgetContents.setLayout(self._users_layout)
        self._view.comboBox.addItem(GuiLabels.by_email)
        self._view.comboBox.addItem(GuiLabels.by_username)
        self._view.comboBox.setCurrentIndex(1)
        self._view.comboBox.setEditable(False)

    def searching_type(self) -> str:
        """
        Возвращает тип поиска - по email или по имени пользователя. GuiLabels.by_email и GuiLabels.by_username
        соответственно.
        """
        return self._view.comboBox.currentText()

    def add_user_widget(self, username: str, email: str) -> UserWidget:
        """Добавляет виджет пользователя."""
        user_widget = UserWidget(username, email)

        self._users_layout.addWidget(user_widget)
        return user_widget

    def clear(self):
        """Удаляет все виджеты пользователей."""
        for i in range(self._users_layout.count()):
            widget = self._users_layout.itemAt(i).widget()
            if type(widget) is UserWidget:
                widget.hide()


if __name__ == '__main__':
    from client.src.base import GUIStyles
    widget_ = PeopleWindow()
    widget_._view.lineEdit.setFont(GUIStyles.base_font)
    for i in range(15):
        widget_.add_user_widget(f'User#{i}', 'email')

    setup_gui(widget_)

