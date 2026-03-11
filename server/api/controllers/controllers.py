"""Функции для обработки разных видов запросов."""
import flask
from flask import Request, Response
import sqlalchemy.exc as err

import typing as tp

from server.data_const import APIAnswers as APIAn
from common.base import CommonStruct, ErrorCodes, TasksStatuses, DBFields
from common.logger import config_logger, SERVER
from server.api.base import LOG_DIR, MAX_FILE_SIZE, MAX_BACKUP_FILES, LOGGING_LEVEL
from server.database.repository import DataRepository
import server.utils.api_utils as utl
from server.auth.auth_module import Authenticator
import server.services.services as services
from server.database.exceptions import BaseRepoException
from server.api.controllers.exceptions import IncorrectParamException, VALUE, MESSAGE

logger = config_logger(__name__, SERVER, LOG_DIR, MAX_BACKUP_FILES, MAX_FILE_SIZE, LOGGING_LEVEL)


class BaseController:

    @staticmethod
    def get(request: Request, repo: DataRepository, limit: int = None, offset: int = None,
            require_last_num: bool = False):
        pass

    @staticmethod
    def add(request: Request, repo: DataRepository):
        pass

    @staticmethod
    def update(request: Request, repo: DataRepository):
        pass

    @staticmethod
    def delete(request: Request, repo: DataRepository):
        pass

    @staticmethod
    def search(request: Request, repo: DataRepository):
        pass


