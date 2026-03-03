from server.database.exceptions import BaseRepoException


def map_to_service_exception(exception: BaseRepoException):
    pass


class ServiceError(Exception):
    def __init__(self, message: str):
        self.message = message


class IncorrectParamError(ServiceError):
    def __init__(self, param: str, message: str):
        self.param = param
        self.message = message

