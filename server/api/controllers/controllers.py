"""Функции для обработки разных видов запросов."""
import datetime

import flask
from flask import Request, Response

import typing as tp

from common.base import CommonStruct, ErrorCodes, TasksStatuses, DBFields, get_datetime_now
from common.logger import config_logger, SERVER
from server.api.base import LOG_DIR, MAX_FILE_SIZE, MAX_BACKUP_FILES, LOGGING_LEVEL
from server.database.repository import DataRepository
import server.utils.api_utils as utl
from server.auth.auth_module import Authenticator, Authorizer
import server.services.services as services
from server.database.exceptions import BaseRepoException
from server.api.controllers.exceptions import (IncorrectParamException, VALUE, MESSAGE, map_repo_to_controller_exc,
                                               map_service_to_controller_exc)
from server.services.exceptions import BaseServiceException
from server.api.controllers.data_handlers import Bool, Int, Date, DateTime, IntList, String
from server.data_const import Roles

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
            require_last_num: bool = False):
        """
        Возвращает задачи РП.
        """
        ids = IntList(CommonStruct.ws_tasks_ids, request.args.getlist(CommonStruct.ws_tasks_ids),
                      ErrorCodes.incorrect_ws_tasks_ids.value)
        executor_id = Int(CommonStruct.executor_id, request.args.get(CommonStruct.executor_id),
                          ErrorCodes.incorrect_executor_id.value)
        status_ids = IntList(CommonStruct.status_ids, request.args.getlist(CommonStruct.status_ids),
                             ErrorCodes.incorrect_status_ids.value)
        not_completed = Bool(CommonStruct.not_completed, request.args.get(CommonStruct.not_completed),
                             ErrorCodes.incorrect_not_completed.value)
        date = Date(CommonStruct.date, request.args.get(CommonStruct.date), ErrorCodes.incorrect_date.value)
        plan_deadline = DateTime(CommonStruct.plan_deadline, request.args.get(CommonStruct.plan_deadline),
                                 ErrorCodes.incorrect_plan_deadline.value)
        workspace_id = Int(CommonStruct.workspace_id, request.args.get(CommonStruct.workspace_id),
                           ErrorCodes.incorrect_workspace_id.value)

        tasks = repo.get_ws_tasks(ids.value, workspace_id.value, executor_id.value, date.value, plan_deadline.value,
                                  status_ids.value, not_completed.value, limit, offset)

        return utl.form_response(200, 'OK', content=tasks.content,
                                 last_rec_num=tasks.last_record_num,
                                 records_left=tasks.records_left)

    @staticmethod
    def add(request: Request, repo: DataRepository, authenticator: Authenticator, authorizer: Authorizer, user_id: int) -> Response:
        """
        Добавляет задачи проекта. В теле запроса принимает следующее:

        ws_tasks: [
            {
             "name": <название задачи>
             "description" <описание задачи>
             "project_id" <Проект>
             "plan_deadline" <Планируемый дедлайн в формате datetime.datetime>
             "executor_id" <ID исполнителя>
            }
        ]
        Добавляет все задачи в базу.
        """
        tasks = request.json.get(CommonStruct.ws_tasks)
        if not tasks:
            raise IncorrectParamException({CommonStruct.ws_tasks: {VALUE: None, MESSAGE: 'No tasks in request'}})

        project_id = tasks[0].get(DBFields.project_id)
        if not project_id:
            raise IncorrectParamException({DBFields.project_id: {VALUE: None, MESSAGE: 'project_id is required'}})

        try:
            services.WSTaskService.create(tuple(tasks), project_id, user_id, repo, authorizer)
            return utl.form_response(200, 'OK', content=[t.get(DBFields.id) for t in tasks])
        except BaseServiceException as e:
            raise map_service_to_controller_exc(e, {})

    @staticmethod
    def update(request: Request, repo: DataRepository, authenticator: Authenticator, authorizer: Authorizer, user_id: int) -> Response:
        """
        Полностью обновляет модели переданными данными. Принимает в теле ту же структуру, что и add,
        только с id моделей.
        """
        tasks = request.json.get(CommonStruct.ws_tasks)
        if not tasks:
            raise IncorrectParamException({CommonStruct.ws_tasks: {VALUE: None, MESSAGE: 'No tasks in request'}})

        try:
            services.WSTaskService.update(tuple(tasks), user_id, repo, authorizer)
        except BaseServiceException as e:
            raise map_service_to_controller_exc(e, {})

        return utl.form_response(200, 'OK')

    @staticmethod
    def delete(request: Request, repo: DataRepository, authenticator: Authenticator, authorizer: Authorizer, user_id: int):
        """Удаляет задачи проекта по их id."""
        ids = IntList(CommonStruct.ws_tasks_ids, request.args.getlist(CommonStruct.ids),
                      ErrorCodes.incorrect_ws_tasks_ids.value)

        try:
            services.WSTaskService.delete(tuple(ids.value), user_id, repo, authorizer)
        except BaseServiceException as e:
            raise map_service_to_controller_exc(e, {})
        return utl.form_response(200, 'OK')

    @staticmethod
    def change_status(request: Request, task_id: int, repo: DataRepository):
        """Изменяет статус задаче."""
        status = String(CommonStruct.task_status,
                        request.args.get(CommonStruct.task_status),
                        ErrorCodes.incorrect_status.value, allowed=TasksStatuses)
        status_id = String(CommonStruct.status_id,
                           request.args.get(CommonStruct.status_ids),
                           ErrorCodes.incorrect_status_id.value)

        task = repo.get_ws_tasks([task_id])
        if status.value in TasksStatuses:  # Если передан стандартный статус
            if not task.content:
                raise IncorrectParamException({"task_id": {VALUE: task, MESSAGE: "Incorrect task's ID"}})
            task = task.content[0]
            workspace = repo.get_workspaces([task.get(DBFields.workspace)]).content[0]

            if status.value == TasksStatuses.completed.value:
                completed_status_id = workspace.get(CommonStruct.completed_task_status_id)
                repo.update_ws_tasks([{DBFields.id: task_id, DBFields.status_id: completed_status_id}])
                return utl.form_success_response()
        else:
            repo.update_ws_tasks([{DBFields.id: task_id, DBFields.status_id: status_id.value}])
            return utl.form_success_response()


