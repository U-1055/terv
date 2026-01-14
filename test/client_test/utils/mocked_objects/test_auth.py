from PySide6.QtCore import Signal, QObject
from test.client_test.utils.mocked_objects.views import TestBaseView


class TestAuthView(TestBaseView):
    """
    Окно авторизации.
    :param normal_style: обычный стиль QLabel.
    :param error_style: стиль, который будет применён к QLabel, если в него введены неверные данные.
    :param labels: класс надписей GUI.

    """

    btn_auth_pressed = Signal()
    btn_to_register_pressed = Signal()

    def __init__(self, normal_style: str, error_style: str, labels):
        super().__init__()
        self._login = None
        self._password = None
        self._email = None
        self.is_error = False

    def press_btn_auth(self):
        self.btn_auth_pressed.emit()

    def press_btn_to_register(self):
        self.btn_to_register_pressed.emit()

    def password(self) -> str:
        return self._password

    def set_password(self, password: str):
        self._password = password

    def login(self) -> str:
        return self._login

    def set_login(self, login: str):
        self._login = login

    def set_error_login(self, msg: str):
        self.is_error = True

    def set_normal_login(self):
        self.is_error = False

    def set_error_password(self, msg: str):
        self.is_error = True

    def set_normal_password(self):
        self.is_error = False


class TestRegisterView(TestBaseView):

    btn_register_pressed = Signal()
    btn_to_auth_pressed = Signal()

    def __init__(self, normal_style: str, error_style: str, labels):
        super().__init__()
        self._login = None
        self._password = None
        self._email = None
        self.is_error = False

    def press_btn_register(self):
        self.btn_register_pressed.emit()

    def press_btn_to_auth(self):
        self.btn_to_auth_pressed.emit()

    def password(self) -> str:
        return self._password

    def set_password(self, password: str):
        self._password = password

    def login(self) -> str:
        return self._login

    def set_login(self, login: str):
        self._login = login

    def email(self) -> str:
        return self._email

    def set_email(self, email: str):
        self._email = email

    def set_error_login(self, msg: str):
        self.is_error = True

    def set_normal_login(self):
        self.is_error = False

    def set_error_password(self, msg: str):
        self.is_error = True

    def set_normal_password(self):
        self.is_error = False

    def set_error_email(self, msg: str):
        self.is_error = True

    def set_normal_email(self):
        self.is_error = False


class TestPopUpAuthWindow(QObject):
    register_view_sent = Signal(TestRegisterView)  # Представления переданы
    auth_view_sent = Signal(TestAuthView)

    def register_window(self) -> TestRegisterView:
        register_view = TestRegisterView('', '', '')
        self.register_view_sent.emit(register_view)
        return register_view

    def auth_window(self) -> TestAuthView:
        auth_view = TestAuthView('', '', '')
        self.auth_view_sent.emit(auth_view)
        return auth_view
