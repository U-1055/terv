"""Функции для обработки разных видов запросов."""
import flask
from flask import Request, Response
import sqlalchemy.exc as err

import logging
import typing as tp

from server.data_const import DataStruct, APIAnswers as APIAn
from common.base import CommonStruct, ErrorCodes
from server.database.repository import DataRepository
import server.utils.api_utils as utl
from server.auth.auth_module import Authenticator
import server.services.services as services


@utl.get_request
def get_wf_tasks(request: Request, repo: DataRepository, user_id: int = None, limit: int = None, offset: int = None,
                 require_last_num: bool = False):  # ToDo: авторизация
    """
    Возвращает задачи РП. Вид запроса:
    api/wf_tasks/ids,name,description,project_id,creator_id,entrusted_id,executor_id
    """
    ids = request.args.getlist(CommonStruct.wf_tasks_ids)

    for id_ in ids:
        if not id_.isdigit():
            return utl.form_response(400,
                                 APIAn.invalid_data_error(
                                     CommonStruct.wf_tasks_ids,
                                     request.endpoint,
                                     f'Incorrect id: {id_}',
                                 ),
                                 error_id=ErrorCodes.incorrect_id.value
                                 )
    ids = [int(id_) for id_ in ids]
    tasks = repo.get_wf_tasks_by_id(ids, limit, offset)

    return utl.form_response(200, 'OK', content=tasks.content,
                         last_rec_num=tasks.last_record_num,
                         records_left=tasks.records_left)


def search_wf_tasks(request: Request, repo: DataRepository):
    """Возвращает задачи по параметрам, переданным в теле запроса."""
    pass  # ToDo: сложный поиск


def add_wf_tasks(request: Request, repo: DataRepository) -> Response:
    """
    Добавляет задачи ПП. В теле запроса принимает следующее:

    wf_tasks: [
        {
         "name": <название задачи>
         "description" <описание задачи>
         "workflow_id" <ID ПП, в котором создаётся задача>
         "project_id" <Проект>  (Опционально)
         "creator_id" <ID создателя>.
         "entrusted_id" <ID поручившего задачу>.
         "work_direction_id" <Направление работы> (Опционально)
         "parent_task_id" <ID родительской задачи> (Опционально)
         "plan_deadline" <Планируемый дедлайн>
         "fact_deadline" <Фактический дедлайн> (Опционально)
         "plan_time": <Планируемое время работы> (Опционально)
         "fact_time": <Фактическое время работы> (Опционально)
         "plan_start_work_date": <Планируемая дата взятия в работу> (Опционально)
         "fact_start_work_date": <Фактическая дата взятия в работу> (Опционально)
        }
    <следующие задачи>
    ]
    Добавляет все задачи в базу.
    """
    tasks = request.json.get(CommonStruct.wf_tasks)
    try:
        result = repo.add_wf_tasks(tasks)
        return utl.form_response(200, 'OK', content=result.ids)
    except err.IntegrityError as e:
        return utl.form_response(400, APIAn.database_write_error(
            CommonStruct.wf_tasks, request.endpoint,
            'Database error occurred',
            str(e)
        ))


def update_wf_tasks(request: Request, repo: DataRepository) -> Response:
    """
    Полностью обновляет модели переданными данными. Принимает в теле ту же структуру, что и add_wf_tasks,
    только с id моделей.
    """
    tasks = request.json.get(CommonStruct.wf_tasks)
    try:
        repo.update_wf_tasks(tasks)
    except err.IntegrityError as e:
        logging.warning(f'DB-error occurred during updating WFTasks: {e}')
        return utl.form_response(400, APIAn.database_write_error(
            CommonStruct.wf_tasks, request.endpoint,
            'Database error occurred',
            str(e)
        ))

    return utl.form_response(200, 'OK')


def delete_wf_tasks(request: Request, repo: DataRepository):
    """Удаляет задачи РП по их id."""
    ids = request.args.getlist(CommonStruct.ids)
    if not utl.check_list_is_digit(ids):
        return utl.form_response(400, APIAn.invalid_data_error(
            CommonStruct.ids, request.endpoint, 'One of params is not integer'))
    ids = utl.list_to_int(ids)

    try:
        repo.delete_wf_tasks_by_id(ids)
    except err.IntegrityError as e:
        logging.warning(f'DB-error occurred during deleting WFTasks: {e}')
        return utl.form_response(400, APIAn.database_write_error(
            CommonStruct.ids, request.endpoint,
            'Database error occurred',
            str(e)
        ))

    return utl.form_response(200, 'OK')


