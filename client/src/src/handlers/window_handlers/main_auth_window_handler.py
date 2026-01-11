from PySide6.QtCore import Signal

import asyncio

from client.src.gui.windows.auth_window import PopUpAuthWindow
from client.src.src.handlers.window_handlers.base import BaseWindowHandler
from client.src.gui.main_view import MainWindow
from client.src.requester.requester import Requester
from client.src.client_model.model import Model
from client.src.src.handlers.widgets_view_handlers.auth_view_handlers import AuthViewHandler, RegisterViewHandler
from client.src.base import DataStructConst, GuiLabels
import client.src.requester.errors as err


class MainAuthWindowHandler(BaseWindowHandler):
    tokens_updated = Signal()
    authorize_complete = Signal()  # Авторизация прошла успешно

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

        def prepare_auth(future: asyncio.Future):
            try:
                self._prepare_request(future, self._set_new_tokens)
            except err.UnknownCredentials:
                self._auth_handler.set_error_password(self._labels.incorrect_credentials)
                self._auth_handler.set_error_login(self._labels.incorrect_credentials)

        login = self._auth_handler.login
        password = self._auth_handler.password

        request: asyncio.Future = self._requester.authorize(login, password)
        request.add_done_callback(lambda future: prepare_auth(future))

    def _on_tried_to_register(self):

        login = self._register_handler.login
        password = self._register_handler.password
        email = self._register_handler.email

        try:
            request: asyncio.Future = self._requester.register(login, password, email)
            request.add_done_callback(lambda future: self._prepare_request(future, self._set_new_tokens))
        except err.LoginAlreadyExists:  # ToDo: разобраться, какие конкретно ошибки обрабатывать
            self._register_handler.set_error_login(self._labels.used_login)
        except err.IncorrectEmail:
            self._register_handler.set_error_email(self._labels.incorrect_email)
        except err.EmailAlreadyExists:
            self._register_handler.set_error_email(self._labels.used_email)

