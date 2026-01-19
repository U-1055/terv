"""Слой API."""
import datetime
import logging

import httpx

import json
import time
import typing as tp
import asyncio
import threading

import client.src.requester.errors as err
from common.base import CommonStruct, ErrorCodes
from client.src.base import DataStructConst
from client.utils.timeout_list import TimeoutList


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
    :param timeout: минимальное время между двумя одинаковыми запросами (мс).
    :param request_limit: максимальное число записей (элементов в поле content) в одном запросе.
    """

    def __init__(self, server: str, common_data_struct: CommonStruct = CommonStruct, timeout: int = 100, request_limit: int = 100):
        self._server = server
        self._struct = common_data_struct
        self._timeout = timeout
        if self._timeout is None:
            self._timeout = 100
        self._request_limit = request_limit
        if self._request_limit is None:  # / 1000, т.к. TimeoutList принимает в секундах, а нам приходят миллисекунды
            self._request_limit = 100
        self._requests: TimeoutList[Request] = TimeoutList(self._timeout // 1000, max_length=100)

    def _prepare_response(self, response: 'ServerResponse', request: 'Request'):
        """Обрабатывает ответ: вызывает исключения, если запрос неудачный, передаёт ответ дальше, если успешный"""
        error_code = response.error_id
        message = response.message

        if error_code != ErrorCodes.ok.value:  # Вызов исключения по коду
            logging.warning(f'API error. Code: {error_code}. Error: {err.exceptions_error_ids.get(error_code)}. Request:'
                            f'{request}. Response: {response}.')
            exc = err.exceptions_error_ids.get(error_code)
            raise exc(message, request=request)

    def set_timeout(self, timeout: int):
        """Установить новый timeout (в мс)."""
        self._timeout = timeout
        self._requests.set_timeout(self._timeout // 1000)

    @property
    def timeout(self) -> int:
        return self._timeout

    def set_request_limit(self, request_limit: int):
        self._request_limit = request_limit

    @property
    def request_limit(self) -> int:
        return self._request_limit

    async def _choose_request_type(self, request: 'Request', limit: int | None) -> 'Response':
        try:
            if not limit:  # Если лимит не установлен
                response = await self._prepare_requests_sequence(request, limit)
            elif limit > self._request_limit:  # Если лимит больше максимального за запрос
                response = await self._prepare_requests_sequence(request, limit)
            else:
                response = await self._make_request(request)

            return response
        except err.APIError as e:
            raise e

    async def _prepare_requests_sequence(self, request: 'Request', limit: int | None):  # ToDo: а что делать, если в процессе отправки истечёт access?
        """
        Посылает запросы на URL переданного запроса, меняя их offset до тех пор, пока не будут получены все записи
        или не будет достигнут limit.
        Предназначен для запросов, в ответ на которые API отдаёт список записей. Для других запросов корректного
        результата не будет.

        :param limit: максимальное число записей, который могут быть получены от сервера.

        """

        request.set_limit(self._request_limit)  # Установка лимита

        if not request.offset:
            request.set_offset(0)
        offset = request.offset
        try:
            response = await self._make_request(request)  # Первый запрос
            content = response.content
        # Запрашиваем данные, пока не превысим лимит или не получим все данные (в этом случае придёт records_left = 0)
            while response.records_left and (not limit or limit and len(content) < limit):
                request.set_offset(offset + len(content))  # Прибавляем offset
                response = await self._make_request(request)
                if response.content:
                    content.extend(response.content)

            response = Response(request, content, response.records_left, 0)

            return response

        except err.APIError as e:
            raise e

    async def _make_request(self, request: 'Request') -> 'Response':

        if self._requests and self._requests[-1].path == request.path and self._requests[-1].method == request.method: #  Запросы одинаковы
            diff = request.time - self._requests[-1].time  # Разница во времени отправки
            if diff < datetime.timedelta(milliseconds=self._timeout):
                await asyncio.sleep(diff.microseconds * 1e6)  # Задержка до допустимого времени между запросами

        try:
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
                   raise err.RequesterError(f'Unknown method: {request.method}')
                self._requests.append(request)  # Добавляем запрос в список

            # Обработка запроса и его возврат в виде Response
            server_response = ServerResponse(result)
            self._prepare_response(server_response, request)

            return Response(request, server_response.content, server_response.records_left,
                            server_response.last_record_num)
        except err.APIError as e:  # Обработка ошибок API
            logging.warning(f'Excepted error {e} during making request {Request}')
            raise e
        except (httpx.ConnectError, httpx.ReadError, httpx.WriteError) as e:  # Обработка ошибок сети
            logging.warning(f'Excepted network connection error {e} during making request {Request}')
            raise err.get_network_error(e, request)


    @synchronized_request
    async def make_custom_request(self, request: 'Request') -> 'Response':
        try:
            response = await self._make_request(request)
            return response
        except err.APIError as e:
            raise e

    @synchronized_request
    async def register(self, login: str, password: str, email: str) -> 'Response':
        try:
            request = Request(f'{self._server}/register', Request.POST,
                              json_={
                self._struct.login: login,
                self._struct.password: password,
                self._struct.email: email
            })
            response = await self._make_request(request)
            return response
        except err.APIError as e:
            raise e

    @synchronized_request
    async def update_tokens(self, refresh_token: str) -> 'Response':
        try:
            request = Request(f'{self._server}/auth/refresh', Request.POST,
                              json_={self._struct.refresh_token: refresh_token})
            response = await self._make_request(request)
            return response
        except err.APIError as e:
            raise e

    @synchronized_request
    async def authorize(self, login: str, password: str) -> 'Response':
        try:
            request = Request(f'{self._server}/auth/login', Request.POST,
                              json_={self._struct.login: login, self._struct.password: password})
            response = await self._make_request(request)
            return response
        except err.APIError as e:
            raise e

    @synchronized_request
    async def get_user_info(self, access_token: str) -> 'Response':
        try:
            request = Request(f'{self._server}/users', Request.GET, headers={'Authorization': access_token})
            response = await self._make_request(request)
            return response
        except err.APIError as e:
            raise e

    @synchronized_request
    async def get_personal_tasks(self, user_id: int, access_token: str, task_ids: list[int] = None,
                                 limit: int = None, offset: int = None) -> 'Response':
        """Получает личные задачи (конкретную или по user_id)."""
        try:
            path = f'{self._server}/personal_tasks'
            request = Request(path, Request.GET, headers={'Authorization': access_token},
                              query_params={CommonStruct.limit: limit, CommonStruct.offset: offset})
            response = await self._choose_request_type(request, limit)

            return response
        except err.APIError as e:
            raise e

    @synchronized_request
    async def get_wf_tasks(self, tasks_ids: list[int], access_token: str, limit: int = None, offset: int = 0) -> 'Response':
        try:
            path = f'{self._server}/wf_tasks'
            request = Request(path, Request.GET, headers={'Authorization': access_token},
                              query_params={
                                  CommonStruct.limit: limit,
                                  CommonStruct.offset: offset
                              })
            response = await self._choose_request_type(request, limit)
            return response
        except err.APIError as e:
            raise e

    @synchronized_request
    async def retry(self, access_token: str, request: 'Request') -> 'Response':
        """
        Повторяет один из предыдущих запросов, предварительно меняя его access_token на переданный.
        :param access_token: access токен.
        :param request: запрос.
        """
        try:
            if request.headers.get('Authorization'):
                request.headers['Authorization'] = access_token

            response = await self._make_request(request)
            return response.content.get(self._struct.content)

        except err.APIError as e:
            raise e


class ServerResponse:
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
            self.error_id = response_data.get(CommonStruct.error_id)
            self.content = response_data.get(CommonStruct.content)
            self.message = response_data.get(CommonStruct.message)
            self.records_left = response_data.get(CommonStruct.records_left)
            self.last_record_num = response_data.get(CommonStruct.last_rec_num)
        except (json.JSONDecodeError, AttributeError):
            self.error_id = ErrorCodes.server_error
            self.content = None
            self.message = 'No data in response'
            self.records_left = None
            self.last_record_num = None


class Response:
    """
    Ответ Requester'a.
    :param request: запрос типа Request.
    :param content: содержимое (поле content) ответа API.
    :param records_left: число оставшихся записей (для запросов, в ответ на которые возвращается список записей).
    :param last_record_num: номер последней полученной записи
           (для запросов, в ответ на которые возвращается список записей).
    """

    def __init__(self, request: 'Request', content: tp.Any, records_left: int, last_record_num: int):
        self.request = request
        self.content = content
        self.records_left = records_left
        self.last_record_num = last_record_num

    def __str__(self):
        return str(self.__dict__)


class Request:  # ToDo: переделать в датаклассы
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

    def __init__(self, path: str, method: str, query_params: dict = None, json_: dict = None, headers: dict = None):
        self.path = path
        self.method = method
        self.query_params = query_params
        self.json = json_
        if headers:  # Проверка заголовков
            headers = {header: headers[header] for header in headers if headers[header]}
        self.headers = headers

        self._time = datetime.datetime.now()

    @property
    def time(self) -> datetime:
        return self._time

    @property
    def id(self) -> int:
        return self._id

    @property
    def limit(self) -> int | None:
        return self.query_params.get(CommonStruct.limit)

    def set_limit(self, limit: int):
        self.query_params[CommonStruct.limit] = limit

    @property
    def offset(self) -> int | None:
        return self.query_params.get(CommonStruct.offset)

    def set_offset(self, offset: int):
        self.query_params[CommonStruct.offset] = offset

    def __str__(self):
        return str(self.__dict__)


if __name__ == '__main__':
    pass

