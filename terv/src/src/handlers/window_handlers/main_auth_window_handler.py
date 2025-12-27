from PySide6.QtCore import Signal

import asyncio

from terv.src.gui.windows.auth_window import PopUpAuthWindow
from terv.src.src.handlers.window_handlers.base import BaseWindowHandler
from terv.src.gui.main_view import MainWindow
from terv.src.requester.requester import Requester
from terv.src.client_model.model import Model
from terv.src.src.handlers.widgets_view_handlers.auth_view_handlers import AuthViewHandler, RegisterViewHandler
from terv.src.base import DataStructConst
import terv.src.requester.errors as err


class MainAuthWindowHandler(BaseWindowHandler):
    tokens_updated = Signal()

    def __init__(self, window: PopUpAuthWindow, main_view: MainWindow, requester: Requester, model: Model):
        super().__init__(window, main_view, requester, model)
        self._window = window
        self._requester = requester
        self._model = model

        auth_window = self._window.auth_window()
        register_window = self._window.register_window()

        self._auth_handler = AuthViewHandler(auth_window, DataStructConst())
        self._register_handler = RegisterViewHandler(register_window)

    def _prepare_updating(self, tokens: dict):
        self._set_new_tokens(tokens)
        self.tokens_updated.emit()

    def on_tried_to_go_to_auth(self):
        self._window.choose_auth_window()

    def on_tried_to_go_to_register(self):
        self._window.choose_register_window()

    def on_tried_to_auth(self):
        login = self._auth_handler.login
        password = self._auth_handler.password

        try:
            request: asyncio.Future = self._requester.authorize(login, password)
            request.add_done_callback(lambda future: self._prepare_request(future, self._set_new_tokens))
        except err.IncorrectPassword:
            self._auth_handler.set_error_password()
        except err.IncorrectLogin:
            self._auth_handler.set_error_login()

    def on_tried_to_register(self):
        login = self._register_handler.login
        password = self._register_handler.password
        email = self._register_handler.email

        try:
            request: asyncio.Future = self._requester.register(login, password, email)
            request.add_done_callback(lambda future: self._prepare_request(future, self._set_new_tokens))
        except err.IncorrectPassword:
            self._register_handler.set_error_password()
        except err.IncorrectLogin:
            self._register_handler.set_error_login()
        except err.IncorrectEmail:
            self._register_handler.set_error_email()
