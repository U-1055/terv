"""Слой API."""
import datetime

import httpx

import json
import time
import typing as tp
import asyncio
import threading

import client.src.requester.errors as err
from common.base import DataStruct, ErrorCodes


def run_loop(loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def synchronized_request(func):
    def prepare(*args) -> asyncio.Future:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            thread = threading.Thread(target=lambda: run_loop(loop))
            thread.start()
            time.sleep(0.1)

        future = asyncio.run_coroutine_threadsafe(func(*args), loop)
        return future

    return prepare


class Requester:
    """
    Слой API.

    :param server: адрес сервера.
    :param common_data_struct: константы и требования к данным.
    :param timeout: минимальное время между двумя одинаковыми запросами
    """

    def __init__(self, server: str, common_data_struct: DataStruct = DataStruct, timeout: int = 0.1):
        self._server = server
        self._struct = common_data_struct
        self._timeout = timeout
        self._requests: list[Request] = []

    def _prepare_response(self, response: 'Response'):
        """Обрабатывает ответ: вызывает исключения, если запрос неудачный, передаёт ответ дальше, если успешный"""
        error_code = response.error_id
        message = response.message

        if error_code != ErrorCodes.ok:  # Вызов исключения по коду
            exc = err.exceptions_error_ids.get(error_code)
            raise exc(message)

    async def _make_request(self, request: 'Request') -> 'Response':  # Базовые методы запросов

        async with httpx.AsyncClient() as client:
            if request.method == Request.GET:
                result = await client.get(request.path, headers=request.headers, params=request.query_params)
            elif request.method == Request.POST:
                result = await client.post(request.path, headers=request.headers, params=request.query_params,
                                           json=request.json)
            elif request.method == Request.DELETE:
                result = await client.post(request.path, headers=request.headers, params=request.query_params)
            elif request.method == Request.PUT:
                result = await client.post(request.path, headers=request.headers, params=request.query_params,
                                           json=request.json)
            else:
                raise err.RequesterError(f'Unknown method: {self._last_request.method}')
            self._last_request = request
        try:
            return self._prepare_response(Response(result))
        except err.APIError as e:
            raise e

    @synchronized_request
    async def register(self, login: str, password: str, email: str):
        try:
            request = Request(f'{self._server}/register', Request.POST,
                              json_={
                self._struct.login: login,
                self._struct.password: password,
                self._struct.email: email
            })
            response = await self._make_request(request)
            return response.content.get(self._struct.content)
        except err.APIError as e:
            raise e

    @synchronized_request
    async def update_tokens(self, refresh_token: str) -> dict:
        try:
            request = Request(f'{self._server}/auth/refresh', Request.POST,
                              json_={self._struct.refresh_token: refresh_token})
            response = await self._make_request(request)
            return response.content.get(self._struct.refresh_token)
        except err.APIError as e:
            raise e

    @synchronized_request
    async def authorize(self, login: str, password: str) -> dict:
        try:
            request = Request(f'{self._server}/auth/login', Request.POST,
                              json_={self._struct.login: login, self._struct.password: password})
            response = await self._make_request(request)
            return response.content.get(self._struct.content)
        except err.APIError as e:
            raise e

    @synchronized_request
    async def get_user_info(self, access_token: str, ):
        try:
            request = Request(f'{self._server}/users', Request.GET, headers={'Authorization': access_token})
            response = await self._make_request(request)
            return response.content.get(self._struct.content)
        except err.APIError as e:
            raise e

    @synchronized_request
    async def get_personal_tasks(self, user_id: int, access_token: str, task_id: int = None):
        """Получает личные задачи (конкретную или по user_id)."""
        try:
            path = f'{self._server}/personal_tasks'
            if task_id:
                path = f'{self._server}/personal_tasks/{task_id}'
            request = Request(path, Request.GET, headers={'Authorization': access_token})
            response = await self._make_request(request)
            return response.content.get(self._struct.content)
        except err.APIError as e:
            raise e

    @synchronized_request
    async def retry(self, access_token: str, request_num: int):
        """
        Повторяет один из предыдущих запросов.
        :param access_token: access токен.
        :param request_num: номер запроса относительно последнего. 0 - последний, -1 - предпоследний и т.д.
        """
        try:
            request = self._requests[request_num - 1]  # Обращение к запросу
            if not request:
                raise err.NoLastRequest('There is no requests before.')
            if request.headers.get('Authorization'):
                request.headers['Authorization'] = access_token

            response = await self._make_request(request)
            return response.content.get(self._struct.content)

        except err.APIError as e:
            raise e


class Response:
    """
    Ответ API.

    :var http_code: Код статуса HTTP.
    :var error_id: ID ошибки. Если JSON в ответе отсутствует, error_id = 500 Server Error.
    :var content: Содержимое ответа (только для успешных запросов). Если JSON отсутствует, content = None.
    :var message: Сообщение из ответа.
    """

    def __init__(self, response: httpx.Response):
        self.response = response
        self.http_code = response.status_code

        try:
            response_data = response.json()
            self.error_id = response_data.get(DataStruct.error_id)
            self.content = response_data.get(DataStruct.content)
            self.message = response_data.get(DataStruct.message)
        except (json.JSONDecodeError, AttributeError):
            self.error_id = ErrorCodes.server_error
            self.content = None
            self.message = 'No data in response'


class Request:
    """
    Запрос.

    :var path: URL-адрес, на который идёт запрос.
    :var method: HTTP-метод запроса.
    :var query_params: параметры запроса
    :var json: JSON, отправляемый в запросе.
    :var headers: заголовки.
    :cvar time: время создания запроса
    """

    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    ids = []

    def __init__(self, path: str, method: str, query_params: dict = None, json_: dict = None, headers: dict = None):
        self.path = path
        self.method = method
        self.query_params = query_params
        self.json = json_
        self.headers = headers

        self._time = datetime.datetime.now()

    @property
    def time(self) -> datetime:
        return self._time


if __name__ == '__main__':
    pass
