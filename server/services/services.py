"""Сервисы."""

from common.base import CommonStruct, DBFields
from server.database.repository import DataRepository
from server.data_const import DBStruct
import server.services.exceptions as err
from common.logger import config_logger, SERVER
from server.api.base import LOG_DIR, MAX_BACKUP_FILES, MAX_FILE_SIZE, LOGGING_LEVEL

logger = config_logger(__name__, SERVER, LOG_DIR, MAX_BACKUP_FILES, MAX_FILE_SIZE, LOGGING_LEVEL)

# ToDo: обеспечивать формат даты из CommonStruct.datetime_format


class BaseService:
    pass


class UserService(BaseService):
    pass


class WorkspaceService(BaseService):
    @staticmethod
    def delete(workspace_id: int, repo: DataRepository):
        pass

    @staticmethod
    def add_users(user_ids: tuple[int, ...], workspace_id: int, repo: DataRepository):
        """
        Добавляет пользователя в РП. Устанавливает ему стандартную роль. Пользователи, уже имеющиеся в РП, добавлены
        не будут. (Исключений при этом не вызывается)
        """
        default_role_id = repo.get_workspace_default_role_id(workspace_id)  # ID стандартной роли
        if not default_role_id:
            raise err.IncorrectParamError('workspace', f'There is no default role in this Workspace: ws_id: {workspace_id}')

        content = repo.get_roles_by_id([default_role_id]).content
        if not content:
            raise err.IncorrectParamError('workspace', f'There is no role with default role id: {default_role_id}')
        default_role = content[0]

        workspace_content = repo.get_workspaces([workspace_id]).content
        if not workspace_content:
            raise err.IncorrectParamError('workspace', f'There is no workspace with id {workspace_id}')
        workspace = workspace_content[0]

        role_users = set(default_role[DBFields.users])  # Добавляем пользователей в роль
        role_users.update(user_ids)
        default_role[DBFields.users] = list(role_users)

        workspace_users = set(workspace[DBFields.users])  # Добавляем пользователей в РП
        workspace_users.update(user_ids)
        workspace[DBFields.users] = list(workspace_users)

        repo.update_ws_roles([default_role])  # Отправляем в БД
        repo.update_workspaces([workspace])

    @staticmethod
    def delete_users(workspace_id: int, users_ids: tuple[int], repo: DataRepository):  # ToDo: удаление из всех связанных с РП сущностями
        workspace_content = repo.get_workspaces([workspace_id]).content
        if not workspace_content:
            raise err.IncorrectParamError('workspace', f'There is no workspace with id {workspace_id}')
        workspace = workspace_content[0]

        default_role_id = workspace.get(DBFields.default_role_id)
        default_role_content = repo.get_roles_by_id([default_role_id]).content
        if not default_role_content:
            logger.error(f'There is no role with default role id: {default_role_id}. Workspace: {workspace}.'
                          f' (Excepting during deleting_users from workspace)')
            raise err.IncorrectParamError('workspace', f'There is no role with default role id: {default_role_id}')
        default_role = default_role_content[0]

        for user_id in users_ids:
            if user_id in workspace[DBFields.users]:  # Удаление из РП
                workspace[DBFields.users].remove(user_id)
            if user_id in default_role[DBFields.users]:  # Удаление из роли
                default_role[DBFields.users].remove(user_id)
        repo.update_workspaces([workspace])
        repo.update_ws_roles([default_role])

    @staticmethod
    def create(workspace: dict, user_id: int, repo: DataRepository) -> int:
        """
        Создаёт РП. Добавляет туда пользователя с id = user_id и присваивает ему роль создателя (creator role).
        Создаёт creator role и default role в РП.
        Возвращает ID созданной модели Workspace в БД.
        """

        if DBFields.name not in workspace:
            raise err.IncorrectParamError('workspace', f'No name in workspace: {workspace}')
        if len(workspace.get(DBFields.name)) > CommonStruct.max_name_length:
            raise err.IncorrectParamError('workspace', f'Length of the name of a workspace must be in range 1-{CommonStruct.max_name_length}')
        if DBFields.description in workspace and len(workspace.get(DBFields.description)) > CommonStruct.max_description_length:
            raise err.IncorrectParamError('workspace', f'Length of the description of a workspace must be '
                                                      f'equal to {CommonStruct.max_description_length} or be less.')

        # Обновляем поля workspace
        workspace[DBFields.users] = [user_id]
        workspace[DBFields.creator_id] = user_id
        result = repo.add_workspaces([workspace])  # Вносим РП в БД
        workspace_id = result.ids[0]
        workspace = repo.get_workspaces([workspace_id]).content[0]  # Получаем РП (чтобы узнать ID)

        default_role = {DBFields.name: DBStruct.default_role, DBFields.workspace_id: workspace_id}
        creator_role = {DBFields.name: DBStruct.creator_role, DBFields.workspace_id: workspace_id}

        result = repo.add_ws_roles([default_role, creator_role])
        default_role_id = result.ids[0]
        creator_role_id = result.ids[1]

        workspace[DBFields.default_role_id] = default_role_id
        creator_role = repo.get_roles_by_id([creator_role_id]).content[0]
        creator_role[DBFields.users] = [user_id]

        repo.update_workspaces([workspace])  # Обновляем РП и роли
        repo.update_ws_roles([creator_role])

        return workspace_id


class WSDailyEventService(BaseService):
    """Сервис однодневного события РП."""

    @staticmethod
    def create(ws_daily_events: tuple[dict, ...], workspace_id: int, repo: DataRepository):
        for event in ws_daily_events:
            event[CommonStruct.workspace_id] = workspace_id

        repo.add_ws_daily_events(ws_daily_events)

    @staticmethod
    def update(ws_daily_events: tuple[dict, ...], repo: DataRepository):
        repo.update_ws_daily_events(ws_daily_events)

    @staticmethod
    def delete(ws_daily_events_ids: tuple[int, ...], repo: DataRepository):
        repo.delete_ws_daily_events(ws_daily_events_ids)


class WSManyDaysEventService(BaseService):
    """Сервис многодневного события РП."""

    @staticmethod
    def create(ws_many_days_events: tuple[dict, ...], workspace_id: int, repo: DataRepository):
        for event in ws_many_days_events:
            event[CommonStruct.workspace_id] = workspace_id
        repo.add_ws_many_days_events(ws_many_days_events)

    @staticmethod
    def update(ws_many_days_events: tuple[dict, ...], workspace_id: int, repo: DataRepository):
        repo.update_ws_many_days_events(ws_many_days_events)

    @staticmethod
    def delete(ws_many_days_events_ids: tuple[int, ...], repo: DataRepository):
        repo.delete_ws_many_days_events(ws_many_days_events_ids)


class WSTaskService(BaseService):
    """Сервис задач РП."""

    @staticmethod
    def create(ws_tasks: tuple[dict, ...], workspace_id: int, repo: DataRepository):
        pass

    @staticmethod
    def update(ws_tasks: tuple[dict, ...], repo: DataRepository):
        pass

    @staticmethod
    def update_status(ws_tasks: tuple[dict, ...]):
        pass


class ProjectService(BaseService):
    pass


if __name__ == '__main__':
    pass
