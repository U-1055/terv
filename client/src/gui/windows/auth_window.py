from PySide6.QtWidgets import QStackedWidget, QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal

from client.src.gui.windows.windows import BaseWindow
from client.src.gui.widgets_view.auth_view import AuthView
from client.src.gui.widgets_view.register_view import RegisterView
from client.src.base import GuiLabels, ObjectNames


class PopUpAuthWindow(QDialog):
    """Всплывающее окно регистрации/аутентификации."""

    btn_exit_pressed = Signal()
    auth_win_num = 0  # Номер окна в стековом виджете QStackLayout
    register_win_num = 1

    def __init__(self, normal_style: str, error_style: str, labels: GuiLabels = GuiLabels(), title: str = GuiLabels.registration_window):
        super().__init__()
        self._stacked_widget = QStackedWidget()
        main_layout = QVBoxLayout()
        register_window = RegisterView(normal_style, error_style, labels)
        auth_window = AuthView(normal_style, error_style, labels)
        lbl = QLabel(title)
        lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        btn_exit = QPushButton(GuiLabels.exit)
        btn_exit.setObjectName(ObjectNames.btn_exit)
        btn_exit.clicked.connect(self.press_btn_exit)

        self._stacked_widget.addWidget(auth_window)
        self._stacked_widget.addWidget(register_window)
        main_layout.addWidget(lbl)
        main_layout.addWidget(self._stacked_widget)
        main_layout.addWidget(btn_exit, alignment=Qt.AlignmentFlag.AlignLeft)

        self.setLayout(main_layout)
        self.choose_auth_window()

    def press_btn_exit(self):
        self.btn_exit_pressed.emit()

    def choose_auth_window(self):
        self._stacked_widget.setCurrentIndex(self.auth_win_num)

    def choose_register_window(self):
        self._stacked_widget.setCurrentIndex(self.register_win_num)

    def register_window(self) -> RegisterView:
        return self._stacked_widget.widget(self.register_win_num)

    def auth_window(self) -> AuthView:
        return self._stacked_widget.widget(self.auth_win_num)



