import flask
from flask import Response, jsonify, Request
from sqlalchemy.exc import SQLAlchemyError

import datetime
import typing as tp
import functools

from common.base import CommonStruct, ErrorCodes
from common.logger import config_logger, SERVER
from server.api.base import LOG_DIR, LOGGING_LEVEL, MAX_FILE_SIZE, MAX_BACKUP_FILES
from server.data_const import APIAnswers as APIAn
import server.api.controllers.exceptions as controller_exc

logger = config_logger(__name__, SERVER, LOG_DIR, MAX_BACKUP_FILES, MAX_FILE_SIZE, LOGGING_LEVEL)


def form_response(http_code: int,
                  message: str,
                  content: tp.Any = None,
                  last_rec_num: int = None,
                  records_left: int = None,
                  error_id: int = ErrorCodes.ok.value,
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
        CommonStruct.message: message
    }
    if content:
        response.update(content=content)
    if last_rec_num is not None:
        response.update(last_rec_num=last_rec_num)
    if records_left is not None:
        response.update(records_left=records_left)
    if error_id != ErrorCodes.ok.value:
        response.update(error_id=error_id)

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


def form_get_success_response(content: tp.Any | None = None, last_rec_num: int | None = None,
                              records_left: int | None = None):
    """Формирует ответ на GET-запрос."""
    return form_response(200, "OK", content, last_rec_num, records_left)


def check_list_is_digit(list_: list[str]) -> bool:
    """Проверяет, все ли элементы списка могут быть приведены к типу int."""
    for el in list_:
        if not el.isdigit():
            return False
    return True


def list_to_int(list_: list[str], param: str, error_id: int) -> list[int]:
    """
    Приводит все элементы списка к типу int. Если элемент не приводится, выбрасывается исключение
    IncorrectParamsError.

    :param list_: Список для приведения.
    :param param: Название параметра в API.
    :param error_id: ID ошибки в случае, если элемент списка не приводится к int.

    """
    try:
        return [int(el) for el in list_]
    except ValueError as e:
        logger.exception(f'ValueError during converting list to int: {e}')
        raise controller_exc.IncorrectParamException(
            {
                param: {
                    controller_exc.VALUE: list_,
                    controller_exc.ERROR_ID: error_id,
                    controller_exc.MESSAGE: "This list contains params that can't be converted to int."
                }
            }
        )


def exceptions_handler(func: tp.Callable):
    """Обработчик исключений."""

    @functools.wraps(func)
    def prepare(request: flask.Request):
        try:
            return func(request)
        except controller_exc.IncorrectParamException as e:
            if len(e.params) == 1:
                param = list(e.params.keys())[0]
                error_id = int(e.params[param][controller_exc.ERROR_ID])
                status_code = 400
            else:
                error_id = ErrorCodes.server_error.value
                status_code = 500
            message = f'Incorrect params in request to endpoint {request.endpoint}. Params: {e.params}.'
            return form_response(status_code, message, error_id=error_id)

    return prepare


def get_request(func: tp.Callable):
    """
    Обработчик для функций, обрабатывающих GET-запросы к ресурсам. Валидирует параметры пагинации (limit,
    offset, require_last_num) и передаёт их в декорируемую функцию. Если происходит ошибка при валидации, возвращает
    соответствующий ответ API.
    """

    @functools.wraps(func)
    def prepare(request: flask.Request, *args, **kwargs):
        limit = request.args.get(CommonStruct.limit)
        offset = request.args.get(CommonStruct.offset)
        require_last_num = request.args.get(CommonStruct.require_last_num)

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
            offset = 0

        if require_last_num and require_last_num != '0' and require_last_num.lower() != 'false':
            require_last_num = True

        return func(request, *args, **kwargs, limit=limit, offset=offset, require_last_num=require_last_num)

    return prepare


def _convert_to_datetime_format(string: str, error_id: int, param: str, type_: tp.Type[datetime.date]) -> tp.Any:
    if type_ is datetime.datetime:
        using_format = CommonStruct.datetime_format
    else:
        using_format = CommonStruct.date_format

    try:
        result = datetime.datetime.strptime(string, using_format)
        if using_format == CommonStruct.date_format:
            result = result.date()
        return result
    except ValueError as e:
        logger.exception(f'ValueError during converting string to date: {e}')
        raise controller_exc.IncorrectParamException(
            {
                param: {
                    controller_exc.MESSAGE: f'This parameter is incorrect for date format:'
                                            f' {using_format}.',
                    controller_exc.VALUE: string, controller_exc.ERROR_ID: error_id
                }
            }
        )


def string_to_date(string: str, error_id: int, param: str) -> datetime.date:
    """
    Превращает строку в дату. Если строка невалидна для формата CommonStruct.date_format -
    выбрасывает IncorrectParamsError.

    :param string: Преобразуемая строка.
    :param error_id: ID ошибки, в случае, если строка невалидна.
    :param param: Название параметра, значение которого передаётся в string.

    """
    return _convert_to_datetime_format(string, error_id, param, datetime.date)


def string_to_datetime(string: str, error_id: int, param: str):
    """
    Превращает строку в datetime.datetime.
    Если строка невалидна для формата CommonStruct.datetime_format, выбрасывает IncorrectParamsError.

    :param string: Преобразуемая строка.
    :param error_id: ID ошибки, в случае, если строка невалидна.
    :param param: Название параметра, значение которого передаётся в string.

    """
    return _convert_to_datetime_format(string, error_id, param, datetime.datetime)


def string_to_int(value: str, param: str, error_id: int) -> int:
    """
    Превращает строку в число. Если строка невалидна, выбрасывает IncorrectParamsError.

    :param value: Строка.
    :param param: Название параметра в API.
    :param error_id: ID ошибки в случае, если строка невалидна.

    """
    try:
        return int(value)
    except (ValueError, TypeError) as e:
        logger.exception(f'ValueError during converting string to int: {e}')
        raise controller_exc.IncorrectParamException(
            {
                param: {
                    controller_exc.MESSAGE: f"This parameter is not valid int.",
                    controller_exc.VALUE: value,
                    controller_exc.ERROR_ID: error_id
                }
            }
        )


