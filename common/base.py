"""Общие константы, используемые и клиентом и сервером. (Названия параметров, элементов ответа, требования к данным)."""


class DataStruct:

    login = 'login'
    password = 'password'
    email = 'email'
    access_token = 'access_token'
    refresh_token = 'refresh_token'
    content = 'content'
    status_code = 'status_code'
    logins = 'logins'
    tokens = 'tokens'

    max_login_length = 25
    min_login_length = 5

    max_password_length = 50
    min_password_length = 10


def check_password(password: str) -> bool:
    """Проверяет пароль на соответствие требованиям: длине (10-50), сложности (наличие букв, цифр, символов)."""
    is_chars = any([char.isalpha() for char in password])
    is_digits = any([char.isdigit() for char in password])
    is_other_symbols = any([not char.isdigit() and not char.isalpha() for char in password])

    return DataStruct.min_password_length <= len(password) <= DataStruct.max_password_length and is_chars and is_digits and is_other_symbols


if __name__ == '__main__':
    pass