def delete_users(request: Request, repo: DataRepository):
    ids = request.args.getlist(CommonStruct.ids)
    if not utl.check_list_is_digit(ids):
        return utl.form_response(400, APIAn.invalid_data_error(
            CommonStruct.ids, request.endpoint, 'One of params is not integer'))

    try:
        repo.delete_users(ids)
    except err.IntegrityError as e:
        logging.warning(f'DB-error occurred during deleting Users: {e}')
        return utl.form_response(400, APIAn.database_write_error(
            CommonStruct.ids, request.endpoint,
            'Database error occurred',
            str(e)
        ))

    return utl.form_response(200, 'OK')


@utl.get_request
def get_users(request: Request, repo: DataRepository, authenticator: Authenticator, limit: int = None,
              offset: int = None, require_last_num: bool = False):

    params = request.args
    ids = params.getlist(CommonStruct.ids)

    if not ids:  # Если передан только access
        try:
            access_token = request.headers.get('Authorization')
            user_ids = [authenticator.get_user_id(access_token)]
            result = repo.get_users_by_id(user_ids, limit=limit, offset=offset)
            return utl.form_response(200, 'OK', content=result.content)

        except ValueError:
            return utl.form_response(401, 'Expired access token', error_id=ErrorCodes.invalid_access.value)

    if not utl.check_list_is_digit(ids):
        return utl.form_response(400, APIAn.invalid_data_error(CommonStruct.ids, 'One of ids is not integer.'))
    ids = utl.list_to_int(ids)

    try:
        result = repo.get_users_by_id(ids, limit=limit, offset=offset)
        if limit or offset or require_last_num:
            return utl.form_response(200, 'OK', content=result.content, last_rec_num=result.last_record_num,
                                     records_left=result.records_left)
        else:
            return utl.form_response(200, 'OK', content=result.content)
    except err.IntegrityError as e:
        logging.warning(f'DB-error during receiving Users: {e}')
        return utl.form_response(400, APIAn.database_write_error(
            CommonStruct.ids, request.endpoint,
            'Database error occurred',
            str(e)
        ))


def update_users(request: Request, repo: DataRepository):
    """
    Полностью обновляет модели пользователей. В теле запроса принимает следующее:
    {
    users: <список сериализованных моделей User>
    }
    """
    users = request.json.get(CommonStruct.users)
    try:
        repo.update_users(users)
    except err.IntegrityError as e:
        logging.warning(f'DB-error occurred during updating Users: {e}')
        return utl.form_response(400, APIAn.database_write_error(
            CommonStruct.users, request.endpoint,
            'Database error occurred',
            str(e)
        ))

    return utl.form_response(200, 'OK')

# ToDo: параметры фильтрации как аргументы во всех обработчики GET-ов.


@utl.get_request
def get_personal_tasks(request: Request, repo: DataRepository, user_id: int = None, limit: int = None, offset: int = None,
                       require_last_num: bool = False):
    """Получает личные задачи по их ID."""

    params = request.args  # ToDo: фильтрация по пользователю и по датам
    ids = params.getlist(CommonStruct.ids)
    require_last_num = params.get(CommonStruct.require_last_num)

    if not utl.check_list_is_digit(ids):
        return utl.form_response(400, APIAn.invalid_data_error(CommonStruct.ids, request.endpoint,
                                                               'One of ids is not integer'))
    ids = utl.list_to_int(ids)
    try:
        result = repo.get_personal_tasks_by_id(ids, limit, offset)
        if limit or offset or require_last_num:  # Проверка запроса лимита или offset-а
            return utl.form_response(200, 'OK', last_rec_num=result.last_record_num,
                                     records_left=result.records_left, content=result.content)
        else:
            return utl.form_response(200, 'OK', content=result.content)
    except err.IntegrityError as e:
        logging.warning(f'DB-error occurred during receiving PersonalTasks: {e}')
        return utl.form_response(400, APIAn.database_write_error(
            CommonStruct.wf_tasks, request.endpoint,
            'Database error occurred',
            str(e)
        ))


def add_personal_tasks(request: Request, repo: DataRepository):
    """
    Добавляет модели личных задач в базу. Принимает в теле список сериализованных моделей задач с указанными NOT NULL
    полями и без полей id.
    """
    personal_tasks = request.json.getlist(CommonStruct.personal_tasks)
    try:
        result = repo.add_personal_tasks(personal_tasks)
        return utl.form_success_response(content=result.ids)
    except err.IntegrityError as e:
        logging.warning(f'DB-error occurred during creating PersonalTasks: {e}')
        return utl.form_response(400, APIAn.database_write_error(
            CommonStruct.wf_tasks, request.endpoint,
            'Database error occurred',
            str(e)
        ))


