"""Общие константы, используемые и клиентом и сервером. (Названия параметров, элементов ответа, требования к данным)."""
import enum


class CommonStruct:
    """Названия параметров запросов и ответов API и требования к данным"""

    login = 'login'
    password = 'password'
    email = 'email'
    access_token = 'access_token'
    refresh_token = 'refresh_token'
    content = 'content'
    status_code = 'status_code'
    error_id = 'error_id'
    message = 'message'
    logins = 'logins'
    tokens = 'tokens'

    max_login_length = 25
    min_login_length = 5

    max_password_length = 50
    min_password_length = 10


class ErrorCodes(enum.Enum):
    """
    Конкретные коды ошибок (error ids).

    Префиксы ошибок:
    no - данные отсутствуют
    invalid - данные не соответствуют требованиям
    existing - (для идентификаторов) уже есть объект с таким идентификатором

    """
    ok = 200
    server_error = 500

    no_email = 0
    invalid_email = 1
    no_password = 2
    invalid_password = 3
    no_login = 4
    invalid_login = 5

    existing_login = 6
    existing_email = 7

    invalid_credentials = 8
    invalid_refresh = 9
    invalid_access = 10
    no_access = 11
    no_refresh = 12

    no_tokens = 13


def check_password(password: str) -> bool:
    """Проверяет пароль на соответствие требованиям: длине (10-50), сложности (наличие букв, цифр, символов)."""
    is_chars = any([char.isalpha() for char in password])
    is_digits = any([char.isdigit() for char in password])
    is_other_symbols = any([not char.isdigit() and not char.isalpha() for char in password])

    return CommonStruct.min_password_length <= len(password) <= CommonStruct.max_password_length and is_chars and is_digits and is_other_symbols


if __name__ == '__main__':
    pass
