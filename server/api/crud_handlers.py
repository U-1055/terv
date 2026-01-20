"""Функции для обработки разных видов запросов."""
import logging

from flask import Request, Response
import sqlalchemy.exc as err

from server.data_const import DataStruct, APIAnswers as APIAn
from common.base import CommonStruct, ErrorCodes
from server.database.repository import DataRepository
from server.utils.api_utils import form_response, prepare_limit_offset, check_list_is_digit, list_to_int
from server.auth.auth_module import Authenticator


def get_wf_tasks(request: Request, repo: DataRepository):
    """
    Возвращает задачи РП. Вид запроса:
    api/wf_tasks/ids,name,description,project_id,creator_id,entrusted_id,executor_id

    """
    ids = request.args.getlist(CommonStruct.wf_tasks_ids)
    limit = request.args.get(CommonStruct.limit)
    offset = request.args.get(CommonStruct.offset)

    result = prepare_limit_offset(limit, offset, request)
    if result:
        return result

    if limit:
        limit = int(limit)
    else:
        limit = None
    if offset:
        offset = int(offset)
    else:
        offset = None

    for id_ in ids:
        if not id_.isdigit():
            return form_response(400,
                                 APIAn.invalid_data_error(
                                     CommonStruct.wf_tasks_ids,
                                     request.endpoint,
                                     f'Incorrect id: {id_}',
                                 ),
                                 error_id=ErrorCodes.incorrect_id.value
                                 )
    ids = [int(id_) for id_ in ids]
    tasks = repo.get_wf_tasks_by_id(ids, limit, offset)

    return form_response(200, 'OK', content=tasks.content,
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
        repo.add_wf_tasks(tasks)
    except err.IntegrityError as e:
        return form_response(400, APIAn.database_write_error(
            CommonStruct.wf_tasks, request.endpoint,
            'Database error occurred',
            str(e)
        ))

    return form_response(200, 'OK')


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
        return form_response(400, APIAn.database_write_error(
            CommonStruct.wf_tasks, request.endpoint,
            'Database error occurred',
            str(e)
        ))

    return form_response(200, 'OK')


def delete_wf_tasks(request: Request, repo: DataRepository):
    """Удаляет задачи РП по их id."""
    ids = request.args.getlist(CommonStruct.ids)
    if not check_list_is_digit(ids):
        return form_response(400, APIAn.invalid_data_error(
            CommonStruct.ids, request.endpoint, 'One of params is not integer'))
    ids = list_to_int(ids)

    try:
        repo.delete_wf_tasks_by_id(ids)
    except err.IntegrityError as e:
        logging.warning(f'DB-error occurred during deleting WFTasks: {e}')
        return form_response(400, APIAn.database_write_error(
            CommonStruct.ids, request.endpoint,
            'Database error occurred',
            str(e)
        ))

    return form_response(200, 'OK')


def delete_users(request: Request, repo: DataRepository):
    ids = request.args.getlist(CommonStruct.ids)
    if not check_list_is_digit(ids):
        return form_response(400, APIAn.invalid_data_error(
            CommonStruct.ids, request.endpoint, 'One of params is not integer'))

    try:
        repo.delete_users(ids)
    except err.IntegrityError as e:
        logging.warning(f'DB-error occurred during deleting Users: {e}')
        return form_response(400, APIAn.database_write_error(
            CommonStruct.ids, request.endpoint,
            'Database error occurred',
            str(e)
        ))

    return form_response(200, 'OK')


def get_users(request: Request, repo: DataRepository, authenticator: Authenticator):

    params = request.args
    ids = params.getlist(CommonStruct.ids)
    limit = params.get(CommonStruct.limit)
    offset = params.get(CommonStruct.offset)
    require_last_num = params.get(CommonStruct.require_last_num)

    result = prepare_limit_offset(limit, offset, request)
    if result:
        return result

    if limit:
        limit = int(limit)
    else:
        limit = None
    if offset:
        offset = int(offset)
    else:
        offset = None

    if not ids:  # Если передан только access
        try:
            access_token = request.headers.get('Authorization')
            usernames = [authenticator.get_login(access_token)]
            result = repo.get_users_by_username(usernames, limit=limit, offset=offset)
            return form_response(200, 'OK', content=result.content)

        except ValueError:
            return form_response(401, 'Expired access token', error_id=ErrorCodes.invalid_access.value)

    if not check_list_is_digit(ids):
        return form_response(400, APIAn.invalid_data_error(CommonStruct.ids, 'One of ids is not integer.'))
    ids = list_to_int(ids)

    try:
        result = repo.get_users_by_id(ids, limit=limit, offset=offset)
        if limit or offset or require_last_num:
            return form_response(200, 'OK', content=result.content, last_rec_num=result.last_record_num,
                                 records_left=result.records_left)
        else:
            return form_response(200, 'OK', content=result.content)
    except err.IntegrityError as e:
        logging.warning(f'DB-error during receiving Users: {e}')
        return form_response(400, APIAn.database_write_error(
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
        return form_response(400, APIAn.database_write_error(
            CommonStruct.users, request.endpoint,
            'Database error occurred',
            str(e)
        ))

    return form_response(200, 'OK')


def get_personal_tasks(request: Request, repo: DataRepository):
    """Получает личные задачи по их ID."""

    params = request.args
    ids = params.getlist(CommonStruct.ids)
    limit = params.get(CommonStruct.limit)
    offset = params.get(CommonStruct.offset)
    require_last_num = params.get(CommonStruct.require_last_num)

    result = prepare_limit_offset(limit, offset, request)
    if result:
        return result

    if limit:
        limit = int(limit)
    else:
        limit = None
    if offset:
        offset = int(offset)
    else:
        offset = None

    if not check_list_is_digit(ids):
        return form_response(400, APIAn.invalid_data_error(CommonStruct.ids, request.endpoint,
                                                           'One of ids is not integer'))
    ids = list_to_int(ids)
    try:
        result = repo.get_wf_tasks_by_id(ids, limit, offset)
        if limit or offset or require_last_num:  # Проверка запроса лимита или offset-а
            return form_response(200, 'OK', last_rec_num=result.last_record_num,
                                 records_left=result.records_left)
        else:
            return form_response(200, 'OK', content=result.content)
    except err.IntegrityError as e:
        logging.warning(f'DB-error occurred during receiving PersonalTasks: {e}')
        return form_response(400, APIAn.database_write_error(
            CommonStruct.wf_tasks, request.endpoint,
            'Database error occurred',
            str(e)
        ))


def add_personal_tasks(request: Request, repo: DataRepository):
    pass


def update_personal_tasks(request: Request, repo: DataRepository):
    pass


def delete_personal_tasks(request: Request, repo: DataRepository):
    pass
