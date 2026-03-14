"""Обработчики данных из запроса."""
import datetime
import re
import typing as tp

from server.utils.api_utils import list_to_int, string_to_int, string_to_date, string_to_datetime
from server.api.controllers.exceptions import IncorrectParamException, VALUE, MESSAGE, ERROR_ID


class BaseParam:
    """
    Обработчик параметра запроса. Если параметр пуст, преобразует его
    в None. Если параметр есть и невалиден, выбрасывает соответствующее исключение контроллера.

    :param param: Название параметра запроса.
    :param value: Значение параметра.
    :param error_id: ID ошибки, соответствующей невалидному значению параметра.

    :var value: Преобразованное значение параметра.

    """

    def __init__(self, param: str, value: tp.Any, error_id: int | None = None):
        self.param = param
        self.error_id = error_id
        self.value = self._validate(value)

    def __str__(self):
        return f'{self.__class__.__name__} parameter: {self.value}.'

    def _validate(self, value: tp.Any) -> tp.Any | None:
        pass


class Int(BaseParam):
    """
    Обработчик целочисленного параметра запроса. Принимает в __init__ строковый параметр и пытается
    превратить его в целочисленный, при ошибке возвращает исключение контроллеров. Если параметр пуст, преобразует его
    в None.

    :param param: Название параметра запроса.
    :param value: Значение параметра.
    :param error_id: ID ошибки, соответствующей невалидному значению параметра.

    :var value: Преобразованное значение параметра.

    """

    def __init__(self, param: str, value: str, error_id: int | None = None):
        super().__init__(param, value, error_id)

    def _validate(self, value: str) -> int | None:
        if value:
            return string_to_int(value, self.param, self.error_id)


class IntList(BaseParam):
    """
    Обработчик списка целочисленных значений. Принимает в __init__ список строковых значений и пытается
    преобразовать его в список целочисленных, при ошибке возвращает исключение контроллеров. Список вида ['']
    преобразует в None (Такой список в Flask соответствует пустому параметру). Если параметр пуст, преобразует его
    в None.

    :param param: Название параметра запроса.
    :param value: Значение параметра.
    :param error_id: ID ошибки, соответствующей невалидному значению параметра.

    :var value: Преобразованное значение параметра.

    """

    def __init__(self, param: str, value: list[str], error_id: int | None = None):
        super().__init__(param, value, error_id)

    def _validate(self, value: list[str]) -> list[int] | None:
        if value and value[0]:
            return list_to_int(value, self.param, self.error_id)


class Date(BaseParam):
    """
    Обработчик даты. Если параметр пуст, преобразует его
    в None.

    :param param: Название параметра запроса.
    :param value: Значение параметра.
    :param error_id: ID ошибки, соответствующей невалидному значению параметра.

    :var value: Преобразованное значение параметра.

    """

    def __init__(self, param: str, value: str, error_id: int | None = None):
        super().__init__(param, value, error_id)

    def _validate(self, value: str) -> datetime.date | None:
        if value:
            return string_to_date(value, self.error_id, self.param)


class DateTime(BaseParam):
    """
    Обработчик даты и времени. Если параметр пуст, преобразует его
    в None.

    :param param: Название параметра запроса.
    :param value: Значение параметра.
    :param error_id: ID ошибки, соответствующей невалидному значению параметра.

    :var value: Преобразованное значение параметра.

    """

    def __init__(self, param: str, value: str, error_id: int | None = None):
        super().__init__(param, value, error_id)

    def _validate(self, value: str) -> datetime.datetime | None:
        if value:
            return string_to_datetime(value, self.error_id, self.param)


class Bool(BaseParam):
    """
    Обработчик булевого значения. Если входное значение не равно 0 или false (без учёта регистра),
    то оно считается истинным. Если параметр пуст, преобразует его
    в None.

    :param param: Название параметра запроса.
    :param value: Значение параметра.
    :param error_id: ID ошибки, соответствующей невалидному значению параметра.

    :var value: Преобразованное значение параметра.

    """

    def __init__(self, param: str, value: str, error_id: int | None = None):
        super().__init__(param, value, error_id)

    def _validate(self, value: str) -> bool | None:
        if value:
            return True if value != '0' and value.lower() != 'false' else False


class String(BaseParam):
    """
    Обработчик строки. Проверяет, равна ли строка одному из переданных значений и соответствует ли она регулярному
    выражению. В случае несоответствия выбрасывает исключение контроллера.

    :param param: Название параметра запроса.
    :param value: Значение параметра.
    :param error_id: ID ошибки, соответствующей невалидному значению параметра.

    :var value: Значение параметра.

    """

    # Условия валидации строки
    AND = 'and'
    OR = 'or'

    def __init__(self, param: str, value: str, error_id: int | None = None, allowed: tp.Sequence | None = None,
                 regexp: str = None, condition: str = OR):
        self._allowed = allowed
        self._regexp = regexp
        self._condition = condition
        super().__init__(param, value, error_id)

    def _validate(self, value: str) -> str:
        is_valid_for_regexp, is_valid_value = True, True
        if self._regexp:
            is_valid_for_regexp = re.match(self._regexp, self.value)
        if self._allowed:
            is_valid_value = self.value in self._allowed
        if self._condition == self.AND:
            if not is_valid_value or not is_valid_for_regexp:
                raise self._form_exc(value)
        if self._condition == self.OR:
            if not is_valid_value and not is_valid_for_regexp:
                raise self._form_exc(value)

        return value

    def _form_exc(self, value: str) -> IncorrectParamException:

        if self._regexp and self._allowed:
            message = (f'This value must be correct for regexp {self._regexp} {self._condition} be contained in '
                       f'{self._allowed}')
        elif self._regexp:
            message = f'This value must be correct for regexp {self._regexp}'
        elif self._allowed:
            message = f'This value must be contained in {self._allowed}'
        else:
            message = ''

        return IncorrectParamException({self.param: {VALUE: value, MESSAGE: message, ERROR_ID: self.error_id}})
