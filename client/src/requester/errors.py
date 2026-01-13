from common.base import ErrorCodes
import typing as tp

Request = tp.Any
if tp.TYPE_CHECKING:
    from client.src.requester.requester import Request


class APIError(BaseException):  # Ошибка, возвращённая API
    """
    Ошибка API.
    :param request: запрос, при котором произошла ошибка.
    """
    def __init__(self, message: str, request: Request):
        self.request = request


class RequesterError(BaseException):  # Ошибка внутри Requester'а
    pass


class NoLastRequest(RequesterError):  # Не было запросов
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

# Соответствие между кодами ошибок и исключениями


exceptions_error_ids = {
    ErrorCodes.server_error: ServerError,
    ErrorCodes.no_email: NoEmail,
    ErrorCodes.no_login: NoLogin,
    ErrorCodes.no_password: NoPassword,
    ErrorCodes.invalid_email: IncorrectEmail,
    ErrorCodes.invalid_login: IncorrectLogin,
    ErrorCodes.invalid_credentials: UnknownCredentials,
    ErrorCodes.invalid_password: IncorrectPassword,
    ErrorCodes.invalid_refresh: ExpiredRefreshToken,
    ErrorCodes.no_refresh: ExpiredRefreshToken,  # Для токенов вызывается одно и то же исключение, если токена нет и если токен просрочен
    ErrorCodes.no_access: ExpiredAccessToken,
    ErrorCodes.invalid_access: ExpiredAccessToken,
    ErrorCodes.no_tokens: NoTokens,
    ErrorCodes.existing_email: EmailAlreadyExists,
    ErrorCodes.existing_login: LoginAlreadyExists
}