class UserController(BaseController):

    @staticmethod
    def delete(request: Request, repo: DataRepository):
        ids = IntList(CommonStruct.ids,
                      request.args.getlist(CommonStruct.ids),
                      ErrorCodes.incorrect_user_ids.value)

        try:
            repo.delete_users(ids.value)
        except BaseRepoException as e:
            raise map_repo_to_controller_exc(e, {})

        return utl.form_response(200, 'OK')

    @staticmethod
    @utl.get_request
    def get(request: Request, repo: DataRepository, authenticator: Authenticator, limit: int = None,
            offset: int = None, require_last_num: bool = False):

        ids = IntList(CommonStruct.ids,
                      request.args.getlist(CommonStruct.ids),
                      ErrorCodes.incorrect_user_ids.value)

        if not ids.value:  # Если нет ID пользователя, берём с access
            try:
                access_token = request.headers.get('Authorization')
                user_ids = [authenticator.get_user_id(access_token)]
                result = repo.get_users_by_id(user_ids, limit=limit, offset=offset)
                return utl.form_response(200, 'OK', content=result.content)
            except ValueError:
                return utl.form_response(401, 'Expired access token', error_id=ErrorCodes.invalid_access.value)

        try:
            result = repo.get_users_by_id(ids.value, limit=limit, offset=offset)
            return utl.form_success_response(result.content)
        except BaseRepoException as e:
            raise map_repo_to_controller_exc(e, {})

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
        except BaseRepoException as e:
            raise map_repo_to_controller_exc(e, {})

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
        username = String(CommonStruct.username,
                          request.args.get(CommonStruct.username))
        email_ = String(CommonStruct.email, request.args.get(CommonStruct.email))
        try:
            response = repo.search_users(username.value, email_.value, limit, offset, require_last_num)
            return utl.form_success_response(content=response.content)
        except BaseRepoException as e:
            raise map_repo_to_controller_exc(e, {})


