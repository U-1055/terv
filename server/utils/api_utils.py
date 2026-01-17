from flask import Response, jsonify

import typing as tp

from common.base import CommonStruct, ErrorCodes


def form_response(http_code: int, message: str, content: tp.Any = None, error_id: int = ErrorCodes.ok.value, last_rec_num: int = None) -> Response:
    """
    Формирует ответ API.

    :param http_code: HTTP-код статуса ответа.
    :param message: Сообщение в ответе.
    :param content: Содержимое ответа.
    :param error_id: ID ошибки.
    :param last_rec_num: Номер последней записи в БД (для GET-запросов).

    """

    response = {
        CommonStruct.message: message,
        CommonStruct.error_id: error_id
    }
    if content:
        response.update(content=content)
    if last_rec_num:
        response.update(last_rec_num=last_rec_num)

    result = jsonify(response)
    result.status_code = http_code
    return result

