"""Сервисы."""
import logging

import sqlalchemy.exc

from common.base import CommonStruct, DBFields
from server.database.repository import DataRepository
from server.utils.api_utils import db_exceptions_handler
from server.data_const import DBStruct
import server.database.models.common_models as cm
import server.database.models.roles as roles
import server.database.schemes.common_schemes as cs
import server.services.errors as err

# ToDo: обеспечивать формат даты из CommonStruct.datetime_format


class BaseService:
    pass


class UserService(BaseService):
    pass


class WorkflowService(BaseService):
    @staticmethod
    @db_exceptions_handler
    def delete(workflow_id: int, repo: DataRepository):
        pass

    @staticmethod
    @db_exceptions_handler
    def add_users(user_ids: tuple[int, ...], workflow_id: int, repo: DataRepository):
        """
        Добавляет пользователя в РП. Устанавливает ему стандартную роль. Пользователи, уже имеющиеся в РП, добавлены
        не будут. (Исключений при этом не вызывается)
        """
        default_role_id = repo.get_workflow_default_role_id(workflow_id)  # ID стандартной роли
        if not default_role_id:
            raise err.IncorrectParamError('workflow', f'There is no default role in this Workflow: wf_id: {workflow_id}')

        content = repo.get_roles_by_id([default_role_id]).content
        if not content:
            raise err.IncorrectParamError('workflow', f'There is no role with default role id: {default_role_id}')
        default_role = content[0]

        workflow_content = repo.get_workflows([workflow_id]).content
        if not workflow_content:
            raise err.IncorrectParamError('workflow', f'There is no workflow with id {workflow_id}')
        workflow = workflow_content[0]

        role_users = set(default_role[DBFields.users])  # Добавляем пользователей в роль
        role_users.update(user_ids)
        default_role[DBFields.users] = list(role_users)

        workflow_users = set(workflow[DBFields.users])  # Добавляем пользователей в РП
        workflow_users.update(user_ids)
        workflow[DBFields.users] = list(workflow_users)

        repo.update_wf_roles([default_role])  # Отправляем в БД
        repo.update_workflows([workflow])

    @staticmethod
    @db_exceptions_handler
    def delete_users(workflow_id: int, users_ids: tuple[int], repo: DataRepository):  # ToDo: удаление из всех связанных с РП сущностями
        workflow_content = repo.get_workflows([workflow_id]).content
        if not workflow_content:
            raise err.IncorrectParamError('workflow', f'There is no workflow with id {workflow_id}')
        workflow = workflow_content[0]

        default_role_id = workflow.get(DBFields.default_role_id)
        default_role_content = repo.get_roles_by_id([default_role_id]).content
        if not default_role_content:
            logging.error(f'There is no role with default role id: {default_role_id}. Workflow: {workflow}.'
                          f' (Excepting during deleting_users from workflow)')
            raise err.IncorrectParamError('workflow', f'There is no role with default role id: {default_role_id}')
        default_role = default_role_content[0]

        for user_id in users_ids:
            if user_id in workflow[DBFields.users]:  # Удаление из РП
                workflow[DBFields.users].remove(user_id)
            if user_id in default_role[DBFields.users]:  # Удаление из роли
                default_role[DBFields.users].remove(user_id)
        repo.update_workflows([workflow])
        repo.update_wf_roles([default_role])

    @staticmethod
    @db_exceptions_handler
    def create(workflow: dict, user_id: int, repo: DataRepository) -> int:
        """
        Создаёт РП. Добавляет туда пользователя с id = user_id и присваивает ему роль создателя (creator role).
        Создаёт creator role и default role в РП.
        Возвращает ID созданной модели Workflow в БД.
        """

        if DBFields.name not in workflow:
            raise err.IncorrectParamError('workflow', f'No name in workflow: {workflow}')
        if len(workflow.get(DBFields.name)) > CommonStruct.max_name_length:
            raise err.IncorrectParamError('workflow', f'Length of the name of a workflow must be in range 1-{CommonStruct.max_name_length}')
        if DBFields.description in workflow and len(workflow.get(DBFields.description)) > CommonStruct.max_description_length:
            raise err.IncorrectParamError('workflow', f'Length of the description of a workflow must be '
                                                      f'equal to {CommonStruct.max_description_length} or be less.')

        workflow[DBFields.creator] = user_id  # Обновляем поля workflow
        workflow[DBFields.users] = [user_id]
        workflow[DBFields.creator_id] = user_id
        result = repo.add_workflows([workflow])  # Вносим РП в БД
        workflow_id = result.ids[0]
        workflow = repo.get_workflows([workflow_id]).content[0]  # Получаем РП (чтобы узнать ID)

        default_role = {DBFields.name: DBStruct.default_role, DBFields.workflow_id: workflow_id}
        creator_role = {DBFields.name: DBStruct.creator_role, DBFields.workflow_id: workflow_id}

        result = repo.add_wf_roles([default_role, creator_role])
        default_role_id = result.ids[0]
        creator_role_id = result.ids[1]

        workflow[DBFields.default_role_id] = default_role_id
        creator_role = repo.get_roles_by_id([creator_role_id]).content[0]
        creator_role[DBFields.users] = [user_id]

        repo.update_workflows([workflow])  # Обновляем РП и роли
        repo.update_wf_roles([creator_role])

        return workflow_id


class ProjectService(BaseService):
    pass


if __name__ == '__main__':
    pass
