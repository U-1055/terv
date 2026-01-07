from PySide6.QtCore import Signal

from client.src.gui.widgets_view.auth_view import AuthView
from client.src.gui.widgets_view.register_view import RegisterView
from client.src.src.handlers.widgets_view_handlers.base import BaseViewHandler
from client.src.base import DataStructConst, GuiLabels


class AuthViewHandler(BaseViewHandler):

    tried_to_auth = Signal()
    tried_to_go_to_register = Signal()

    def __init__(self, auth_view: AuthView, data_const: DataStructConst(), labels: GuiLabels = GuiLabels()):
        super().__init__(auth_view)
        self._data_const = data_const
        self._labels = labels
        self._auth_view = auth_view
        self._auth_view.btn_auth_pressed.connect(self.try_to_auth)
        self._auth_view.btn_to_register_pressed.connect(self.try_to_go_to_register)

    def try_to_auth(self):
        login, password = self._auth_view.login(), self._auth_view.password()

        self._auth_view.set_normal_login()
        self._auth_view.set_normal_password()

        if not login:
            self._auth_view.set_error_login(self._labels.fill_all)
        if not password:
            self._auth_view.set_error_login(self._labels.fill_all)
        if login and password:
            self.tried_to_auth.emit()

    def try_to_go_to_register(self):
        self.tried_to_go_to_register.emit()

    def set_error_login(self, msg: str):
        self._auth_view.set_error_login(msg)

    def set_error_password(self, msg: str):
        self._auth_view.set_error_password(msg)

    def set_normal_login(self):
        self._auth_view.set_normal_login()

    def set_normal_password(self):
        self._auth_view.set_normal_password()

    @property
    def password(self) -> str:
        return self._auth_view.password()

    @password.setter
    def password(self, password: str):
        self._auth_view.set_password(password)

    @property
    def login(self) -> str:
        return self._auth_view.login()

    @login.setter
    def login(self, login: str):
        self._auth_view.set_login(login)


class RegisterViewHandler(BaseViewHandler):

    tried_to_register = Signal()
    tried_to_go_to_auth = Signal()

    def __init__(self, register_view: RegisterView, data_const: DataStructConst = DataStructConst(), labels: GuiLabels = GuiLabels()):
        super().__init__(register_view)
        self._register_view = register_view
        self._data_const = data_const
        self._labels = labels
        self._register_view.btn_register_pressed.connect(self.try_to_register)
        self._register_view.btn_to_auth_pressed.connect(self.try_to_go_to_auth)

    def try_to_register(self):
        login, password, email = self._register_view.login(), self._register_view.password(), self._register_view.email()

        self._register_view.set_normal_email()
        self._register_view.set_normal_password()
        self._register_view.set_normal_login()

        if login and password and email:
            self.tried_to_register.emit()
        if not login:
            self._register_view.set_error_login(self._labels.fill_all)
        if not password:
            self._register_view.set_error_password(self._labels.fill_all)
        if not email:
            self._register_view.set_error_email(self._labels.fill_all)

    def try_to_go_to_auth(self):
        self.tried_to_go_to_auth.emit()

    def set_error_login(self, msg: str):
        self._register_view.set_error_login(msg)

    def set_error_password(self, msg: str):
        self._register_view.set_error_password(msg)

    def set_normal_login(self):
        self._register_view.set_normal_login()

    def set_normal_password(self):
        self._register_view.set_normal_password()

    def set_error_email(self, msg: str):
        self._register_view.set_error_email(msg)

    def set_normal_email(self):
        self._register_view.set_normal_email()

    @property
    def password(self) -> str:
        return self._register_view.password()

    @password.setter
    def password(self, password: str):
        self._register_view.set_password(password)

    @property
    def login(self) -> str:
        return self._register_view.login()

    @login.setter
    def login(self, login: str):
        self._register_view.set_login(login)

    @property
    def email(self) -> str:
        return self._register_view.email()

    @email.setter
    def email(self, email: str):
        self._register_view.set_email(email)


if __name__ == '__main__':
    pass
