"""Слой API."""
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

    def __init__(self, server: str, common_data_struct: DataStruct = DataStruct):
        self._server = server
        self._struct = common_data_struct

    def _prepare_response(self, response: 'Response'):
        """Обрабатывает ответ: вызывает исключения, если запрос неудачный, передаёт ответ дальше, если успешный"""
        error_code = response.error_id
        message = response.message

        if error_code != ErrorCodes.ok:  # Вызов исключения по коду
            exc = err.exceptions_error_ids.get(error_code)
            raise exc(message)

    async def _get(self, path: str, query_params: dict = None, headers: dict = None) -> 'Response':  # Базовые методы запросов
        async with httpx.AsyncClient() as client:
            result = await client.get(path, headers=headers, params=query_params)

        try:
            return self._prepare_response(Response(result))
        except err.APIError as e:
            raise e

    async def _post(self, path: str, query_params: dict = None, headers: dict = None, json_: dict = None) -> 'Response':
        async with httpx.AsyncClient() as client:
            result = await client.post(path, json=json_, headers=headers, params=query_params)
        try:
            return self._prepare_response(Response(result))
        except err.APIError as e:
            raise e

    async def _delete(self, path: str, query_params: dict = None, headers: dict = None) -> 'Response':
        async with httpx.AsyncClient() as client:
            result = await client.delete(path, headers=headers, params=query_params)
        try:
            return self._prepare_response(Response(result))
        except err.APIError as e:
            raise e

    async def _put(self, path: str, query_params: dict = None, headers: dict = None, json_: dict = None) -> 'Response':
        async with httpx.AsyncClient() as client:
            result = await client.put(path, json=json_, headers=headers, params=query_params)
        try:
            return self._prepare_response(Response(result))
        except err.APIError as e:
            raise e

    @synchronized_request
    async def register(self, login: str, password: str, email: str):
        try:
            response = await self._post(
                f'{self._server}/register',
                json_={
                    self._struct.login: login,
                    self._struct.password: password,
                    self._struct.email: email
                }
            )
            return response.content.get(self._struct.content)
        except err.APIError as e:
            raise e

    @synchronized_request
    async def update_tokens(self, refresh_token: str) -> dict:
        try:
            response = await self._post(
                f'{self._server}/auth/refresh',
                json_={self._struct.refresh_token: refresh_token}
            )
            return response.content.get(self._struct.refresh_token)
        except err.APIError as e:
            raise e

    @synchronized_request
    async def authorize(self, login: str, password: str) -> dict:
        try:
            response = await self._post(
                f'{self._server}/auth/login',
                json_={self._struct.login: login, self._struct.password: password}
            )
            return response.content.get(self._struct.content)
        except err.APIError as e:
            raise e

    @synchronized_request
    async def get_user_info(self, access_token: str, ):
        try:
            response = await self._get(f'{self._server}/users', headers={'Authorization': access_token})
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
            response = await self._get(path, headers={'Authorization': access_token})
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


if __name__ == '__main__':
    pass
