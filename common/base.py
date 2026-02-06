"""Общие константы, используемые и клиентом и сервером. (Названия параметров, элементов ответа, требования к данным)."""
import enum
import datetime


class CommonStruct:
    """Названия параметров запросов и ответов API и требования к данным"""

    login = 'login'
    password = 'password'
    email = 'email'
    access_token = 'access_token'
    refresh_token = 'refresh_token'
    content = 'content'
    status_code = 'status_code'
    error_id = 'error_id'
    message = 'message'
    logins = 'logins'
    tokens = 'tokens'
    ids = 'ids'
    users = 'users'
    require_last_num = 'require_last_num'
    wf_tasks_ids = 'wf_tasks_ids'
    wf_tasks = 'wf_tasks'
    personal_tasks = 'personal_tasks'
    creator_id = 'creator_id'
    executor_id = 'executor_id'
    workflow_id = 'workflow_id'
    date = 'date'
    task_status = 'task_status'

    wf_daily_events = 'wf_daily_events'
    wf_many_days_events = 'wf_many_days_events'
    personal_daily_events = 'personal_daily_events'
    personal_many_days_events = 'personal_many_days_events'
    user_id = 'user_id'

    limit = 'limit'
    offset = 'offset'
    last_rec_num = 'last_rec_num'
    records_left = 'records_left'

    max_login_length = 25
    min_login_length = 5

    max_password_length = 50
    min_password_length = 10
    'YYYY-MM-DDTHH: MM:SS.mmmmmm'
    date_format = '%Y-%m-%d'
    time_format = '%H:%M:%S'
    datetime_format = f'{date_format}T{time_format}'
    max_name_length = 30  # Максимальная длина названий объектов
    max_description_length = 1000  # Максимальная длина описаний объектов


class TasksStatuses:
    """Статусы задач."""
    completed = 'completed'
    in_progress = 'in_progress'
    standing_by = 'standing_by'


class DBFields:
    """Названия полей таблиц БД."""
    # Base's fields
    created_at = 'created_at'
    updated_at = 'updated_at'

    # User's fields
    id = 'id'
    username = 'username'
    email = 'email'
    hashed_password = 'hashed_password'
    created_workflows = 'created_workflows'
    created_projects = 'created_projects'
    linked_workflows = 'linked_workflows'
    linked_projects = 'linked_projects'
    created_wf_tasks = 'created_wf_tasks'
    assigned_to_user_tasks = 'assigned_to_user_tasks'
    assigned_by_user_tasks = 'assigned_by_user_tasks'
    responsibility_tasks = 'responsibility_tasks'
    created_personal_tasks = 'created_personal_tasks'
    roles = 'roles'
    created_wf_documents = 'created_wf_documents'
    created_wf_daily_events = 'created_wf_daily_events'
    created_wf_many_days_events = 'created_wf_many_days_events'
    notified_daily_events = 'notified_daily_events'
    notified_many_days_events = 'notified_many_days_events'
    work_directions = 'work_directions'
    personal_daily_events = 'personal_daily_events'
    personal_many_days_events = 'personal_many_days_events'
    fields = 'fields'
    one_links = 'one_links'
    many_links = 'many_links'
    # Workflow's fields
    creator_id = 'creator_id'
    name = 'name'
    description = 'description'
    default_role_id = 'default_role_id'
    projects = 'projects'
    tasks = 'tasks'
    users = 'users'
    creator = 'creator'
    documents = 'documents'
    base_categories = 'base_categories'
    # Project's fields
    workflow_id = 'workflow_id'
    workflow = 'workflow'
    # WFTask's fields
    project_id = 'project_id'
    entrusted_id = 'entrusted_id'
    work_direction_id = 'work_direction_id'
    parent_task_id = 'parent_task_id'
    plan_deadline = 'plan_deadline'
    fact_deadline = 'fact_deadline'
    plan_time = 'plan_time'
    fact_time = 'fact_time'
    plan_start_work_date = 'plan_start_work_date'
    fact_start_work_date = 'fact_start_work_date'
    responsible = 'responsible'
    executors = 'executors'
    entrusted = 'entrusted'
    work_direction = 'work_direction'
    parent_task = 'parent_task'
    child_tasks = 'child_tasks'
    project = 'project'
    # PersonalTask's fields
    owner_id = 'owner_id'
    owner = 'owner'
    # WFWorkDirection's fields
    # PersonalWorkDirection's fields
    # PersonalDailyEvent's fields
    date = 'date'
    time_start = 'time_start'
    time_end = 'time_end'
    # PersonalManyDaysEvent's fields
    datetime_start = 'datetime_start'
    datetime_end = 'datetime_end'
    # WFDailyEvent's fields
    notified = 'notified'
    # WFManyDaysEvent's fields
    # WFBaseCategory's fields
    parent_category_id = 'parent_category_id'
    parent_category = 'parent_category'
    child_categories = 'child_categories'
    # WFDocument's fields
    base_category_id = 'base_category_id'
    base_category = 'base_category'

    # WFRole's fields
    color = 'color'
    permissions = 'permissions'
    # Permission's fields
    type = 'type'
    project_roles = 'project_roles'
    task_roles = 'task_roles'
    daily_event_roles = 'daily_event_roles'
    many_days_event_roles = 'many_days_event_roles'
    document_roles = 'document_roles'
    # WFRoleTask's fields
    role_id = 'role_id'
    task_id = 'task_id'
    # WFRoleDailyEvent's fields
    daily_event_id = 'daily_event_id'
    # WFRoleManyDaysEvent's fields
    many_days_event_id = 'many_days_event_id'
    # WFRoleDocument's fields
    document_id = 'document_id'


