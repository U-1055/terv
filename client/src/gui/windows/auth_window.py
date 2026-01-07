from PySide6.QtWidgets import QStackedWidget, QDialog, QHBoxLayout

from client.src.gui.windows.windows import BaseWindow
from client.src.gui.widgets_view.auth_view import AuthView
from client.src.gui.widgets_view.register_view import RegisterView
from client.src.base import GuiLabels


class PopUpAuthWindow(QDialog):
    """Всплывающее окно регистрации/аутентификации."""
    auth_win_num = 0  # Номер окна в стековом виджете QStackLayout
    register_win_num = 1

    def __init__(self, normal_style: str, error_style: str, labels: GuiLabels = GuiLabels()):
        super().__init__()
        self._stacked_widget = QStackedWidget()
        main_layout = QHBoxLayout()
        register_window = RegisterView(normal_style, error_style, labels)
        auth_window = AuthView(normal_style, error_style, labels)

        self._stacked_widget.addWidget(auth_window)
        self._stacked_widget.addWidget(register_window)
        main_layout.addWidget(self._stacked_widget)

        self.setLayout(main_layout)
        self.choose_auth_window()

    def choose_auth_window(self):
        self._stacked_widget.setCurrentIndex(self.auth_win_num)

    def choose_register_window(self):
        self._stacked_widget.setCurrentIndex(self.register_win_num)

    def register_window(self) -> RegisterView:
        return self._stacked_widget.widget(self.register_win_num)

    def auth_window(self) -> AuthView:
        return self._stacked_widget.widget(self.auth_win_num)



