import logging

import flask
from flask import Response, jsonify, Request
from sqlalchemy.exc import SQLAlchemyError

import typing as tp

from common.base import CommonStruct, ErrorCodes
from server.data_const import APIAnswers as APIAn


def form_response(http_code: int,
                  message: str,
                  content: tp.Any = None,
                  error_id: int = ErrorCodes.ok.value,
                  last_rec_num: int = None,
                  records_left: int = None
                  ) -> Response:
    """
    Формирует ответ API.

    :param http_code: HTTP-код статуса ответа.
    :param message: Сообщение в ответе.
    :param content: Содержимое ответа.
    :param error_id: ID ошибки.
    :param last_rec_num: Номер последней записи в БД (для GET-запросов).
    :param records_left: Осталось записей в БД (для GET-запросов).
    """

    response = {
        CommonStruct.message: message,
        CommonStruct.error_id: error_id
    }
    if content:
        response.update(content=content)
    if last_rec_num is not None:
        response.update(last_rec_num=last_rec_num)
    if records_left is not None:
        response.update(records_left=records_left)

    result = jsonify(response)
    result.status_code = http_code
    return result


def form_invalid_limit_response(endpoint: str):
    return form_response(400,
                         APIAn.invalid_data_error(CommonStruct.limit, endpoint, f'Incorrect limit'),
                         error_id=ErrorCodes.incorrect_limit.value
                         )


def form_invalid_offset_response(endpoint: str) -> flask.Response:
    return form_response(400,
                         APIAn.invalid_data_error(CommonStruct.limit, endpoint, f'Incorrect limit'),
                         error_id=ErrorCodes.incorrect_limit.value
                         )


def form_success_response(content: tp.Any = None) -> flask.Response:
    return form_response(200, 'OK', content)


def form_expired_access_response():
    return form_response(401, 'Expired access token', error_id=ErrorCodes.invalid_access.value)


def form_forbidden_response(resource: str, endpoint: str, role: str, permission: str):
    """Формирует ответ API об отсутствии доступа к ресурсу."""
    return form_response(403, f'Users with role {role} have not permission {permission} to execute'
                              f'operation with resource {resource}.')


def prepare_pagination_param(param: str) -> int:
    """
    Валидирует и приводит к требуемому виду параметры пагинации (limit и offset).
    Оба параметра: числа, >=0.
    """
    if param:
        param = int(param)

    else:
        pass


def check_list_is_digit(list_: list[str]) -> bool:
    """Проверяет, все ли элементы списка могут быть приведены к типу int."""
    for el in list_:
        if not el.isdigit():
            return False
    return True


def list_to_int(list_: list[str]) -> list[int]:
    """Приводит все элементы списка к типу int."""
    return [int(el) for el in list_]


def exceptions_handler(func: tp.Callable):
    """Обработчик исключений."""

    def prepare(request: flask.Request):
        try:
            return func(request)
        except Exception as e:
            logging.critical(f'Unknown error was excepted during preparing request: {request}.')
            return form_response(500, 'Unknown server error', error_id=ErrorCodes.server_error.value)

    return prepare


def get_request(func: tp.Callable):
    """
    Обработчик для функций, обрабатывающих GET-запросы к ресурсам. Валидирует параметры пагинации (limit и offset).
    """

    def prepare(request: flask.Request, *args):
        limit = request.args.get(CommonStruct.limit)
        offset = request.args.get(CommonStruct.offset)
        if limit:
            try:
                limit = int(limit)
            except ValueError:
                return form_invalid_limit_response(request.endpoint)
        else:
            limit = None

        if offset:
            try:
                offset = int(offset)
            except ValueError:
                return form_invalid_offset_response(request.endpoint)
        else:
            offset = None
        return func(request, *args, limit=limit, offset=offset)

    return prepare


def db_exceptions_handler(func: tp.Callable):
    """Передаёт вызывающей стороне все исключения БД, вызванные в декорированной функции."""

    def prepare(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            raise e

    return prepare