class ObjectTypes:
    """Названия объектов, возвращаемых сервером."""

    user = 'user'
    wf_task = 'wf_task'
    wf_daily_event = 'wf_daily_event'
    wf_many_days_event = 'wf_daily_event'
    personal_daily_event = 'personal_daily_event'
    personal_many_days_event = 'personal_many_days_event'
    personal_task = 'personal_task'
    workflow = 'workflow'


class ErrorCodes(enum.Enum):
    """
    Конкретные коды ошибок (error ids).

    Префиксы ошибок:
    no - данные отсутствуют
    invalid - данные не соответствуют требованиям
    existing - (для идентификаторов) уже есть объект с таким идентификатором

    """
    ok = 200  # Запрос выполнен успешно
    server_error = 500  # Ошибка сервера

    no_email = 0  # Нет email'а
    invalid_email = 1  # Некорректный email
    no_password = 2  # Нет пароля
    invalid_password = 3  # Некорректный пароль
    no_login = 4  # Нет логина
    invalid_login = 5  # Некорректный логин

    existing_login = 6  # Логин уже существует
    existing_email = 7  # Email уже существует

    invalid_credentials = 8  # Некорректные учётные данные
    invalid_refresh = 9  # Некорректный refresh-токен
    invalid_access = 10  # Некорректный access-токен
    no_access = 11  # Нет access-токена
    no_refresh = 12  # Нет refresh-токена

    no_tokens = 13  # Нет токенов
    incorrect_id = 14  # Некорректный ID
    incorrect_limit = 15  # Некорректный limit
    incorrect_offset = 16  # Некорректный offset
    forbidden_access_to_personal_object = 17  # Попытка получить доступ к личному объекту другого пользователя


def check_password(password: str) -> bool:
    """Проверяет пароль на соответствие требованиям: длине (10-50), сложности (наличие букв, цифр, символов)."""
    is_chars = any([char.isalpha() for char in password])
    is_digits = any([char.isdigit() for char in password])
    is_other_symbols = any([not char.isdigit() and not char.isalpha() for char in password])

    return CommonStruct.min_password_length <= len(password) <= CommonStruct.max_password_length and is_chars and is_digits and is_other_symbols


def get_datetime_now() -> datetime.datetime:
    """Получает текущее время в формате CommonStruct.datetime_format."""
    datetime_now = datetime.datetime.now()
    formatted_dt = datetime_now.strftime(CommonStruct.datetime_format)
    result = datetime.datetime.strptime(formatted_dt, CommonStruct.datetime_format)
    return result


if __name__ == '__main__':
    pass
