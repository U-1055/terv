import typing as tp

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from marshmallow.exceptions import MarshmallowError, ValidationError
from common.logger import config_logger, SERVER
from server.api.base import LOG_DIR, LOGGING_LEVEL, MAX_FILE_SIZE, MAX_BACKUP_FILES
from common_utils.text_prepare_utils import snake_to_camel_case

logger = config_logger(__name__, SERVER, LOG_DIR, MAX_BACKUP_FILES, MAX_FILE_SIZE, LOGGING_LEVEL)

NOT_UNIQUE_VALUE_MESSAGE = 'UNIQUE constraint failed'  # sqlalchemy.exc.IntegrityError
NO_VALUE = 'Missing data for required field'  # marshmallow.exceptions.ValidationError
UNKNOWN_FIELD = 'Unknown field'  # marshmallow.exceptions.ValidationError


def exc_mapped(func: tp.Callable) -> tp.Callable[[], Exception]:
    def prepare(*args, **kwargs) -> tp.Any:
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
            return NotUniqueValue(msg)
    else:
        logger.critical(f'There is no complimentary exceptions for: {exc}.')
        raise ValueError('Unknown Repo error.')


def map_marshmallow_exc_to_repo_exc(exc: MarshmallowError) -> 'BaseRepoException':
    if type(exc) is ValidationError:
        exc: ValidationError

        messages = exc.messages_dict
        no_value_params = []
        unknown_params = []
        for param in messages:
            if NO_VALUE in messages[param][0]:
                no_value_params.append(param)
            if UNKNOWN_FIELD in messages[param][0]:
                unknown_params.append(param)
        if not unknown_params:
            return NoRequiredParams(no_value_params)
        return UnknownParams(unknown_params)


class BaseRepoException(Exception):
    """Базовый класс ошибок слоя доступа к данным."""
    message: str

    def __str__(self):
        return f'RepositoryException - {self.__class__.__name__}: {self.message}'


class NotUniqueValue(BaseRepoException):
    """
    Соответствует ошибке, вызванной неуникальным значением.

    :param message: Сообщение sqlalchemy.exc.IntegrityError вида UNIQUE constraint failed: "<tablename>.<param>"

    :var entity: Сущность, с которой произошла ошибка.
    :var param: Параметр сущности, который вызвал ошибку.

    """

    def __init__(self, message: str):
        self.entity, self.param = self._prepare_msg(message)
        self.message = f'The param {self.param} of entity {self.entity} must be unique.'

    def _prepare_msg(self, message: str) -> tuple[str, str] | tuple[None, None]:
        spl_line = message.split(':')
        if len(spl_line) > 1:
            spl_line = spl_line[1].strip().split('.')
            if len(spl_line) == 2:
                spl_line[0] = snake_to_camel_case(spl_line[0], True)
                return tuple(spl_line)


class NoRequiredParams(BaseRepoException):
    """
    Исключение, соответствующее отсутствию обязательного параметра.

    :param params: Обязательные параметры, в которых нет данных.

    """

    def __init__(self, params: tp.Collection[str]):
        self.params = params
        self.message = f'There are null required params {','.join(self.params)}'


class UnknownParams(BaseRepoException):
    """
    Исключение, соответствующее неизвестному параметру.

    :param params: Неизвестные параметры.

    """
    def __init__(self, params: tp.Collection[str]):
        self.params = params
        self.message = f'There are unknown params {','.join(self.params)}'


if __name__ == '__main__':
    print(NotUniqueValue('UNIQUE constraint failed: user.username'))