class PersonalTaskController(BaseController):

    @staticmethod
    @utl.get_request
    def get(request: Request, repo: DataRepository, user_id: int = None, limit: int = None, offset: int = None,
            require_last_num: bool = False):
        """Получает личные задачи по их ID."""

        ids = IntList(CommonStruct.ids, request.args.getlist(CommonStruct.ids),
                      ErrorCodes.incorrect_personal_tasks_ids.value)
        date = Date(CommonStruct.date, request.args.get(CommonStruct.date), ErrorCodes.incorrect_date.value)
        not_completed = Bool(CommonStruct.not_completed, request.args.get(CommonStruct.not_completed))
        status_ids = IntList(CommonStruct.status_ids, request.args.getlist(CommonStruct.status_ids),
                             ErrorCodes.incorrect_status_ids.value)
        plan_deadline = DateTime(CommonStruct.plan_deadline, request.args.get(CommonStruct.plan_deadline),
                                 ErrorCodes.incorrect_plan_deadline.value)
        if user_id:
            owner_id = Int(CommonStruct.user_id, user_id, ErrorCodes.incorrect_user_id.value)
        else:
            owner_id = Int(CommonStruct.user_id, request.args.get(CommonStruct.user_id), ErrorCodes.incorrect_user_id.value)

        try:
            result = repo.get_personal_tasks_by_id(ids.value, owner_id.value, date.value, plan_deadline.value,
                                                   status_ids.value, not_completed.value, limit, offset)
            if limit or offset or require_last_num:  # Check request of limit or offset
                return utl.form_response(200, 'OK', last_rec_num=result.last_record_num,
                                         records_left=result.records_left, content=result.content)
            else:
                return utl.form_response(200, 'OK', content=result.content)
        except BaseRepoException as e:
            raise map_repo_to_controller_exc(e, {})

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
        except BaseRepoException as e:
            raise map_repo_to_controller_exc(e, {})

    @staticmethod
    def update(request: Request, repo: DataRepository):
        """Обновляет модели личных задач. Принимает в теле список сериализованных моделей личных задач PersonalTask."""
        personal_tasks = request.json.getlist(CommonStruct.personal_tasks)
        try:
            repo.update_personal_tasks(personal_tasks)
            return utl.form_success_response()
        except BaseRepoException as e:
            raise map_repo_to_controller_exc(e, {})

    @staticmethod
    def delete(request: Request, repo: DataRepository):
        """Удаляет модели личных задач. Принимает в параметре список ID удаляемых моделей."""
        ids = IntList(CommonStruct.ids, request.args.getlist(CommonStruct.ids),
                      ErrorCodes.incorrect_personal_tasks_ids.value)
        try:
            repo.delete_personal_tasks(ids.value)
            return utl.form_success_response()
        except BaseRepoException as e:
            raise map_repo_to_controller_exc(e, {})

    @staticmethod
    def change_status(request: Request, task_id: int, repo: DataRepository):
        """Изменяет статус задаче."""
        status = String(CommonStruct.task_status,
                        request.args.get(CommonStruct.task_status),
                        ErrorCodes.incorrect_status.value, allowed=TasksStatuses)
        status_id = String(CommonStruct.status_id,
                           request.args.get(CommonStruct.status_ids),
                           ErrorCodes.incorrect_status_id.value)

        task = repo.get_personal_tasks_by_id([task_id])
        if status.value in TasksStatuses:  # Если передан стандартный статус
            if not task.content:
                raise IncorrectParamException({"task_id": {VALUE: task, MESSAGE: "Incorrect task's ID"}})
            task = task.content[0]
            owner = repo.get_users_by_id([task.get(DBFields.owner)]).content[0]

            if status.value == TasksStatuses.completed.value:
                completed_status_id = owner.get(CommonStruct.completed_task_status_id)
                repo.update_personal_tasks([{DBFields.id: task_id, DBFields.status_id: completed_status_id}])
                return utl.form_success_response()
        else:
            repo.update_personal_tasks([{DBFields.id: task_id, DBFields.status_id: status_id.value}])
            return utl.form_success_response()


