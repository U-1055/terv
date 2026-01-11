"""Слой API."""
import json

import httpx

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

    async def _get(self, path: str, query_params: dict = None, headers: dict = None) -> 'Response':  # Базовые методы запросов
        async with httpx.AsyncClient() as client:
            result = await client.get(path, headers=headers, params=query_params)
        return Response(result)

    async def _post(self, path: str, query_params: dict = None, headers: dict = None, json_: dict = None) -> 'Response':
        async with httpx.AsyncClient() as client:
            result = await client.post(path, json=json, headers=headers, params=query_params)
        return Response(result)

    async def _delete(self, path: str, query_params: dict = None, headers: dict = None) -> 'Response':
        async with httpx.AsyncClient() as client:
            result = await client.delete(path, headers=headers, params=query_params)
        return Response(result)  # ToDo: переписать запросы с новыми методами

    async def _put(self, path: str, query_params: dict = None, headers: dict = None, json_: dict = None) -> 'Response':
        async with httpx.AsyncClient() as client:
            result = await client.put(path, json=json, headers=headers, params=query_params)
        return Response(result)

    @synchronized_request
    async def register(self, login: str, password: str, email: str):
        async with httpx.AsyncClient() as client:
            result = await client.post(f'{self._server}/register', json={self._struct.login: login, self._struct.password: password, self._struct.email: email})
        error_code = result.json().get(self._struct.error_id)
        message = result.json().get(self._struct.message)

        if error_code != ErrorCodes.ok:  # Вызов исключения по коду
            exc = err.exceptions_error_ids.get(error_code)
            raise exc(message)

        return result.json().get(self._struct.content)

    @synchronized_request
    async def update_tokens(self, refresh_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            result = await client.post(f'{self._server}/auth/refresh', json={self._struct.refresh_token: refresh_token})

        error_code = result.json().get(self._struct.error_id)
        message = result.json().get(self._struct.message)

        if error_code != ErrorCodes.ok:  # Вызов исключения по коду
            exc = err.exceptions_error_ids.get(error_code)
            raise exc(message)

        return result.json().get(self._struct.refresh_token)

    @synchronized_request
    async def authorize(self, login: str, password: str) -> dict:
        async with httpx.AsyncClient() as client:
            result = await client.post(f'{self._server}/auth/login', json={self._struct.login: login, self._struct.password: password})

        if result.status_code == 400:
            raise err.UnknownCredentials

        return result.json().get(self._struct.content)

    @synchronized_request
    async def get_user_info(self, access_token: str):
        async with httpx.AsyncClient() as client:
            result = await client.get(f'{self._server}/users', headers={'Authorization': access_token})

        if result.status_code == 401:
            raise err.ExpiredAccessToken
        if result.status_code == 500:
            raise err.ServerError

        return result.json().get(self._struct.content)

    @synchronized_request
    async def get_personal_tasks(self, user_id: int, access_token: str):
        async with httpx.AsyncClient() as client:
            result = await client.get(f'{self._server}/personal_tasks')

        if result.status_code == 401:
            raise err.ExpiredAccessToken
        if result.status_code == 500:
            raise err.ServerError

        return result.json().get(self._struct.content)


class Response:
    """
    Ответ API.

    :var response: объект httpx.Response.
    :var http_code: код статуса HTTP.
    :var error_id: ID ошибки. Если JSON в ответе отсутствует, error_id = 500 Server Error.
    :var content: содержимое ответа (только для успешных запросов). Если JSON отсутствует, content = None.
    :var message: сообщение из ответа.
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
