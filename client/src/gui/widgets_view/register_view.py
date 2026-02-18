"""Представление виджета регистрации"""

from PySide6.QtWidgets import (QWidget, QFormLayout, QVBoxLayout, QPushButton, QHBoxLayout, QLineEdit, QLabel,
                               QRadioButton, QCheckBox)
from PySide6.QtCore import Signal

from client.src.base import GuiLabels
from client.src.gui.widgets_view.base_view import BaseView
import client.src.gui.aligns as al


class RegisterView(BaseView):

    btn_register_pressed = Signal()
    btn_to_auth_pressed = Signal()

    def __init__(self, normal_style: str, error_style: str, labels: GuiLabels = GuiLabels()):
        super().__init__()
        self._normal_style, self._error_style, self._labels = normal_style, error_style, labels

        self._main_layout = QVBoxLayout()
        self._form_layout = QFormLayout()

        btn_register = QPushButton(self._labels.register)
        btn_register.clicked.connect(self.press_btn_register)

        btn_to_auth = QPushButton(self._labels.authorize)
        btn_to_auth.clicked.connect(self.press_btn_to_auth)

        self._line_edit_password = QLineEdit()
        self._line_edit_login = QLineEdit()
        self._line_edit_email = QLineEdit()

        self._check_hide = QRadioButton(GuiLabels.hide_password)
        self._check_hide.clicked.connect(self._on_btn_hide_pressed)
        self._check_hide.click()

        self._lbl_message = QLabel()

        self._form_layout.addRow(self._labels.login, self._line_edit_login)
        self._form_layout.addRow(self._labels.password, self._line_edit_password)
        self._form_layout.addRow(self._labels.email, self._line_edit_email)
        self._form_layout.addRow(self._check_hide)

        self._main_layout.addLayout(self._form_layout, 5)
        self._main_layout.addWidget(self._lbl_message, 1)
        self._lbl_message.hide()
        self._main_layout.addWidget(btn_register, 2)
        self._main_layout.addWidget(btn_to_auth, 1, alignment=al.AlignLeft)

        self.setLayout(self._main_layout)

    def _on_btn_hide_pressed(self):
        if self._check_hide.isChecked():
            self._line_edit_password.setEchoMode(QLineEdit.EchoMode.Password)
        else:
            self._line_edit_password.setEchoMode(QLineEdit.EchoMode.Normal)

    def press_btn_register(self):
        self.btn_register_pressed.emit()

    def press_btn_to_auth(self):
        self.btn_to_auth_pressed.emit()

    def password(self) -> str:
        return self._line_edit_password.text()

    def set_password(self, password: str):
        self._line_edit_password.setText(password)

    def login(self) -> str:
        return self._line_edit_login.text()

    def set_login(self, login: str):
        self._line_edit_login.setText(login)

    def email(self) -> str:
        return self._line_edit_email.text()

    def set_email(self, email: str):
        self._line_edit_email.setText(email)

    def set_error_login(self, msg: str):
        self._line_edit_login.setStyleSheet(self._error_style)
        if self._lbl_message.isHidden():
            self._lbl_message.show()
            self._lbl_message.setText(msg)

    def set_normal_login(self):
        self._line_edit_login.setStyleSheet(self._normal_style)
        if not self._lbl_message.isHidden():
            self._lbl_message.setText('')
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

    def set_error_email(self, msg: str):
        self._line_edit_email.setStyleSheet(self._error_style)
        if self._lbl_message.isHidden():
            self._lbl_message.show()
            self._lbl_message.setText(msg)

    def set_normal_email(self):
        self._line_edit_email.setStyleSheet(self._normal_style)
        if not self._lbl_message.isHidden():
            self._lbl_message.setText('')
            self._lbl_message.hide()


if __name__ == '__main__':
    pass
