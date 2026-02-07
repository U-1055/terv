import dataclasses

from PySide6.QtCore import Signal, QObject

import typing as tp
import logging
import threading

from client.src.gui.windows.windows import BaseWindow
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
        self._access_token_status = True
        self._refresh_token_status = True
        self._main_thread_id = threading.get_ident()

    def _prepare_no_data(self, data_get_func: tp.Callable[[], Request], data_get_request: Request, calling_func: tp.Callable):
        """
        Повторяет запрос в случае, если отсутствуют данные, получаемые этим запросом.

        :param data_get_func: Функция получения данных, которые отсутствуют. В нём должен отправляться запрос
                                на получение этих данных.
        :param data_get_request: Запрос (объект requester.Request) для получения этих данных.
        :param calling_func: Вызывающая функция (которой требуются отсутствующие данные).

        """
        logging.info(f"Starting prepare request that returns no data. Request: {data_get_request}. "
                     f"Calling method: {calling_func}. Data get method: {data_get_func}."
                     f"Request's exception: {data_get_request.exception()}")

        if type(data_get_request.exception()) is err.NetworkTimeoutError:
            return
        if not self._access_token_status or not self._refresh_token_status:  # Если просрочены токены, запрос не повторяется (Чтобы избежать зацикливания)
            logging.info(f'Request is not prepared: invalid tokens status - Access: {self._access_token_status}.'
                         f'Refresh: {self._refresh_token_status}.')
            return

        # Запрос либо отправлен, но завершён (и данных нет), либо не отправлен.
        if data_get_request is not None and data_get_request.is_finished() or data_get_request is None:
            new_request = data_get_func()
            # Подключаемся к сигналу завершения запроса, чтобы выполнить вызывающий метод снова, когда будут получены данные
            new_request.finished.connect(lambda _: calling_func())
        else:  # Запрос отправлен, но не завершён
            data_get_request.finished.connect(lambda _: calling_func())

    def _set_new_tokens(self, tokens: dict):
        access_token = tokens.get(CommonStruct.access_token)
        refresh_token = tokens.get(CommonStruct.refresh_token)
        self._model.set_access_token(access_token)
        self._model.set_refresh_token(refresh_token)
        self.set_access_token_status(True)  # Access-токен снова валиден
        self.set_refresh_token_status(True)  # Новый refresh тоже валиден

    def _update_tokens(self):
        """Обновляет access и refresh токены по refresh-токену. Обновляет обработчик после получения токенов."""

        refresh_token = self._model.get_refresh_token()
        tokens = self._requester.update_tokens(refresh_token)
        tokens.finished.connect(lambda response: self._prepare_request(response, self._set_new_tokens))
        tokens.finished.connect(lambda _: self.update_state)

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
            self.set_access_token_status(False)
            self._update_tokens()

        except err.ExpiredRefreshToken as e:  # Обработка просрочки refresh-токена
            logging.debug('Expired Refresh Token')
            self.set_refresh_token_status(False)
            self.incorrect_tokens_update.emit()

        except err.NetworkTimeoutError as e:  # Обработка ошибки сети
            self.network_error_occurred.emit()

    def access_token_status(self) -> bool:
        return self._access_token_status

    def refresh_token_status(self) -> bool:
        return self._refresh_token_status

    def set_access_token_status(self, status: bool):
        self._access_token_status = status
        logging.debug(f'Access token status: {status}')

    def set_refresh_token_status(self, status: bool):
        self._refresh_token_status = status
        logging.debug(f'Refresh token status: {status}')

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


@dataclasses.dataclass
class BaseWindowHandlerRequests:
    pass

