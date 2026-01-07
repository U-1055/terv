

class APIError(BaseException):
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

