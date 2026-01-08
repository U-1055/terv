import datetime
import enum


class DataStruct:

    date_format = '%d.%m.%Y'
    time_format = '%H:%M:%S'
    datetime_format = f'{date_format}-{time_format}'
    blacklist = 'blacklist'
    secret = 'secret'
    access = 'access'
    refresh = 'refresh'
    jwt_alg = 'HS256'
    access_token_lifetime = datetime.timedelta(minutes=15)
    refresh_token_lifetime = datetime.timedelta(hours=24)

    login = 'login'
    email = 'email'
    hashed_password = 'hashed_password'
    username = 'username'

    task = 'task'
    project = 'project'
    document = 'document'
    daily_event = 'daily_event'
    many_days_event = 'many_days_event'


class Permissions(enum.Enum):
    # Базовые доступы роли в Workflow
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
    set_workflow = 'set_workflow'
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
