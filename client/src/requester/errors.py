import httpx

from common.base import ErrorCodes
import typing as tp


def get_network_error(error_type: httpx.NetworkError, request) -> 'NetworkTimeoutError':
    if type(error_type) == httpx.ConnectError:
        return ConnectTimeoutError('Network error', request)
    elif type(error_type) == httpx.ReadError:
        return ReadTimeoutError('Network error', request)
    elif type(error_type) == httpx.WriteError:
        return WriteTimeoutError('Network error', request)


Request = tp.Any
if tp.TYPE_CHECKING:
    from client.src.requester.requester import Request


class APIError(Exception):  # Ошибка, возвращённая API
    """
    Ошибка API.
    :param request: запрос, при котором произошла ошибка.
    """
    def __init__(self, message: str, request: Request):
        self.request = request


class NetworkTimeoutError(APIError):  # Ошибка сети
    pass


class ReadTimeoutError(NetworkTimeoutError):  # Не удалось получить данных с сервера
    pass


class ConnectTimeoutError(NetworkTimeoutError):  # Не удалось установить соединение
    pass


class WriteTimeoutError(NetworkTimeoutError):   # Не удалось отправить запрос
    pass


class RequesterError(Exception):  # Ошибка внутри Requester'а
    pass


class NoLastRequest(RequesterError):  # Не было запросов
    pass


class RequestError(Exception):  # Ошибка при обращении к объекту запроса
    pass


class NotFinishedError(RequestError):  # Запрос ещё не завершен
    pass


class ExpiredAccessToken(APIError):  # Просроченный access-токен
    pass


class ExpiredRefreshToken(APIError):  # Просроченный refresh-токен
    pass


class UnknownCredentials(APIError):  # Неверные учётные данные
    pass


class IncorrectParamsError(APIError):
    pass


class IncorrectEmail(IncorrectParamsError):  # Некорректный email (вызывается при регистрации)
    pass


class EmailAlreadyExists(IncorrectParamsError):  # Email уже существует (вызывается при регистрации)
    pass


class IncorrectPassword(IncorrectParamsError):  # (вызывается при регистрации)
    pass


class IncorrectLogin(IncorrectParamsError):  # (вызывается при регистрации)
    pass


class LoginAlreadyExists(IncorrectParamsError):  # Login уже существует (вызывается при регистрации)
    pass


class ServerError(APIError):
    pass


class NoLogin(IncorrectParamsError):
    pass


class NoPassword(IncorrectParamsError):
    pass


class NoEmail(IncorrectParamsError):
    pass


class NoTokens(IncorrectParamsError):
    pass


class ForbiddenAccess(APIError):
    pass


class ForbiddenAccessToPersonalObject(ForbiddenAccess):
    pass


# Соответствие между кодами ошибок и исключениями


exceptions_error_ids = {
    ErrorCodes.server_error.value: ServerError,
    ErrorCodes.no_email.value: NoEmail,
    ErrorCodes.no_login.value: NoLogin,
    ErrorCodes.no_password.value: NoPassword,
    ErrorCodes.invalid_email.value: IncorrectEmail,
    ErrorCodes.invalid_login.value: IncorrectLogin,
    ErrorCodes.invalid_credentials.value: UnknownCredentials,
    ErrorCodes.invalid_password.value: IncorrectPassword,
    ErrorCodes.invalid_refresh.value: ExpiredRefreshToken,
    ErrorCodes.no_refresh.value: ExpiredRefreshToken,  # Для токенов вызывается одно и то же исключение, если токена нет и если токен просрочен
    ErrorCodes.no_access.value: ExpiredAccessToken,
    ErrorCodes.invalid_access.value: ExpiredAccessToken,
    ErrorCodes.no_tokens.value: NoTokens,
    ErrorCodes.existing_email.value: EmailAlreadyExists,
    ErrorCodes.existing_login.value: LoginAlreadyExists,
    ErrorCodes.forbidden_access_to_personal_object: ForbiddenAccessToPersonalObject
}