class WSDailyEventController(BaseController):

    @staticmethod
    @utl.get_request
    def get(request: flask.Request, repo: DataRepository, ids=tp.Iterable[int], user_id: int = None,
            limit: int = None, offset: int = None, require_last_num: bool = False):
        """Получает однодневные события РП."""
        ids = IntList(CommonStruct.ids, request.args.getlist(CommonStruct.ids),
                      ErrorCodes.incorrect_ws_daily_events_ids.value)
        date = Date(CommonStruct.date, request.args.get(CommonStruct.date), ErrorCodes.incorrect_date.value)
        workspace_id = Int(CommonStruct.workspace_id, request.args.get(CommonStruct.workspace_id),
                           ErrorCodes.incorrect_workspace_id.value)

        if user_id:
            notified_ids = [user_id]
        else:
            notified_ids = IntList(CommonStruct.notified_ids, request.args.getlist(CommonStruct.notified_ids),
                                   ErrorCodes.incorrect_notified_ids.value)
        try:
            result = repo.get_ws_daily_events_by_id(ids.value, workspace_id.value, notified_ids.value, date.value,
                                                    limit, offset, require_last_num)
            return utl.form_response(200, 'OK', result.content, last_rec_num=result.last_record_num,
                                     records_left=result.records_left)
        except BaseRepoException as e:
            raise map_repo_to_controller_exc(e, {})

    @staticmethod
    def update(request: flask.Request, workspace_id: int, repo: DataRepository):
        pass

    @staticmethod
    def add(request: flask.Request, workspace_id: int, repo: DataRepository):
        """Добавляет однодневные события РП."""
        pass


class WSManyDaysEventController(BaseController):
    @staticmethod
    @utl.get_request
    def get(request: flask.Request, repo: DataRepository, user_id: int = None, limit: int = None,
            offset: int = None, require_last_num: bool = False):
        """Получает многодневные события РП."""
        ids = IntList(CommonStruct.ids, request.args.getlist(CommonStruct.ids),
                      ErrorCodes.incorrect_ws_many_days_events_ids.value)
        included_date = Date(CommonStruct.included_date, request.args.get(CommonStruct.included_date),
                             ErrorCodes.incorrect_included_date.value)
        workspace_id = Int(CommonStruct.workspace_id, request.args.get(CommonStruct.workspace_id),
                           ErrorCodes.incorrect_workspace_id.value)

        if user_id:
            notified_ids = [user_id]
        else:
            notified_ids = IntList(CommonStruct.notified_ids, request.args.getlist(CommonStruct.notified_ids),
                                   ErrorCodes.incorrect_notified_ids.value)
        try:
            result = repo.get_ws_many_days_events_by_id(ids.value, workspace_id.value, notified_ids.value,
                                                        included_date.value, limit, offset, require_last_num)
            return utl.form_response(200, 'OK', result.content, last_rec_num=result.last_record_num,
                                     records_left=result.records_left)
        except BaseRepoException as e:
            raise map_repo_to_controller_exc(e, {})


class PersonalDailyEventController(BaseController):

    @staticmethod
    @utl.get_request
    def get(request: flask.Request, repo: DataRepository, user_id: int = None, limit: int = None,
            offset: int = None, require_last_num: bool = False):
        """Получает личные однодневные события."""
        ids = IntList(CommonStruct.ids, request.args.getlist(CommonStruct.ids),
                      ErrorCodes.incorrect_personal_daily_events_ids.value)
        date = Date(CommonStruct.date, request.args.get(CommonStruct.date), ErrorCodes.incorrect_date.value)

        if not user_id:
            user_id = Int(CommonStruct.user_id, request.args.get(CommonStruct.user_id),
                          ErrorCodes.incorrect_user_id.value)

        try:
            result = repo.get_personal_daily_events_by_id(ids.value, user_id.value, date.value,
                                                          limit, offset, require_last_num)
            return utl.form_response(200, 'OK', result.content, last_rec_num=result.last_record_num,
                                     records_left=result.records_left)
        except BaseRepoException as e:
            raise map_repo_to_controller_exc(e, {})