def update_personal_tasks(request: Request, repo: DataRepository):
    """Обновляет модели личных задач. Принимает в теле список сериализованных моделей личных задач PersonalTask."""
    personal_tasks = request.json.getlist(CommonStruct.personal_tasks)
    try:
        repo.update_personal_tasks(personal_tasks)
        return utl.form_success_response()
    except err.IntegrityError as e:
        logging.warning(f'DB-error occurred during updating PersonalTasks: {e}')
        return utl.form_response(400, APIAn.database_write_error(
            CommonStruct.wf_tasks, request.endpoint,
            'Database error occurred',
            str(e)
        ))


def delete_personal_tasks(request: Request, repo: DataRepository):
    """Удаляет модели личных задач. Принимает в параметре список ID удаляемых моделей."""
    ids = request.args.getlist(CommonStruct.ids)
    try:
        repo.delete_personal_tasks(ids)
        return utl.form_success_response()
    except err.IntegrityError as e:
        logging.warning(f'DB-error occurred during updating PersonalTasks: {e}')
        return utl.form_response(400, APIAn.database_write_error(
            CommonStruct.wf_tasks, request.endpoint,
            'Database error occurred',
            str(e)
        ))


@utl.get_request
def get_wf_daily_events(request: flask.Request, repo: DataRepository, limit: int = None, offset: int = None,
                        require_last_num: bool = False):
    """Получает однодневные события РП."""
    ids = request.args.getlist(CommonStruct.ids)


def update_wf_daily_events(request: flask.Request, workflow_id: int, repo: DataRepository):
    services.WFDailyEventService.update()


def add_wf_daily_events(request: flask.Request, workflow_id: int, repo: DataRepository):
    """Добавляет однодневные события РП."""
    wf_daily_events = request.args.getlist(CommonStruct.wf_daily_events)
    try:
        repo.add_wf_daily_events(wf_daily_events)
        return utl.form_success_response()
    except err.IntegrityError as e:
        logging.warning(f'DB-error occurred during creating WFDailyEvent: {e}')
        return utl.form_response(400, APIAn.database_write_error(
            CommonStruct.wf_daily_events, request.endpoint,
            'Database error occurred',
            str(e)
        ))


def delete_wf_daily_events(request: flask.Request, workflow_id: int, repo: DataRepository):
    ids = request.args.getlist(CommonStruct.ids)  # ToDo: дописать, когда будет реализована обработка ошибок сервисного слоя


def add_users_to_workflow(request: flask.Request, repo: DataRepository):
    """Добавляет пользователей в ПП. Структура запроса: api/endpoint&workflow_id,user_ids."""
    ids = request.args.getlist(CommonStruct.ids)
    workflow_id = request.args.get(CommonStruct.workflow_id)

    if workflow_id.isdigit():
        workflow_id = int(workflow_id)
    else:
        return utl.form_response(400, APIAn.invalid_data_error(CommonStruct.workflow_id, request.endpoint,
                                                               'Parameter must be digit'))

    if utl.check_list_is_digit(ids):
        ids = utl.list_to_int(ids)
    else:
        return utl.form_response(400, APIAn.invalid_data_error(CommonStruct.ids,
                                                               request.endpoint, 'All of values must be digits'))

    try:
        services.WorkflowService.add_users(ids, workflow_id, repo)
    except ValueError as e:
        logging.warning(f'Error during adding users to workflow: {e}')
        return utl.form_response(400, "Invalid params in request's params")  # ToDo: разобраться с обработкой ошибок (например, ввести исключения сервисного слоя)
    return utl.form_success_response()


def delete_users_from_workflow(request: flask.Request, repo: DataRepository):
    """Удаляет пользователей из ПП. Структура запроса: api/endpoint&workflow_id,user_ids."""
    ids = request.args.getlist(CommonStruct.ids)
    workflow_id = request.args.get(CommonStruct.workflow_id)

    if workflow_id.isdigit():
        workflow_id = int(workflow_id)
    else:
        return utl.form_response(400, APIAn.invalid_data_error(CommonStruct.workflow_id, request.endpoint,
                                                               'Parameter must be digit'))

    if utl.check_list_is_digit(ids):
        ids = utl.list_to_int(ids)
    else:
        return utl.form_response(400, APIAn.invalid_data_error(CommonStruct.ids,
                                                               request.endpoint, 'All of values must be digits'))
    try:
        services.WorkflowService.delete_users(workflow_id, ids, repo)
    except ValueError as e:
        logging.warning(f'Error during deleting users to workflow: {e}')
        return utl.form_response(400,
                                 "Invalid params in request's params")
    return utl.form_success_response()


def set_wf_task_status(request: flask.Request, repo: DataRepository):
    pass

