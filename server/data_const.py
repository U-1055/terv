import datetime
import enum
import logging
import os
from pathlib import Path
import json

from common.base import CommonStruct

logging.basicConfig(level=logging.WARN)


class DataStruct:

    blacklist = 'blacklist'
    secret = 'secret'
    jwt_alg = 'HS256'
    access_token = 'access_token'
    refresh_token = 'refresh_token'

    # Поля конфига
    env = 'env'
    prod = 'prod'
    dev = 'dev'
    test = 'test'
    access_token_lifetime = 'access_token_lifetime'
    refresh_token_lifetime = 'refresh_token_lifetime'
    database_path = 'database_path'

    # Параметры конфига по умолчанию

    default_access_token_lifetime = datetime.timedelta(seconds=15 * 60)
    default_refresh_token_lifetime = datetime.timedelta(seconds=24 * 3600)
    default_database_path = 'sqlite:///../database/database'

    login = 'login'
    email = 'email'
    user_id = 'user_id'
    hashed_password = 'hashed_password'
    username = 'username'

    task = 'task'
    project = 'project'
    document = 'document'
    daily_event = 'daily_event'
    many_days_event = 'many_days_event'

    # Описания требований к параметрам (Возвращаются в ответах)
    login_conditions = f'The length of the login must be in range {CommonStruct.min_login_length}-{CommonStruct.max_login_length}'
    password_conditions = (f'Length of the password must be in range {CommonStruct.min_password_length}-{CommonStruct.max_password_length}.'
                           f'The password must include letters, numbers and other symbols.')


class DBStruct:
    """Поля из БД."""
    default_description = 'Описание отсутствует'
    default_role = 'Пользователь'
    creator_role = 'Владелец'


# Конфиг по умолчанию
default_config = {
    DataStruct.env: DataStruct.prod,
    DataStruct.access_token_lifetime: DataStruct.default_access_token_lifetime,
    DataStruct.refresh_token_lifetime: DataStruct.default_refresh_token_lifetime
}


class Permissions(enum.Enum):
    # Базовые доступы роли в Workspace
    del_wf = 'del_wf'
    del_project = 'del_project'
    create_event = 'create_event'
    del_event = 'del_event'
    edit_event = 'edit_event'
    create_task = 'create_task'
    del_task = 'del_task'
    edit_task = 'edit_task'
    complete_task = 'complete_task'
    invite = 'invite'
    kick = 'kick'
    create_doc = 'create_doc'
    dec_doc = 'del_doc'
    edit_doc = 'edit_doc'

    set_project = 'set_project'
    set_workspace = 'set_workspace'
    set_roles = 'set_roles'
    view_analytics = 'view_analytics'
    set_analytics = 'set_analytics'

    # Доступы просмотра конкретных ресурсов ()
    create = 'create'
    edit = 'edit'
    delete = 'delete'
    view = 'view'


class APIAnswers:

    no_login_message = 'There is no login in the token'
    unknown_credentials_message = 'Unknown login or password'

    @staticmethod
    def no_params_error(param: str, endpoint: str) -> str:
        return f'The endpoint {endpoint} expected parameter {param}, but it was not sent'

    @staticmethod
    def invalid_data_error(param: str, endpoint: str, message: str = '') -> str:
        return f'The endpoint {endpoint} received the invalid param {param}: {message}'

    @staticmethod
    def database_write_error(param: str, endpoint: str, message: str = '', database_error: str = '') -> str:
        return (f'The endpoint {endpoint} received invalid data in param {param} and cannot write to DB.'
                f'{message}. Database error: {database_error}.')


class Config:
    """
    Представление конфиг-файла config.json.

    Структура config-файла: {
        'env': str [prod, dev, test]
        'access_token_lifetime': int (seconds)
        'refresh_token_lifetime': int (seconds)
    }

    """

    def __init__(self, config_path: Path):
        self._config_path = config_path
        p = os.getcwd()
        try:
            with open(self._config_path, 'rb') as config:
                config_data = json.load(config)
                self._env = config_data.get(DataStruct.env)

                if not self._env:  # Окружение по умолчанию
                    logging.warning(
                        f'Incorrect param in config: {DataStruct.env} = {self._env}')
                    self._env = default_config[DataStruct.env]

                access_lifetime = str(config_data.get(DataStruct.access_token_lifetime))
                if access_lifetime and access_lifetime.isdigit():  # Время жизни access-токена по умолчанию
                    self._access_token_lifetime = datetime.timedelta(seconds=int(access_lifetime))
                else:
                    logging.warning(f'Incorrect param in config: {DataStruct.access_token_lifetime} = {access_lifetime}')
                    self._access_token_lifetime = DataStruct.default_access_token_lifetime

                refresh_lifetime = str(config_data.get(DataStruct.refresh_token_lifetime))
                if refresh_lifetime and refresh_lifetime.isdigit():  # Время жизни refresh-токена по умолчанию
                    self._refresh_token_lifetime = datetime.timedelta(seconds=int(refresh_lifetime))
                else:
                    logging.warning(f'Incorrect param in config: {DataStruct.refresh_token_lifetime} = {refresh_lifetime}')
                    self._refresh_token_lifetime = DataStruct.default_refresh_token_lifetime
            self._database_path = config_data.get(DataStruct.database_path)
            if not self._database_path:
                logging.warning(f'Incorrect param in config: {DataStruct.database_path} = {self._database_path}')
                self._database_path = DataStruct.default_database_path

        except (OSError, json.JSONDecodeError):
            self._env = default_config[DataStruct.env]
            self._refresh_token_lifetime = DataStruct.default_refresh_token_lifetime
            self._access_token_lifetime = DataStruct.default_access_token_lifetime
            self._database_path = DataStruct.default_database_path

    @property
    def env(self) -> str:
        return self._env

    @property
    def access_token_lifetime(self) -> datetime.timedelta:
        return self._access_token_lifetime

    @property
    def refresh_token_lifetime(self) -> datetime.timedelta:
        return self._refresh_token_lifetime

    @property
    def database_path(self) -> str:
        return self._database_path


if __name__ == '__main__':
    Config('config.json')