class PersonalManyDaysEventController(BaseController):

    @staticmethod
    @utl.get_request
    def get(request: flask.Request, repo: DataRepository, user_id: int = None, limit: int = None,
            offset: int = None, require_last_num: bool = False):
        """Получает личные многодневные события."""
        ids = IntList(CommonStruct.ids, request.args.getlist(CommonStruct.ids),
                      ErrorCodes.incorrect_personal_many_days_events_ids.value)
        included_date = Date(CommonStruct.included_date, request.args.get(CommonStruct.included_date),
                             ErrorCodes.incorrect_included_date.value)
        if not user_id:
            user_id = Int(CommonStruct.user_id, request.args.get(CommonStruct.user_id),
                          ErrorCodes.incorrect_user_id.value)

        try:
            result = repo.get_personal_many_days_events_by_id(ids.value, user_id.value, included_date.value, limit, offset, require_last_num)
            return utl.form_response(200, 'OK', result.content, last_rec_num=result.last_record_num,
                                     records_left=result.records_left)
        except BaseRepoException as e:
            raise map_repo_to_controller_exc(e, {})


class WorkspaceController(BaseController):

    @staticmethod
    def add(request: flask.Request, repo: DataRepository, authenticator: Authenticator, authorizer: Authorizer, user_id: int):
        """Добавляет пользователей в ПП. Структура запроса: api/endpoint&workspace_id,user_ids."""
        ids = IntList(CommonStruct.ids, request.args.getlist(CommonStruct.ids),
                      ErrorCodes.incorrect_user_ids.value)
        workspace_id = Int(CommonStruct.workspace_id, request.args.get(CommonStruct.workspace_id),
                           ErrorCodes.incorrect_workspace_id.value)

        try:
            services.WorkspaceService.add_users(ids.value, workspace_id.value, repo)
        except BaseServiceException as e:
            raise map_service_to_controller_exc(e, {})

        return utl.form_success_response()

    @staticmethod
    def kick(request: flask.Request, repo: DataRepository):
        """Удаляет пользователей из РП. Структура запроса: api/endpoint&workspace_id,user_ids."""
        ids = IntList(CommonStruct.ids, request.args.getlist(CommonStruct.ids), ErrorCodes.incorrect_user_ids.value)
        workspace_id = Int(CommonStruct.workspace_id, request.args.get(CommonStruct.workspace_id),
                           ErrorCodes.incorrect_workspace_id.value)
        try:
            services.WorkspaceService.delete_users(workspace_id.value, ids.value, repo)
        except BaseServiceException as e:
            map_service_to_controller_exc(e, {})
        return utl.form_success_response()

    @staticmethod
    @utl.get_request
    def get(request: flask.Request, repo: DataRepository, limit: int = None, offset: int = None,
            require_last_num: bool = False):
        """
        Query: ids (ID РП), creator_ids (ID создателей)
        """
        ids = IntList(CommonStruct.ids, request.args.getlist(CommonStruct.ids), ErrorCodes.incorrect_workspaces_ids.value)
        creator_ids = IntList(CommonStruct.creator_ids, request.args.getlist(CommonStruct.creator_ids),
                              ErrorCodes.incorrect_creator_ids.value)
        try:
            response = repo.get_workspaces(ids.value, creator_ids.value, limit, offset, require_last_num)
            return utl.form_get_success_response(response.content, response.last_record_num, response.records_left)
        except BaseRepoException as e:
            raise map_repo_to_controller_exc(e, {})

    @staticmethod
    def create(request: flask.Request, repo: DataRepository, authenticator: Authenticator, authorizer: Authorizer, user_id: int):
        """Создаёт рабочее пространство."""
        workspace = request.json.get('workspace')
        if not workspace:
            raise IncorrectParamException({'workspace': {VALUE: None, MESSAGE: 'No workspace in request'}})

        try:
            workspace_id = services.WorkspaceService.create(workspace, user_id, repo, authorizer)

            # Создаём роли для нового рабочего пространства
            roles = [
                {DBFields.name: Roles.mentor.value, DBFields.workspace_id: workspace_id},
                {DBFields.name: Roles.student.value, DBFields.workspace_id: workspace_id},
                {DBFields.name: Roles.admin.value, DBFields.workspace_id: workspace_id},
                {DBFields.name: Roles.team_lead.value, DBFields.workspace_id: workspace_id}
            ]
            repo.add_ws_roles(roles)

            return utl.form_success_response({'workspace_id': workspace_id})
        except BaseServiceException as e:
            raise map_service_to_controller_exc(e, {})

    @staticmethod
    def update(request: flask.Request, repo: DataRepository, authenticator: Authenticator, authorizer: Authorizer, user_id: int):
        """Обновляет рабочее пространство."""
        workspace = request.json.get('workspace')
        if not workspace:
            raise IncorrectParamException({'workspace': {VALUE: None, MESSAGE: 'No workspace in request'}})

        try:
            workspace[DBFields.updated_at] = get_datetime_now()
            repo.update_workspaces([workspace])
            return utl.form_success_response()
        except BaseRepoException as e:
            raise map_repo_to_controller_exc(e, {})

    @staticmethod
    def delete(request: flask.Request, repo: DataRepository, authenticator: Authenticator, authorizer: Authorizer, user_id: int):
        """Удаляет рабочее пространство."""
        ids = IntList(CommonStruct.ids, request.args.getlist(CommonStruct.ids), ErrorCodes.incorrect_workspaces_ids.value)
        try:
            repo.delete_workspaces(ids.value)
            return utl.form_success_response()
        except BaseRepoException as e:
            raise map_repo_to_controller_exc(e, {})

    @staticmethod
    def add_user_to_workspace(request: flask.Request, repo: DataRepository, authorizer: Authorizer, user_id: int, workspace_id: int):
        """Добавляет пользователей в рабочее пространство."""
        user_ids = IntList(CommonStruct.ids, request.args.getlist(CommonStruct.ids), ErrorCodes.incorrect_user_ids.value)
        try:
            for uid in user_ids.value:
                services.WorkspaceService.add_user_to_workspace(uid, workspace_id, repo, authorizer, user_id)
            return utl.form_success_response()
        except BaseServiceException as e:
            raise map_service_to_controller_exc(e, {})

    @staticmethod
    def remove_user_from_workspace(request: flask.Request, repo: DataRepository, authorizer: Authorizer, user_id: int, workspace_id: int, target_user_id: int):
        """Удаляет пользователя из рабочего пространства."""
        try:
            services.WorkspaceService.delete_user_from_workspace(target_user_id, workspace_id, repo, authorizer, user_id)
            return utl.form_success_response()
        except BaseServiceException as e:
            raise map_service_to_controller_exc(e, {})

    @staticmethod
    def get_workspace_users(request: flask.Request, repo: DataRepository, workspace_id: int, limit: int = None, offset: int = None, require_last_num: bool = False):
        """Получает пользователей рабочего пространства."""
        try:
            response = repo.get_workspace_users(workspace_id, limit, offset, require_last_num)
            return utl.form_get_success_response(response.content, response.last_record_num, response.records_left)
        except BaseRepoException as e:
            raise map_repo_to_controller_exc(e, {})

    @staticmethod
    def get_user_role_in_workspace(request: flask.Request, repo: DataRepository, workspace_id: int, target_user_id: int):
        """Получает роль пользователя в рабочем пространстве."""
        try:
            role = services.WorkspaceService.get_user_role(target_user_id, workspace_id, repo)
            if role:
                return utl.form_success_response(role)
            else:
                return utl.form_response(404, 'User not found in workspace', error_id=ErrorCodes.incorrect_user_id.value)
        except BaseRepoException as e:
            raise map_repo_to_controller_exc(e, {})

    @staticmethod
    def set_user_role_in_workspace(request: flask.Request, repo: DataRepository, authenticator: Authenticator, authorizer: Authorizer, user_id: int, workspace_id: int, target_user_id: int):
        """Устанавливает роль пользователю в рабочем пространстве."""
        role_id = Int('role_id', request.args.get('role_id'), ErrorCodes.incorrect_id.value)
        try:
            services.WorkspaceService.set_user_role(target_user_id, workspace_id, role_id.value, repo, authorizer, user_id)
            return utl.form_success_response()
        except BaseServiceException as e:
            raise map_service_to_controller_exc(e, {})


