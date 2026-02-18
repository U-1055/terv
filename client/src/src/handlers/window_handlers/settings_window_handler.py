import logging

from PySide6.QtCore import Signal

from client.src.src.handlers.window_handlers.base import BaseWindowHandler
from client.src.gui.windows.settings_window import SettingsWindow
from client.src.requester.requester import Requester
from client.src.gui.main_view import MainWindow
from client.src.client_model.model import Model
from client.src.base import DataStructConst
import client.models.common_models as cm


class SettingsWindowHandler(BaseWindowHandler):
    """
    Обработчик окна настроек.

    :var btn_log_in_pressed: Сигнал, испускаемый при нажатии на кнопку входа.
    :var btn_log_out_pressed: Сигнал, испускаемый при нажатии на кнопку выхода из аккаунта.
    :var theme_changed: Сигнал, испускаемый при изменении темы. Передаёт название стиля темы.

    """
    btn_log_in_pressed = Signal()
    btn_log_out_pressed = Signal()
    theme_changed = Signal(str)

    def __init__(self, window: SettingsWindow, main_view: MainWindow, requester: Requester, model: Model):
        super().__init__(window, main_view, requester, model)
        self._user: cm.User | None = None

        self._window, self._main_view, self._requester, self._model = window, main_view, requester, model
        self._window.btn_log_in_pressed.connect(self._on_btn_log_in_pressed)
        self._window.btn_log_out_pressed.connect(self._on_btn_log_out_pressed)
        self._theme_switcher = self._window.place_theme_widget()
        self._theme_switcher.theme_changed.connect(self.change_theme)

        self._window.set_mode_log_in()
        self._set_theme_switcher()

    def _set_user_data_from_request(self, user: tuple[dict, ...]):
        self.set_user_data(cm.User(**user[0]))

    def _set_theme_switcher(self):
        self._theme_switcher.put_theme(DataStructConst.light, DataStructConst.light_main_color)
        self._theme_switcher.put_theme(DataStructConst.dark, DataStructConst.dark_main_color)

    def press_btn_log_in(self):
        self.btn_log_in_pressed.emit()

    def press_btn_log_out(self):
        self.btn_log_out_pressed.emit()

    def change_theme(self, theme: str):
        self.theme_changed.emit(theme)

    def _on_btn_log_out_pressed(self):
        access, refresh = self._model.get_access_token(), self._model.get_refresh_token()
        request = self._requester.recall_tokens(access, refresh)
        self.press_btn_log_out()
        self._model.set_access_token('')
        self._model.set_refresh_token('')
        self._window.set_mode_log_in()

    def _on_btn_log_in_pressed(self):
        self.press_btn_log_in()

    def update_state(self):
        access = self._model.get_access_token()
        request = self._requester.get_user_info(access)
        request.finished.connect(lambda request_: self._prepare_request(request_, self._set_user_data_from_request))

    def set_mode_log_in(self):
        self._window.set_mode_log_in()

    def set_mode_log_out(self):
        self._window.set_mode_log_out()

    def set_user_data(self, user: cm.User):
        logging.debug(f'User info set: {user}')
        self._user = user
        self._window.set_username(user.username)

    def user_data(self) -> cm.User:
        return self._user
