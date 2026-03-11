import typing as tp

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from marshmallow.exceptions import MarshmallowError, ValidationError
from common.logger import config_logger, SERVER
from server.api.base import LOG_DIR, LOGGING_LEVEL, MAX_FILE_SIZE, MAX_BACKUP_FILES
from common_utils.text_prepare_utils import snake_to_camel_case
from functools import wraps


logger = config_logger(__name__, SERVER, LOG_DIR, MAX_BACKUP_FILES, MAX_FILE_SIZE, LOGGING_LEVEL)

NOT_UNIQUE_VALUE_MESSAGE = 'UNIQUE constraint failed'  # sqlalchemy.exc.IntegrityError
NO_VALUE = 'Missing data for required field'  # marshmallow.exceptions.ValidationError
UNKNOWN_FIELD = 'Unknown field'  # marshmallow.exceptions.ValidationError
UNKNOWN_LINK = 'FOREIGN KEY constraint failed'  # sqlalchemy.exc.IntegrityError


P = tp.ParamSpec('P')
T = tp.TypeVar('T')


def exc_mapped(func: tp.Callable[P, T]) -> tp.Callable[P, T]:
    @wraps(func)
    def prepare(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            exc_ = map_sqlalchemy_exc_to_repo_exc(e)
            logger.exception(f'An SQLAlchemyError caught: {e}')
            raise exc_
        except MarshmallowError as e:
            exc_ = map_marshmallow_exc_to_repo_exc(e)
            logger.exception(f'An MarshmallowError caught: {e}')
            raise exc_

    return prepare


def map_sqlalchemy_exc_to_repo_exc(exc: SQLAlchemyError) -> 'BaseRepoException':
    if type(exc) is IntegrityError:
        exc: IntegrityError
        msg = exc.orig.args[0]
        if NOT_UNIQUE_VALUE_MESSAGE in msg:
            return NotUniqueValue(msg, exc)
        if UNKNOWN_LINK in msg:
            return IncorrectLinkError(exc)

    else:
        logger.critical(f'There are no complimentary exceptions for: {exc}.')
        return UnknownRepoException(exc)


def map_marshmallow_exc_to_repo_exc(exc: MarshmallowError) -> 'BaseRepoException':
    if type(exc) is ValidationError:
        exc: ValidationError
        messages = exc.messages_dict
        return DataIntegrityError(messages, exc)

    else:  # Для всех остальных ошибок исключения не предусмотрено
        logger.critical(f'There are no complimentary exceptions for: {exc}')
        return UnknownRepoException(exc)


class BaseRepoException(Exception):
    """Базовый класс ошибок слоя доступа к данным."""
    message: str
    orig: Exception

    def __init__(self, orig: Exception | None):
        self.orig = orig

    @staticmethod
    def get_no_required_param_error(param: str):
        exc = DataIntegrityError({param: NO_VALUE}, None)
        return exc

    def __str__(self):
        return f'RepositoryException - {self.__class__.__name__}: {self.message}'


class UnknownRepoException(BaseRepoException):
    """Неизвестное исключение слоя доступа к данным."""

    def __init__(self, exc: Exception):
        self.orig = exc
        self.message = f'{self.orig.__class__.__name__} - {exc.args[0]}'


class NotUniqueValue(BaseRepoException):
    """
    Соответствует ошибке, вызванной неуникальным значением.

    :param message: Сообщение sqlalchemy.exc.IntegrityError вида UNIQUE constraint failed: "<tablename>.<param>"

    :var entity: Сущность, с которой произошла ошибка.
    :var param: Параметр сущности, который вызвал ошибку.

    """

    def __init__(self, message: str, orig: Exception | None):
        super().__init__(orig)
        self.entity, self.param = self._prepare_msg(message)
        self.message = f'The param {self.param} of entity {self.entity} must be unique.'

    def _prepare_msg(self, message: str) -> tuple[str, str] | tuple[None, None]:
        spl_line = message.split(':')
        if len(spl_line) > 1:
            spl_line = spl_line[1].strip().split('.')
            if len(spl_line) == 2:
                spl_line[0] = snake_to_camel_case(spl_line[0], True)
                return tuple(spl_line)


class DataIntegrityError(BaseRepoException):
    """
    Исключение, выбрасываемое при нарушении целостности данных в БД: неверный тип данных, нет нужного параметра,
    есть неизвестный параметр. Соответствует Marshmallow ValidationError.

    :var data: Информация об ошибке в формате {<Параметр>: <Описание ошибки>}.

    """

    def __init__(self, data: dict, orig: Exception | None):
        super().__init__(orig)
        self.data = self._prepare_data(data)
        self.message = f'Data integrity errors: {str(data)}'

    def _prepare_data(self, data: dict) -> dict:
        """Словарь в ValidationError вида: {<key>: [<error_info>]} переделывается в {<key>: <error_info>}."""
        return {key: data[key][0] for key in data}


class IncorrectLinkError(BaseRepoException):
    """
    Исключение, выбрасываемое при ссылке на несуществующий объект. Соответствует sqlalchemy.exc.IntegrityError
    "FOREIGN KEY constraint failed".
    """

    def __init__(self, orig: Exception | None):
        super().__init__(orig)
        self.message = 'There is link to non-existent object.'


if __name__ == '__main__':
    @exc_mapped
    def func_(sth: str):
        """Docs."""

    print(func_.__doc__)
    print(func_.__name__)