class ProjectController(BaseController):
    """Контроллер проектов."""

    @staticmethod
    def create(request: flask.Request, repo: DataRepository, authorizer: Authorizer, user_id: int):
        """Создаёт проект."""
        project = request.json.get('project')
        workspace_id = Int('workspace_id', request.json.get('workspace_id'), ErrorCodes.incorrect_workspace_id.value)

        if not project:
            raise IncorrectParamException({'project': {VALUE: None, MESSAGE: 'No project in request'}})
        if not workspace_id.value:
            raise IncorrectParamException({'workspace_id': {VALUE: None, MESSAGE: 'workspace_id is required'}})

        try:
            project_id = services.ProjectService.create(project, workspace_id.value, user_id, repo, authorizer)
            return utl.form_success_response({'project_id': project_id})
        except BaseServiceException as e:
            raise map_service_to_controller_exc(e, {})

    @staticmethod
    @utl.get_request
    def get(request: flask.Request, repo: DataRepository, limit: int = None, offset: int = None, require_last_num: bool = False):
        """Получает проекты."""
        ids = IntList(CommonStruct.ids, request.args.getlist(CommonStruct.ids), ErrorCodes.incorrect_id.value)
        workspace_ids = IntList('workspace_ids', request.args.getlist('workspace_ids'), ErrorCodes.incorrect_workspace_id.value)
        creator_ids = IntList(CommonStruct.creator_ids, request.args.getlist(CommonStruct.creator_ids), ErrorCodes.incorrect_creator_ids.value)

        try:
            response = repo.get_projects(ids.value if ids.value else None,
                                         workspace_ids.value if workspace_ids.value else None,
                                         creator_ids.value if creator_ids.value else None,
                                         limit, offset, require_last_num)
            return utl.form_get_success_response(response.content, response.last_record_num, response.records_left)
        except BaseRepoException as e:
            raise map_repo_to_controller_exc(e, {})

    @staticmethod
    def update(request: flask.Request, repo: DataRepository, authenticator: Authenticator, authorizer: Authorizer, user_id: int):
        """Обновляет проект."""
        project = request.json.get('project')
        if not project:
            raise IncorrectParamException({'project': {VALUE: None, MESSAGE: 'No project in request'}})

        try:
            services.ProjectService.update(project, user_id, repo, authorizer)
            return utl.form_success_response()
        except BaseServiceException as e:
            raise map_service_to_controller_exc(e, {})

    @staticmethod
    def delete(request: flask.Request, repo: DataRepository, authenticator: Authenticator, authorizer: Authorizer, user_id: int):
        """Удаляет проекты."""
        ids = IntList(CommonStruct.ids, request.args.getlist(CommonStruct.ids), ErrorCodes.incorrect_id.value)
        try:
            services.ProjectService.delete(tuple(ids.value), user_id, repo, authorizer)
            return utl.form_success_response()
        except BaseServiceException as e:
            raise map_service_to_controller_exc(e, {})

    @staticmethod
    def add_student_to_project(request: flask.Request, repo: DataRepository, authenticator: Authenticator, authorizer: Authorizer, user_id: int, project_id: int):
        """Добавляет студента в проект."""
        user_ids = IntList(CommonStruct.ids, request.args.getlist(CommonStruct.ids), ErrorCodes.incorrect_user_ids.value)
        try:
            for uid in user_ids.value:
                services.ProjectService.add_student_to_project(uid, project_id, repo, authorizer, user_id)
            return utl.form_success_response()
        except BaseServiceException as e:
            raise map_service_to_controller_exc(e, {})

    @staticmethod
    def remove_student_from_project(request: flask.Request, repo: DataRepository, authenticator: Authenticator, authorizer: Authorizer, user_id: int, project_id: int, target_user_id: int):
        """Удаляет студента из проекта."""
        try:
            services.ProjectService.delete_student_from_project(target_user_id, project_id, repo, authorizer, user_id)
            return utl.form_success_response()
        except BaseServiceException as e:
            raise map_service_to_controller_exc(e, {})

    @staticmethod
    def add_mentor_to_project(request: flask.Request, repo: DataRepository, authenticator: Authenticator, authorizer: Authorizer, user_id: int, project_id: int):
        """Добавляет наставника в проект."""
        user_ids = IntList(CommonStruct.ids, request.args.getlist(CommonStruct.ids), ErrorCodes.incorrect_user_ids.value)
        try:
            for uid in user_ids.value:
                services.ProjectService.add_mentor_to_project(uid, project_id, repo, authorizer, user_id)
            return utl.form_success_response()
        except BaseServiceException as e:
            raise map_service_to_controller_exc(e, {})

    @staticmethod
    def remove_mentor_from_project(request: flask.Request, repo: DataRepository, authenticator: Authenticator, authorizer: Authorizer, user_id: int, project_id: int, target_user_id: int):
        """Удаляет наставника из проекта."""
        try:
            services.ProjectService.delete_mentor_from_project(target_user_id, project_id, repo, authorizer, user_id)
            return utl.form_success_response()
        except BaseServiceException as e:
            raise map_service_to_controller_exc(e, {})

    @staticmethod
    def get_project_users(request: flask.Request, repo: DataRepository, project_id: int, limit: int = None, offset: int = None, require_last_num: bool = False):
        """Получает пользователей проекта."""
        try:
            response = repo.get_project_users(project_id, limit, offset, require_last_num)
            return utl.form_get_success_response(response.content, response.last_record_num, response.records_left)
        except BaseRepoException as e:
            raise map_repo_to_controller_exc(e, {})


