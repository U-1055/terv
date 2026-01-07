from PySide6.QtWidgets import QWidget, QFormLayout, QVBoxLayout, QPushButton, QHBoxLayout, QLineEdit, QLabel
from PySide6.QtCore import Signal

from client.src.base import GuiLabels
from client.src.gui.widgets_view.base_view import BaseView


class AuthView(BaseView):
    """
    Окно авторизации.
    :param normal_style: обычный стиль QLabel.
    :param error_style: стиль, который будет применён к QLabel, если в него введены неверные данные.
    :param labels: класс надписей GUI.

    """

    btn_auth_pressed = Signal()
    btn_to_register_pressed = Signal()

    def __init__(self, normal_style: str, error_style: str, labels: GuiLabels = GuiLabels()):
        super().__init__()
        self._labels, self._normal_style, self._error_style = labels, normal_style, error_style

        self._main_layout = QVBoxLayout()
        self._form_layout = QFormLayout()

        btn_auth = QPushButton(self._labels.authorize)
        btn_auth.clicked.connect(self.press_btn_auth)

        btn_to_register = QPushButton(self._labels.register)
        btn_to_register.clicked.connect(self.press_btn_to_register)

        self._lbl_message = QLabel()

        self._line_edit_password = QLineEdit()
        self._line_edit_login = QLineEdit()

        self._form_layout.addRow(self._labels.login, self._line_edit_login)
        self._form_layout.addRow(self._labels.password, self._line_edit_password)

        self._main_layout.addLayout(self._form_layout, 5)

        self._lbl_message.hide()

        self._main_layout.addWidget(self._lbl_message, 1)
        self._main_layout.addWidget(btn_auth, 1)

        self._main_layout.addWidget(btn_to_register, 1)

        self.setLayout(self._main_layout)

    def press_btn_auth(self):
        self.btn_auth_pressed.emit()

    def press_btn_to_register(self):
        self.btn_to_register_pressed.emit()

    def password(self) -> str:
        return self._line_edit_password.text()

    def set_password(self, password: str):
        self._line_edit_password.setText(password)

    def login(self) -> str:
        return self._line_edit_login.text()

    def set_login(self, login: str):
        self._line_edit_login.setText(login)

    def set_error_login(self, msg: str):
        self._line_edit_login.setStyleSheet(self._error_style)
        if self._lbl_message.isHidden():
            self._lbl_message.show()
            self._lbl_message.setText(msg)

    def set_normal_login(self):
        self._line_edit_login.setStyleSheet(self._normal_style)
        if not self._lbl_message.isHidden():
            self._lbl_message.hide()

    def set_error_password(self, msg: str):
        self._line_edit_password.setStyleSheet(self._error_style)
        if self._lbl_message.isHidden():
            self._lbl_message.show()
            self._lbl_message.setText(msg)

    def set_normal_password(self):
        self._line_edit_password.setStyleSheet(self._normal_style)
        if not self._lbl_message.isHidden():
            self._lbl_message.setText('')
            self._lbl_message.hide()
