from flask import Response, jsonify, Request

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


def prepare_limit_offset(limit: str, offset: str, request: Request) -> Response | None:
    """Обрабатывает параметры limit и offset. Возвращает ответ API, если есть ошибка, None - если нет ошибки."""
    if limit and (not limit.isdigit() or int(limit) < 0):
        return form_response(400,
                             APIAn.invalid_data_error(CommonStruct.limit, request.endpoint, f'Incorrect limit'),
                             error_id=ErrorCodes.incorrect_limit.value
                             )
    if offset and (not offset.isdigit() or int(offset) < 0):
        return form_response(400,
                             APIAn.invalid_data_error(CommonStruct.offset, request.endpoint, 'Incorrect offset'),
                             error_id=ErrorCodes.incorrect_offset.value
                             )


def check_list_is_digit(list_: list[str]) -> bool:
    """Проверяет, все ли элементы списка могут быть приведены к типу int."""
    for el in list_:
        if not el.isdigit():
            return False
    return True


def list_to_int(list_: list[str]) -> list[int]:
    """Приводит все элементы списка к типу int."""
    return [int(el) for el in list_]