class WSTaskController(BaseController):
    """Контроллеры WSTasks."""

    @staticmethod
    @utl.get_request
    def get(request: Request, repo: DataRepository, user_id: int = None, limit: int = None, offset: int = None,
            require_last_num: bool = False):  # ToDo: авторизация
        """
        Возвращает задачи РП.
        """
        ids = request.args.getlist(CommonStruct.ws_tasks_ids)
        executor_id = request.args.get(CommonStruct.executor_id)
        status_ids = request.args.getlist(CommonStruct.status_ids)
        not_completed = request.args.get(CommonStruct.not_completed)
        date = request.args.get(CommonStruct.date)
        plan_deadline = request.args.get(CommonStruct.plan_deadline)

        if not executor_id:
            executor_id = user_id

        workspace_id = request.args.get(CommonStruct.workspace_id)

        for id_ in ids:
            if not id_.isdigit():
                return utl.form_response(400,
                                         APIAn.invalid_data_error(
                                             CommonStruct.ws_tasks_ids,
                                             request.endpoint,
                                             f'Incorrect id: {id_}',
                                         ),
                                         error_id=ErrorCodes.incorrect_id.value
                                         )
        ids = [int(id_) for id_ in ids]
        tasks = repo.get_ws_tasks(ids, workspace_id, executor_id, date, plan_deadline, status_ids, not_completed, limit, offset)

        return utl.form_response(200, 'OK', content=tasks.content,
                                 last_rec_num=tasks.last_record_num,
                                 records_left=tasks.records_left)

    @staticmethod
    def add(request: Request, repo: DataRepository) -> Response:
        """
        Добавляет задачи ПП. В теле запроса принимает следующее:

        ws_tasks: [
            {
             "name": <название задачи>
             "description" <описание задачи>
             "workspace_id" <ID ПП, в котором создаётся задача>
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
        tasks = request.json.get(CommonStruct.ws_tasks)
        try:
            result = repo.add_ws_tasks(tasks)
            return utl.form_response(200, 'OK', content=result.ids)
        except err.IntegrityError as e:
            return utl.form_response(400, APIAn.database_write_error(
                CommonStruct.ws_tasks, request.endpoint,
                'Database error occurred',
                str(e)
            ))

    @staticmethod
    def update(request: Request, repo: DataRepository) -> Response:
        """
        Полностью обновляет модели переданными данными. Принимает в теле ту же структуру, что и add_ws_tasks,
        только с id моделей.
        """
        tasks = request.json.get(CommonStruct.ws_tasks)
        try:
            repo.update_ws_tasks(tasks)
        except err.IntegrityError as e:
            logger.warning(f'DB-error occurred during updating WSTasks: {e}')
            return utl.form_response(400, APIAn.database_write_error(
                CommonStruct.ws_tasks, request.endpoint,
                'Database error occurred',
                str(e)
            ))

        return utl.form_response(200, 'OK')

    @staticmethod
    def delete(request: Request, repo: DataRepository):
        """Удаляет задачи РП по их id."""
        ids = request.args.getlist(CommonStruct.ids)
        if not utl.check_list_is_digit(ids):
            return utl.form_response(400, APIAn.invalid_data_error(
                CommonStruct.ids, request.endpoint, 'One of params is not integer'))
        ids = utl.list_to_int(ids)

        try:
            repo.delete_ws_tasks_by_id(ids)
        except err.IntegrityError as e:
            logger.warning(f'DB-error occurred during deleting WSTasks: {e}')
            return utl.form_response(400, APIAn.database_write_error(
                CommonStruct.ids, request.endpoint,
                'Database error occurred',
                str(e)
            ))

        return utl.form_response(200, 'OK')

    @staticmethod
    def change_status(request: Request, task_id: int, repo: DataRepository):
        """Изменяет статус задаче."""
        status = request.args.get(CommonStruct.task_status)
        status_id = request.args.get(CommonStruct.status_ids)
        task = repo.get_ws_tasks([task_id])
        if status in (TasksStatuses.default_completed_task_status_name, TasksStatuses.default_task_status_name):  # Если передан стандартный статус
            if not task.content:
                raise IncorrectParamException({"task_id": {VALUE: task, MESSAGE: "Incorrect task's ID"}})
            task = task.content[0]
            workspace = repo.get_workspaces([task.get(DBFields.workspace_id)]).content[0]

            if status == TasksStatuses.default_completed_task_status_name:
                completed_status_id = workspace.get(CommonStruct.completed_task_status_id)
                repo.update_ws_tasks({DBFields.id: task_id, DBFields.status_id: completed_status_id})
        else:  # Если нестандартный
            repo.update_ws_tasks({DBFields.id: task_id, DBFields.status_id: status_id})


class UserController(BaseController):

    @staticmethod
    def delete(request: Request, repo: DataRepository):
        ids = request.args.getlist(CommonStruct.ids)
        if not utl.check_list_is_digit(ids):
            return utl.form_response(400, APIAn.invalid_data_error(
                CommonStruct.ids, request.endpoint, 'One of params is not integer'))

        try:
            repo.delete_users(ids)
        except err.IntegrityError as e:
            logger.warning(f'DB-error occurred during deleting Users: {e}')
            return utl.form_response(400, APIAn.database_write_error(
                CommonStruct.ids, request.endpoint,
                'Database error occurred',
                str(e)
            ))

        return utl.form_response(200, 'OK')

    @staticmethod
    @utl.get_request
    def get(request: Request, repo: DataRepository, authenticator: Authenticator, limit: int = None,
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
            return utl.form_success_response(result.content)
        except BaseRepoException as e:
            pass

    @staticmethod
    def update(request: Request, repo: DataRepository):
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
            logger.warning(f'DB-error occurred during updating Users: {e}')
            return utl.form_response(400, APIAn.database_write_error(
                CommonStruct.users, request.endpoint,
                'Database error occurred',
                str(e)
            ))

        return utl.form_response(200, 'OK')

    @staticmethod
    @utl.get_request
    def search(request: Request, repo: DataRepository, limit: int = None, offset: int = None,
               require_last_num: bool = False):
        """
        Ищет пользователей (User) по имени. Возвращает пользователей, имя которых содержит переданную строку.
        Структура запроса:
        Query:
        username - Строка, содержащаяся в имени пользователя.
        email - Строка, содержащаяся в email пользователя.
        """
        username = request.args.get(CommonStruct.username)
        email_ = request.args.get(CommonStruct.email)
        try:
            response = repo.search_users(username, email_, limit, offset, require_last_num)
            return utl.form_success_response(content=response.content)
        except BaseRepoException as e:  # ToDo: посылать исключения в метод и обогащать их контекстом (сущностью, значением параметра).
            pass


class PersonalTaskController(BaseController):

    @staticmethod
    @utl.get_request
    def get(request: Request, repo: DataRepository, user_id: int = None, limit: int = None, offset: int = None,
            require_last_num: bool = False):
        """Получает личные задачи по их ID."""

        params = request.args
        ids = params.getlist(CommonStruct.ids)
        require_last_num = params.get(CommonStruct.require_last_num)
        date = request.args.get(CommonStruct.date)
        not_completed = request.args.get(CommonStruct.not_completed)
        status_ids = request.args.getlist(CommonStruct.status_ids)
        plan_deadline = request.args.get(CommonStruct.plan_deadline)

        if not utl.check_list_is_digit(ids):
            return utl.form_response(400, APIAn.invalid_data_error(CommonStruct.ids, request.endpoint,
                                                                   'One of ids is not integer'))
        ids = utl.list_to_int(ids)
        try:
            result = repo.get_personal_tasks_by_id(ids, date, plan_deadline, status_ids, not_completed, limit, offset)
            if limit or offset or require_last_num:  # Проверка запроса лимита или offset-а
                return utl.form_response(200, 'OK', last_rec_num=result.last_record_num,
                                         records_left=result.records_left, content=result.content)
            else:
                return utl.form_response(200, 'OK', content=result.content)
        except err.IntegrityError as e:
            logger.warning(f'DB-error occurred during receiving PersonalTasks: {e}')
            return utl.form_response(400, APIAn.database_write_error(
                CommonStruct.ws_tasks, request.endpoint,
                'Database error occurred',
                str(e)
            ))

    @staticmethod
    def add(request: Request, repo: DataRepository):
        """
        Добавляет модели личных задач в базу. Принимает в теле список сериализованных моделей задач с указанными NOT NULL
        полями и без полей id.
        """
        personal_tasks = request.json.getlist(CommonStruct.personal_tasks)
        try:
            result = repo.add_personal_tasks(personal_tasks)
            return utl.form_success_response(content=result.ids)
        except err.IntegrityError as e:
            logger.warning(f'DB-error occurred during creating PersonalTasks: {e}')
            return utl.form_response(400, APIAn.database_write_error(
                CommonStruct.ws_tasks, request.endpoint,
                'Database error occurred',
                str(e)
            ))

    @staticmethod
    def update(request: Request, repo: DataRepository):
        """Обновляет модели личных задач. Принимает в теле список сериализованных моделей личных задач PersonalTask."""
        personal_tasks = request.json.getlist(CommonStruct.personal_tasks)
        try:
            repo.update_personal_tasks(personal_tasks)
            return utl.form_success_response()
        except err.IntegrityError as e:
            logger.warning(f'DB-error occurred during updating PersonalTasks: {e}')
            return utl.form_response(400, APIAn.database_write_error(
                CommonStruct.ws_tasks, request.endpoint,
                'Database error occurred',
                str(e)
            ))

    @staticmethod
    def delete(request: Request, repo: DataRepository):
        """Удаляет модели личных задач. Принимает в параметре список ID удаляемых моделей."""
        ids = request.args.getlist(CommonStruct.ids)
        try:
            repo.delete_personal_tasks(ids)
            return utl.form_success_response()
        except err.IntegrityError as e:
            logger.warning(f'DB-error occurred during updating PersonalTasks: {e}')
            return utl.form_response(400, APIAn.database_write_error(
                CommonStruct.ws_tasks, request.endpoint,
                'Database error occurred',
                str(e)
            ))

    @staticmethod
    def change_status(request: Request, task_id: int, repo: DataRepository):
        """Изменяет статус задаче."""
        status = request.args.get(CommonStruct.task_status)
        status_id = request.args.get(CommonStruct.status_ids)
        task = repo.get_personal_tasks_by_id([task_id])
        if status in (TasksStatuses.default_completed_task_status_name,
                      TasksStatuses.default_task_status_name):  # Если передан стандартный статус
            if not task.content:
                raise IncorrectParamException({"task_id": {VALUE: task, MESSAGE: "Incorrect task's ID"}})
            task = task.content[0]
            owner = repo.get_users_by_id([task.get(DBFields.owner_id)]).content[0]

            if status == TasksStatuses.default_completed_task_status_name:
                completed_status_id = owner.get(CommonStruct.completed_task_status_id)
                repo.update_ws_tasks({DBFields.id: task_id, DBFields.status_id: completed_status_id})
        else:  # Если нестандартный
            repo.update_ws_tasks({DBFields.id: task_id, DBFields.status_id: status_id})


class WSDailyEventController(BaseController):

    @staticmethod
    @utl.get_request
    def get(request: flask.Request, repo: DataRepository, ids=tp.Iterable[int], user_id: int = None,
            limit: int = None, offset: int = None, require_last_num: bool = False):
        """Получает однодневные события РП."""
        ids = request.args.getlist(CommonStruct.ids)
        date = request.args.get(CommonStruct.date)

        if not utl.check_list_is_digit(ids):
            return utl.form_response(400, APIAn.invalid_data_error(CommonStruct.ids, request.endpoint,
                                                                   'One of ids is not integer'))
        ids = utl.list_to_int(ids)
        try:
            result = repo.get_ws_daily_events_by_id(ids, user_id, date, limit, offset, require_last_num)
            return utl.form_response(200, 'OK', result.content, last_rec_num=result.last_record_num,
                                     records_left=result.records_left)
        except err.IntegrityError as e:
            return utl.form_response(400, APIAn.database_write_error(
                '', request.endpoint,
                'Database error occurred',
                str(e)
            ))

    @staticmethod
    def update(request: flask.Request, workspace_id: int, repo: DataRepository):
        services.WSDailyEventService.update()

    @staticmethod
    def add(request: flask.Request, workspace_id: int, repo: DataRepository):
        """Добавляет однодневные события РП."""
        ws_daily_events = request.json.getlist(CommonStruct.ws_daily_events)
        try:
            repo.add_ws_daily_events(ws_daily_events)
            return utl.form_success_response()
        except err.IntegrityError as e:
            logger.warning(f'DB-error occurred during creating WSDailyEvent: {e}')
            return utl.form_response(400, APIAn.database_write_error(
                CommonStruct.ws_daily_events, request.endpoint,
                'Database error occurred',
                str(e)
            ))


class WSManyDaysEventController(BaseController):
    @staticmethod
    @utl.get_request
    def get(request: flask.Request, repo: DataRepository, user_id: int = None, limit: int = None,
                                offset: int = None, require_last_num: bool = False):
        """Получает многодневные события РП."""
        ids = request.args.getlist(CommonStruct.ids)
        included_date = request.args.get(CommonStruct.included_date)
        try:
            ids = utl.list_to_int(ids)
        except ValueError:
            return utl.form_response(400, APIAn.invalid_data_error(CommonStruct.ids, request.endpoint,
                                                                   'One of ids is not integer'))

        try:
            result = repo.get_ws_many_days_events_by_id(ids, user_id, included_date, limit, offset, require_last_num)
            return utl.form_response(200, 'OK', result.content, last_rec_num=result.last_record_num,
                                     records_left=result.records_left)
        except err.IntegrityError as e:
            pass


class PersonalDailyEventController(BaseController):

    @staticmethod
    @utl.get_request
    def get(request: flask.Request, repo: DataRepository, user_id: int = None, limit: int = None,
                                  offset: int = None, require_last_num: bool = False):
        """Получает личные однодневные события."""
        ids = request.args.getlist(CommonStruct.ids)  # ToDo: проверка доступа
        date = request.args.get(CommonStruct.date)

        if not user_id:  # ToDo: такая же проверка для каждого CRUD-а с фильтрацией
            user_id = request.args.get(CommonStruct.user_id)
            if str(user_id).isdigit():
                user_id = int(user_id)

        try:
            ids = utl.list_to_int(ids)
        except ValueError:
            return utl.form_response(400, APIAn.invalid_data_error(CommonStruct.ids, request.endpoint,
                                                                   'One of ids is not integer'))

        try:
            result = repo.get_personal_daily_events_by_id(ids, user_id, date, limit, offset, require_last_num)
            return utl.form_response(200, 'OK', result.content, last_rec_num=result.last_record_num,
                                     records_left=result.records_left)
        except err.IntegrityError as e:
            pass


class PersonalManyDaysEventController(BaseController):

    @staticmethod
    @utl.get_request
    def get(request: flask.Request, repo: DataRepository, user_id: int = None, limit: int = None,
            offset: int = None, require_last_num: bool = False):
        """Получает личные многодневные события."""
        ids = request.args.getlist(CommonStruct.ids)
        included_date = request.args.get(CommonStruct.included_date)

        try:
            ids = utl.list_to_int(ids)
        except ValueError:
            return utl.form_response(400, APIAn.invalid_data_error(CommonStruct.ids, request.endpoint,
                                                                   'One of ids is not integer'))

        try:
            result = repo.get_personal_many_days_events_by_id(ids, user_id, included_date, limit, offset, require_last_num)
            return utl.form_response(200, 'OK', result.content, last_rec_num=result.last_record_num,
                                     records_left=result.records_left)
        except err.IntegrityError as e:
            pass


class WorkspaceController(BaseController):

    @staticmethod
    def add(request: flask.Request, repo: DataRepository):
        """Добавляет пользователей в ПП. Структура запроса: api/endpoint&workspace_id,user_ids."""
        ids = request.args.getlist(CommonStruct.ids)
        workspace_id = request.args.get(CommonStruct.workspace_id)

        if workspace_id.isdigit():
            workspace_id = int(workspace_id)
        else:
            return utl.form_response(400, APIAn.invalid_data_error(CommonStruct.workspace_id, request.endpoint,
                                                                   'Parameter must be digit'))

        if utl.check_list_is_digit(ids):
            ids = utl.list_to_int(ids)
        else:
            return utl.form_response(400, APIAn.invalid_data_error(CommonStruct.ids,
                                                                   request.endpoint, 'All of values must be digits'))

        try:
            services.WorkspaceService.add_users(ids, workspace_id, repo)
        except ValueError as e:
            logger.warning(f'Error during adding users to workspace: {e}')
            return utl.form_response(400, "Invalid params in request's params")  # ToDo: разобраться с обработкой ошибок (например, ввести исключения сервисного слоя)
        return utl.form_success_response()

    @staticmethod
    def delete(request: flask.Request, repo: DataRepository):
        """Удаляет пользователей из ПП. Структура запроса: api/endpoint&workspace_id,user_ids."""
        ids = request.args.getlist(CommonStruct.ids)
        workspace_id = request.args.get(CommonStruct.workspace_id)

        if workspace_id.isdigit():
            workspace_id = int(workspace_id)
        else:
            return utl.form_response(400, APIAn.invalid_data_error(CommonStruct.workspace_id, request.endpoint,
                                                                   'Parameter must be digit'))

        if utl.check_list_is_digit(ids):
            ids = utl.list_to_int(ids)
        else:
            return utl.form_response(400, APIAn.invalid_data_error(CommonStruct.ids,
                                                                   request.endpoint, 'All of values must be digits'))
        try:
            services.WorkspaceService.delete_users(workspace_id, ids, repo)
        except ValueError as e:
            logger.warning(f'Error during deleting users to workspace: {e}')
            return utl.form_response(400,
                                     "Invalid params in request's params")
        return utl.form_success_response()


class PersonalTaskEventController(BaseController):
    """Контроллер личных задач-мероприятий."""

    @staticmethod
    @utl.get_request
    def get(request: flask.Request, repo: DataRepository, limit: int = None, offset: int = None,
            require_last_num: bool = False):
        ids = request.args.getlist(CommonStruct.ids)
        user_id = request.args.get(CommonStruct.user_id)

        response = repo.get_personal_task_events_by_user(ids, user_id, limit, offset, require_last_num)

        return utl.form_success_response(content=response.content)


class WSTaskEventController(BaseController):
    """Контроллер задач-мероприятий РП."""

    @staticmethod
    @utl.get_request
    def get(request: flask.Request, repo: DataRepository, limit: int = None,
            offset: int = None, require_last_num: bool = False):
        ids = request.args.getlist(CommonStruct.ids)
        workspace_id = request.args.get(CommonStruct.workspace_id)
        executor_id = request.args.get(CommonStruct.executor_id)
        response = repo.get_ws_task_events(ids, workspace_id, executor_id, limit, offset, require_last_num)
        return utl.form_success_response(content=response.content)


