from PySide6.QtCore import QTimer

import typing as tp
import logging

from client.src.gui.main_view import MainWindow
from client.src.gui.sub_widgets.base import BaseWidget
from client.src.requester.requester import Requester
from client.utils.timeout_list import TimeoutList
from client.src.src.handlers.window_handlers.userspace_handler import UserSpaceWindowHandler
from client.src.src.handlers.window_handlers.settings_window_handler import SettingsWindowHandler
from client.src.src.handlers.window_handlers.base import BaseWindowHandler
from client.src.client_model.model import Model
from client.src.base import DataStructConst, GuiLabels, styles_paths
from client.src.src.handlers.window_handlers.main_auth_window_handler import MainAuthWindowHandler
import client.models.common_models as cm
from client.src.client_model.links_handler import LinksHandler
from client.src.requester.cash_manager import CashManager

logging.basicConfig(level=logging.CRITICAL)
logging.debug('Module main_logic.py is running')


class Logic:
    """Главный класс логики приложения."""

    def __init__(
            self,
            view: MainWindow,
            model: Model,
            links_handler: LinksHandler,
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
        self._user: cm.User | None = None
        self._links_handler = links_handler
        self._cash_manager = CashManager(requester, model)
        self._links_handler.set_cash_manager(self._cash_manager)

        self._opened_now: BaseWindowHandler = None
        self._current_open_method: tp.Callable = self._open_userspace

        self._win_handlers = TimeoutList(timeout, self._close_outdated_window, 15)

        self._auth_window_handler: MainAuthWindowHandler | None = None

        current_style = self._model.get_current_style()  # Установка стиля
        if current_style and current_style in (DataStructConst.light_style, DataStructConst.dark_style):
            style = self._model.get_style(current_style)
        else:
            style = self._model.get_style(DataStructConst.dark_style)
            self._model.set_current_style(DataStructConst.dark_style)
        logging.debug(f'Current style: {current_style}.')
        self._view.set_style(style)

        self._view.btn_open_userspace_pressed.connect(self._open_userspace)
        self._view.btn_update_pressed.connect(self._update_state)
        self._view.btn_open_settings_pressed.connect(self._open_settings)

        self._timer.timeout.connect(self._update_current_window)
        self._timer.start(1000 * 60)
        self._timer.singleShot(100, self._open_userspace)

    def _on_theme_changed(self, style_name: str):
        style_path = styles_paths.get(style_name)
        style = self._model.get_style(style_path)
        self._model.set_current_style(style_path)
        self._view.set_style(style)

    def _on_auth_complete(self):
        self._view.show_message(self._labels.op_complete, self._labels.authentication_complete)
        self._auth_window_handler.close()
        self._opened_now.set_access_token_status(True)
        self._opened_now.set_refresh_token_status(True)  # Токены обновлены
        self._opened_now.update_state()

    def _on_registration_complete(self):
        self._view.show_message(self._labels.op_complete, self._labels.register_complete)

    def _on_network_error_occurred(self):
        self._view.show_message(self._labels.error_occurred, self._labels.network_error)
        if self._auth_window_handler:
            self._auth_window_handler.close()

    def _close(self):
        """Закрывает приложение."""
        self._opened_now.update_data()
        self._view.close()

    def _on_user_data_received(self, handler: UserSpaceWindowHandler):
        self._user = handler.data_model().user

    def _on_btn_log_out_pressed(self):
        self._view.show_message(GuiLabels.message, GuiLabels.account_leaved)

    def _authorize(self):
        logging.debug('Opening authorize window by tokens expiration.')
        main_auth_window = self._view.open_auth_window()
        self._auth_window_handler = MainAuthWindowHandler(main_auth_window, self._view, self._requester, self._model)
        self._auth_window_handler.auth_complete.connect(self._on_auth_complete)
        self._auth_window_handler.registration_complete.connect(self._on_registration_complete)
        self._view.show_dialog_window(main_auth_window, title=GuiLabels.registration_window, frameless=True)
        main_auth_window.btn_exit_pressed.connect(self._close)

    def _on_log_in_completed(self):
        self._view.show_message(self._labels.op_complete, self._labels.authentication_complete)
        self._auth_window_handler.close()
        self._opened_now.set_access_token_status(True)
        self._opened_now.set_refresh_token_status(True)
        if isinstance(self._opened_now, SettingsWindowHandler):
            self._opened_now.set_mode_log_in()

    def _on_btn_log_in_pressed(self):
        logging.debug("Opening authorize window by user's request")
        main_auth_window = self._view.open_auth_window()
        self._auth_window_handler = MainAuthWindowHandler(main_auth_window, self._view, self._requester, self._model)
        self._auth_window_handler.auth_complete.connect(self._on_log_in_completed)
        self._auth_window_handler.registration_complete.connect(self._on_registration_complete)
        self._view.show_dialog_window(main_auth_window, title=GuiLabels.registration_window, frameless=False)
        self._auth_window_handler.network_error_occurred.connect(self._on_network_error_occurred)
        main_auth_window.btn_exit_pressed.connect(self._close)

    def _update_current_window(self):
        if self._opened_now:
            logging.debug(f'Updating current hanlder. Handler: {self._opened_now}')
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

    def _open_base_window(self, window_class: tp.Type[BaseWindowHandler], open_method: tp.Callable,
                          window_open_method: tp.Callable):
        if isinstance(self._opened_now, window_class):
            return

        self._win_handlers.update()
        self._current_open_method = open_method
        current_handler = self._get_last_handler(BaseWindowHandler)

        if current_handler:
            self._opened_now = current_handler
            self._view.open_window(current_handler.get_window())
        else:
            window = window_open_method()
            if window_class is UserSpaceWindowHandler:
                win_handler = window_class(window, self._view, self._requester, self._model, self._links_handler)
            else:
                win_handler = window_class(window, self._view, self._requester, self._model)
            self._win_handlers.append(win_handler)
            self._opened_now = win_handler
            win_handler.incorrect_tokens_update.connect(self._authorize)

        self._opened_now.network_error_occurred.connect(self._on_network_error_occurred)

    def _open_userspace(self):
        if type(self._opened_now) is UserSpaceWindowHandler:
            return
        self._open_base_window(UserSpaceWindowHandler, self._open_userspace, lambda: self._view.open_userspace_window(DataStructConst.userspace_loading_time))
        self._opened_now.user_data_received.connect(lambda: self._on_user_data_received(self._opened_now))
        self._opened_now.update_state()

    def _open_settings(self):
        self._open_base_window(SettingsWindowHandler, self._open_settings, self._view.open_settings)
        self._opened_now: SettingsWindowHandler
        self._opened_now.btn_log_out_pressed.connect(self._on_btn_log_out_pressed)
        self._opened_now.btn_log_in_pressed.connect(self._on_btn_log_in_pressed)
        self._opened_now.theme_changed.connect(self._on_theme_changed)

        if self._user:
            self._opened_now.set_user_data(self._user)
            self._opened_now.set_mode_log_out()


if __name__ == '__main__':
    pass
