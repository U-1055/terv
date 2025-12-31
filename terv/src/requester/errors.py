

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


class IncorrectEmail(IncorrectParamsError):
    pass


class IncorrectPassword(IncorrectParamsError):
    pass


class IncorrectLogin(IncorrectParamsError):
    pass


class ServerError(APIError):
    pass

