from PySide6.QtCore import Signal, QObject

import typing as tp
import asyncio
import logging
import threading

from client.src.gui.windows.windows import BaseWindow
from client.models.base import Base
from client.src.gui.main_view import MainWindow
from client.src.requester.requester import Requester, Request, RequestsGroup
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
        self._main_thread_id = threading.get_ident()

    def _set_new_tokens(self, tokens: dict):
        access_token = tokens.get(CommonStruct.access_token)
        refresh_token = tokens.get(CommonStruct.refresh_token)
        self._model.set_access_token(access_token)
        self._model.set_refresh_token(refresh_token)

    def _update_tokens(self):
        """Обновляет access и refresh токены по refresh-токену."""

        refresh_token = self._model.get_refresh_token()
        tokens = self._requester.update_tokens(refresh_token)
        tokens.finished.connect(lambda response: self._prepare_request(response, self._set_new_tokens))

    def _send_error(self, title: str, message: str):
        self.error_occurred.emit(title, message)

    def _prepare_requests_group(self, requests_group: RequestsGroup, prepare_group_func: tp.Callable = None):
        """Обрабатывает группу запросов RequestsGroup. Передаёт группу в переданную функцию."""
        for request in requests_group.requests():
            self._prepare_request(request)
        prepare_group_func(requests_group)

    def _prepare_request(self, request: Request, prepare_data_func: tp.Callable = None):
        """
        Обрабатывает асинхронный запрос. Отправляет Response.content в prepare_data_dunc.
        Если данных не получено - выводит ошибку. Если access-токен недействителен, обновляет его по refresh-токену.
        Если refresh-токен недействителен, испускает сигнал incorrect_tokens_update
        :param request: объект запроса Request.
        :param prepare_data_func: функция, куда будет передан результат Future future.result().
        """
        thread_id = threading.get_ident()
        if thread_id != self._main_thread_id:
            logging.warning(f'Preparing of the request executing in other thread: ID: {thread_id}. Main thread: {self._main_thread_id}')

        try:
            result = request.result()
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

    def update_data(self):
        """
        Обновляет данные в обработчике. При вызове обработчик собирает данные со своих виджетов, делает соответствующие
        запросы на сервер, затем обновляет данных в виджетах.
        """
        pass

    def update_state(self):
        """Обновляет состояние обработчика. Содержит логику настройки обработчика."""
        pass

    def get_window(self):
        return self._window

    def close(self):
        self._window.close()
        self.closed.emit()

    def flush(self):
        pass

