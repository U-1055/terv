"""Общие константы, используемые и клиентом и сервером. (Названия параметров, элементов ответа, требования к данным)."""
import enum


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
    creator_id = ''
    executor_id = ''
    limit = 'limit'
    offset = 'offset'
    last_rec_num = 'last_rec_num'
    records_left = 'records_left'

    max_login_length = 25
    min_login_length = 5

    max_password_length = 50
    min_password_length = 10


class DBFields:
    """Названия полей таблиц БД."""
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


class ErrorCodes(enum.Enum):
    """
    Конкретные коды ошибок (error ids).

    Префиксы ошибок:
    no - данные отсутствуют
    invalid - данные не соответствуют требованиям
    existing - (для идентификаторов) уже есть объект с таким идентификатором

    """
    ok = 200
    server_error = 500

    no_email = 0
    invalid_email = 1
    no_password = 2
    invalid_password = 3
    no_login = 4
    invalid_login = 5

    existing_login = 6
    existing_email = 7

    invalid_credentials = 8
    invalid_refresh = 9
    invalid_access = 10
    no_access = 11
    no_refresh = 12

    no_tokens = 13
    incorrect_id = 14
    incorrect_limit = 15
    incorrect_offset = 16


def check_password(password: str) -> bool:
    """Проверяет пароль на соответствие требованиям: длине (10-50), сложности (наличие букв, цифр, символов)."""
    is_chars = any([char.isalpha() for char in password])
    is_digits = any([char.isdigit() for char in password])
    is_other_symbols = any([not char.isdigit() and not char.isalpha() for char in password])

    return CommonStruct.min_password_length <= len(password) <= CommonStruct.max_password_length and is_chars and is_digits and is_other_symbols


if __name__ == '__main__':
    pass
