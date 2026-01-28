import asyncio
import logging

from PySide6.QtCore import Signal, QObject

import typing as tp

from client.src.gui.windows.windows import BaseWindow
from client.models.base import Base
from client.src.gui.main_view import MainWindow
from client.src.requester.requester import Requester
from client.src.client_model.model import Model
import client.src.requester.errors as err
from common.base import CommonStruct


class BaseWindowHandler(QObject):
    closed = Signal()
    error_occurred = Signal(str, str)  # Произошла ошибка
    incorrect_tokens_update = Signal()  # Ошибка при обновлении токенов
    tokens_updated = Signal()  # Установлены новые токены
    network_error_occurred = Signal()  # Произошла ошибка сети

    def __init__(self, window: BaseWindow, main_view: MainWindow, requester: Requester, model: Model):
        super().__init__()
        self._window = window
        self._main_view = main_view
        self._requester = requester
        self._model = model

    def _set_new_tokens(self, tokens: dict):
        access_token = tokens.get(CommonStruct.access_token)
        refresh_token = tokens.get(CommonStruct.refresh_token)
        self._model.set_access_token(access_token)
        self._model.set_refresh_token(refresh_token)

    def _update_tokens(self):
        """Обновляет access и refresh токены по refresh-токену."""

        refresh_token = self._model.get_refresh_token()
        tokens: asyncio.Future = self._requester.update_tokens(refresh_token)
        tokens.add_done_callback(lambda future: self._prepare_request(future, self._set_new_tokens))

    def _send_error(self, title: str, message: str):
        self.error_occurred.emit(title, message)

    def _prepare_request(self, future: asyncio.Future, prepare_data_func: tp.Callable = None):
        """
        Обрабатывает асинхронный запрос. Отправляет Response.content в prepare_data_dunc.
        Если данных не получено - выводит ошибку. Если access-токен недействителен, обновляет его по refresh-токену.
        Если refresh-токен недействителен, испускает сигнал incorrect_tokens_update
        :param future: Future-объект asyncio.
        :param prepare_data_func: функция, куда будет передан результат Future future.result().
        """
        try:
            result = future.result()
            content = result.content
            if prepare_data_func:
                if result:
                    prepare_data_func(content)
                else:
                    self._send_error('Error', 'The data has not been received')
        except err.ExpiredAccessToken as e:  # Обработка просрочки access-токена
            self._update_tokens()

        except err.ExpiredRefreshToken as e:  # Обработка просрочки refresh-токена
            logging.debug('Expired Refresh Token')
            self.incorrect_tokens_update.emit()

        except err.NetworkTimeoutError as e:  # Обработка ошибки сети
            self.network_error_occurred.emit()

        except Exception as e:  # Все остальные исключения передаются вызывающей стороне
            raise e

    def update_data(self):
        """
        Обновляет данные в обработчике. При вызове обработчик собирает данные со своих виджетов, делает соответствующие
        запросы на сервер, затем обновляет данных в виджетах.
        """
        pass

    def get_window(self):
        return self._window

    def close(self):
        self._window.close()
        self.closed.emit()

    def flush(self):
        pass