class PersonalTaskEventController(BaseController):
    """Контроллер личных задач-мероприятий."""

    @staticmethod
    @utl.get_request
    def get(request: flask.Request, repo: DataRepository, limit: int = None, offset: int = None,
            require_last_num: bool = False):
        ids = IntList(CommonStruct.ids, request.args.getlist(CommonStruct.ids),
                      ErrorCodes.incorrect_personal_tasks_ids.value)
        user_id = Int(CommonStruct.user_id, request.args.get(CommonStruct.user_id), ErrorCodes.incorrect_user_id.value)

        try:
            response = repo.get_personal_task_events_by_user(ids.value, user_id.value, limit, offset, require_last_num)
        except BaseRepoException as e:
            raise map_repo_to_controller_exc(e, {})

        return utl.form_success_response(content=response.content)


class WSTaskEventController(BaseController):
    """Контроллер задач-мероприятий РП."""

    @staticmethod
    @utl.get_request
    def get(request: flask.Request, repo: DataRepository, limit: int = None,
            offset: int = None, require_last_num: bool = False):
        ids = IntList(CommonStruct.ids, request.args.getlist(CommonStruct.ids),
                      ErrorCodes.incorrect_ws_task_events_ids.value)
        workspace_id = Int(CommonStruct.workspace_id, request.args.get(CommonStruct.workspace_id),
                           ErrorCodes.incorrect_workspace_id.value)
        executor_id = Int(CommonStruct.executor_id, request.args.get(CommonStruct.executor_id),
                          ErrorCodes.incorrect_executor_id.value)

        response = repo.get_ws_task_events(ids.value, workspace_id.value, executor_id.value, limit, offset, require_last_num)
        return utl.form_success_response(content=response.content)

