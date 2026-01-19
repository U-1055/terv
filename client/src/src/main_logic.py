from PySide6.QtCore import QTimer

import typing as tp
import logging

from client.src.gui.main_view import MainWindow
from client.src.requester.requester import Requester
from client.utils.timeout_list import TimeoutList
from client.src.src.handlers.window_handlers.userflow_handler import UserFlowWindowHandler
from client.src.src.handlers.window_handlers.personal_tasks_handler import PersonalTasksWindowHandler
from client.src.src.handlers.window_handlers.base import BaseWindowHandler
from client.src.client_model.model import Model
from client.src.base import DataStructConst, GuiLabels
from client.src.src.handlers.window_handlers.main_auth_window_handler import MainAuthWindowHandler

logging.basicConfig(level=logging.DEBUG)
logging.debug('Module main_logic.py is running')


class Logic:
    """Главный класс логики приложения."""

    def __init__(
            self,
            view: MainWindow,
            model: Model,
            requester: Requester,
            timeout: int,
            data_const: DataStructConst = DataStructConst(),
            labels: GuiLabels = GuiLabels()
    ):
        self._view = view
        self._requester = requester
        self._model = model
        self._data_const = data_const
        self._labels = labels
        self._timer = QTimer()
        self._user = None

        self._opened_now: BaseWindowHandler = None
        self._current_open_method: tp.Callable = self._open_userflow

        self._win_handlers = TimeoutList(timeout, self._close_outdated_window, 15)

        self._view.btn_open_userflow_pressed.connect(self._open_userflow)
        self._view.btn_open_personal_tasks_window_pressed.connect(self._open_personal_tasks_window)
        self._view.btn_update_pressed.connect(self._update_state)

        self._timer.timeout.connect(self._update_current_window)
        self._timer.start(1000 * 60)

    def _on_auth_complete(self):
        self._view.show_message(self._labels.op_complete, self._labels.authentication_complete)
        self._auth_window_handler.close()

    def _on_registration_complete(self):
        self._view.show_message(self._labels.op_complete, self._labels.register_complete)

    def _on_network_error_occurred(self):
        self._view.show_message(self._labels.error_occurred, self._labels.network_error)

    def _authorize(self):
        logging.debug('Opening authorize window')
        main_auth_window = self._view.open_auth_window()
        self._auth_window_handler = MainAuthWindowHandler(main_auth_window, self._view, self._requester, self._model)
        self._auth_window_handler.auth_complete.connect(self._on_auth_complete)
        self._auth_window_handler.registration_complete.connect(self._on_registration_complete)
        self._view.show_modal_window(main_auth_window)

    def _update_current_window(self):
        if self._opened_now:
            logging.debug('Updating current hanlder...')
            self._opened_now.update_data()

    def _update_state(self):
        if self._opened_now:
            self._close_outdated_window(self._opened_now)
        self._current_open_method()

    def _show_error(self, title: str, message: str):
        self._view.show_error(title, message)

    def _close_outdated_window(self, handler: BaseWindowHandler):
        handler.close()
        self._win_handlers.remove(handler)

    def _get_last_handler(self, type_) -> BaseWindowHandler | None:
        for handler in self._win_handlers:
            if isinstance(handler, type_):
                return handler

    def _open_personal_tasks_window(self):
        if isinstance(self._opened_now, PersonalTasksWindowHandler):
            return

        self._win_handlers.update()
        self._current_open_method = self._open_personal_tasks_window
        current_handler = self._get_last_handler(PersonalTasksWindowHandler)

        if current_handler:
            self._opened_now = current_handler
            self._view.open_window(current_handler.get_window())

        else:
            window = self._view.open_personal_tasks_window()
            win_handler = PersonalTasksWindowHandler(window, self._view, self._requester, self._model)
            self._win_handlers.append(win_handler)
            self._opened_now = win_handler

    def _open_userflow(self):
        if isinstance(self._opened_now, UserFlowWindowHandler):
            return

        self._win_handlers.update()
        self._current_open_method = self._open_userflow
        current_handler = self._get_last_handler(UserFlowWindowHandler)

        if current_handler:
            self._opened_now = current_handler
            self._view.open_window(current_handler.get_window())
        else:
            window = self._view.open_userflow_window()
            win_handler = UserFlowWindowHandler(window, self._view, self._requester, self._model)
            self._win_handlers.append(win_handler)
            self._opened_now = win_handler
            win_handler.incorrect_tokens_update.connect(self._authorize)
            win_handler._update_state()
        self._opened_now.network_error_occurred.connect(self._on_network_error_occurred)


if __name__ == '__main__':
    pass
