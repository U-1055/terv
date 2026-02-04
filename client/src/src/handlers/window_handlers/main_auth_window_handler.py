from PySide6.QtCore import Signal

import asyncio

from client.src.gui.windows.auth_window import PopUpAuthWindow
from client.src.src.handlers.window_handlers.base import BaseWindowHandler
from client.src.gui.main_view import MainWindow
from client.src.requester.requester import Requester, Request
from client.src.client_model.model import Model
from client.src.src.handlers.widgets_view_handlers.auth_view_handlers import AuthViewHandler, RegisterViewHandler
from client.src.base import DataStructConst, GuiLabels
import client.src.requester.errors as err
from common.base import CommonStruct, check_password


class MainAuthWindowHandler(BaseWindowHandler):

    registration_complete = Signal()  # Регистрация прошла успешно
    auth_complete = Signal()  # Аутентификация прошла успешно

    def __init__(self, window: PopUpAuthWindow, main_view: MainWindow, requester: Requester, model: Model, labels: GuiLabels = GuiLabels()):
        super().__init__(window, main_view, requester, model)
        self._window = window
        self._requester = requester
        self._model = model
        self._labels = labels

        auth_window = self._window.auth_window()
        register_window = self._window.register_window()

        self._auth_handler = AuthViewHandler(auth_window, DataStructConst())
        self._register_handler = RegisterViewHandler(register_window)

        self._auth_handler.tried_to_auth.connect(self._on_tried_to_auth)
        self._auth_handler.tried_to_go_to_register.connect(self._on_tried_to_go_to_register)
        self._register_handler.tried_to_register.connect(self._on_tried_to_register)
        self._register_handler.tried_to_go_to_auth.connect(self._on_tried_to_go_to_auth)

    def _prepare_updating(self, tokens: dict):
        self._set_new_tokens(tokens)
        self.tokens_updated.emit()

    def _on_tried_to_go_to_auth(self):
        self._window.choose_auth_window()

    def _on_tried_to_go_to_register(self):
        self._window.choose_register_window()

    def _on_tried_to_auth(self):

        def prepare_auth(request: Request):  # ToDo: как можно избежать написания вложенных функций под каждый запрос
            try:
                self._prepare_request(request, self._set_new_tokens)
                self.auth_complete.emit()
            except err.UnknownCredentials:
                self._auth_handler.set_error_password(self._labels.incorrect_credentials)
            except (err.NoLogin, err.NoPassword):
                self._auth_handler.set_error_login(self._labels.fill_all)

        login = self._auth_handler.login
        password = self._auth_handler.password

        if not all((login, password)):  # Нет параметра
            self._auth_handler.set_error_login(self._labels.fill_all)
            return

        request = self._requester.authorize(login, password)
        request.finished.connect(prepare_auth)

    def _on_tried_to_register(self):

        def prepare_register(request: Request):
            try:
                self._prepare_request(request)
                self.registration_complete.emit()
            # Ошибки, которые можно обнаружить только после запроса на сервер
            except err.LoginAlreadyExists:
                self._register_handler.set_error_login(self._labels.used_login)
            except err.IncorrectEmail:
                self._register_handler.set_error_email(self._labels.incorrect_email)
            except err.EmailAlreadyExists:
                self._register_handler.set_error_email(self._labels.used_email)
            # Ошибки, которые можно обнаружить на клиенте (Проверяются на всякий случай)
            except (err.NoLogin, err.NoEmail, err.NoPassword):
                self._register_handler.set_error_login(self._labels.fill_all)
            except err.IncorrectLogin:
                self._register_handler.set_error_login(self._labels.incorrect_login)
            except err.IncorrectPassword:
                self._register_handler.set_error_password(self._labels.incorrect_password)

        login = self._register_handler.login
        password = self._register_handler.password
        email = self._register_handler.email

        is_error = False

        if not all((login, password, email)):  # Нет параметра
            self._register_handler.set_error_login(self._labels.fill_all)
        elif len(login) < CommonStruct.min_login_length or len(login) > CommonStruct.max_login_length:  # Недопустимая длина логина
            self._register_handler.set_error_login(self._labels.incorrect_login)
        elif not check_password(password):  # Пароль не подходит
            self._register_handler.set_error_password(self._labels.incorrect_password)

        if is_error:
            return

        request = self._requester.register(login, password, email)
        request.finished.connect(prepare_register)


