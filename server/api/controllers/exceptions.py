"""Исключения слоя контроллеров"""
import typing as tp

import server.database.exceptions as repo_exc


VALUE = 'value'
MESSAGE = 'message'


class BaseControllerException(Exception):
    """Базовое исключение слоя контроллеров."""

    def __init__(self, params: dict[str, dict[str, str | tp.Any]]):
        self.params = params
        self.message = f'Incorrect params: {self.params}'

    @staticmethod
    def get_exception(params: dict[str, tp.Any]) -> 'IncorrectParamException':
        return IncorrectParamException(params)


class IncorrectParamException(BaseControllerException):
    """Исключение, соответствующее неверному параметру в запросе."""


def map_repo_to_controller_exc(exc: repo_exc.BaseRepoException, param_values: dict[str, tp.Any]) -> BaseControllerException:
    type_ = type(exc)
    res_params: dict[str, dict[str, str | tp.Any]] = {}

    if type_ is repo_exc.DataIntegrityError:
        exc: repo_exc.DataIntegrityError
        for param in param_values:
            if param in exc.data:
                res_params[param] = {VALUE: param_values[param], MESSAGE: exc.data[param]}
        return IncorrectParamException(res_params)
    elif type_ is repo_exc.NotUniqueValue:
        exc: repo_exc.NotUniqueValue
        res_params = {exc.param: {VALUE: param_values.get(exc.param), MESSAGE: exc.message}}
        return IncorrectParamException(res_params)
    elif type_ is repo_exc.IncorrectLinkError:
        pass


def map_service_to_controller_exc():
    pass
