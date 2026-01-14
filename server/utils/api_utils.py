from flask import Response, jsonify

import typing as tp

from common.base import CommonStruct, ErrorCodes


def form_response(http_code: int, message: str, content: tp.Any = None, error_id: int = ErrorCodes.ok) -> Response:
    response = {
        CommonStruct.message: message,
        CommonStruct.error_id: error_id
    }
    if content:
        response.update(content=content)
    result = jsonify(response)
    result.status_code = http_code
    return result

