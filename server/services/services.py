"""Сервисы."""

from common.base import CommonStruct, DBFields, get_datetime_now
from server.database.repository import DataRepository
from server.data_const import DataStruct, DBStruct, Permissions
import server.services.exceptions as err
from common.logger import config_logger, SERVER
from server.api.base import LOG_DIR, MAX_BACKUP_FILES, MAX_FILE_SIZE, LOGGING_LEVEL

logger = config_logger(__name__, SERVER, LOG_DIR, MAX_BACKUP_FILES, MAX_FILE_SIZE, LOGGING_LEVEL)

# ToDo: обеспечивать формат даты из CommonStruct.datetime_format


class BaseService:
    pass


class UserService(BaseService):

    def get_days_no_break(self, repo: DataRepository, user_id: int):
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
    def create(workspace: dict, user_id: int, repo: DataRepository, authorizer) -> int:
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

    @staticmethod
    def add_user_to_workspace(user_id: int, workspace_id: int, repo: DataRepository, authorizer, requesting_user_id: int):
        """Добавляет пользователя в рабочее пространство."""
        if not authorizer.check_permissions(requesting_user_id, Permissions.invite.value):
            raise err.AccessDenied(f'Your role can\'t invite')

        repo.add_workspace_user(user_id, workspace_id)

    @staticmethod
    def delete_user_from_workspace(user_id: int, workspace_id: int, repo: DataRepository, authorizer, requesting_user_id: int):
        """Удаляет пользователя из рабочего пространства."""
        if not authorizer.check_permissions(requesting_user_id, Permissions.kick.value):
            raise err.AccessDenied(f'Your role can\'t kick')

        repo.delete_workspace_user(user_id, workspace_id)

    @staticmethod
    def get_user_role(user_id: int, workspace_id: int, repo: DataRepository) -> dict | None:
        """Получает роль пользователя в рабочем пространстве."""
        role_data = repo.get_role_by_user_id(workspace_id, user_id)
        if role_data.content:
            return role_data.content[0]
        return None

    @staticmethod
    def set_user_role(user_id: int, workspace_id: int, role_id: int, repo: DataRepository, authorizer, requesting_user_id: int):
        """Устанавливает роль пользователю в рабочем пространстве."""
        if not authorizer.check_permissions(requesting_user_id, Permissions.set_roles.value):
            raise err.AccessDenied(f'Your role can\'t set_roles')

        # Проверяем, что роль существует и принадлежит этому workspace
        role_data = repo.get_role_by_id_workspace(role_id, workspace_id)
        if not role_data.content:
            raise err.IncorrectParamError('role', f'Role with id {role_id} not found in workspace {workspace_id}')

        # Добавляем пользователя в роль
        role = role_data.content[0]
        if user_id not in role[DBFields.users]:
            role[DBFields.users].append(user_id)
            repo.update_ws_roles([role])


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
    def create(ws_tasks: tuple[dict, ...], project_id: int, user_id: int, repo: DataRepository, authorizer):
        """
        Создаёт задачи проекта.
        Формирует словарь параметров задачи и передаёт его в метод репозитория add_ws_tasks.
        Добавляет creator_id, entrusted_id (равны user_id) и status_id = 1.
        """
        # Проверяем доступ к созданию задач
        if not authorizer.check_permissions(user_id, Permissions.create_task.value):
            role_data = repo.get_role_by_user_id(project_id, user_id)
            if role_data.content:
                role_name = role_data.content[0].get(DBFields.name, 'unknown')
            else:
                role_name = 'unknown'
            raise err.AccessDenied(f'Your role ({role_name}) can\'t create_task')

        for task in ws_tasks:
            task[DBFields.creator_id] = user_id
            task[DBFields.entrusted_id] = user_id
            task[DBFields.status_id] = 1

        repo.add_ws_tasks(ws_tasks)

    @staticmethod
    def update(ws_tasks: tuple[dict, ...], user_id: int, repo: DataRepository, authorizer):
        """
        Редактирует поля задач.
        Проверяет роль пользователя через authorizer перед обновлением.
        """
        # Проверяем доступ к редактированию задач
        if not authorizer.check_permissions(user_id, Permissions.edit_task.value):
            raise err.AccessDenied(f'Your role can\'t edit_task')

        for task in ws_tasks:
            task_id = task.get(DBFields.id)
            if not task_id:
                raise err.IncorrectParamError('task', f'Task must have id field: {task}')

            # Получаем задачу для проверки существования
            task_data = repo.get_ws_tasks([task_id])
            if not task_data.content:
                raise err.IncorrectParamError('task', f'There is no task with id {task_id}')

            task[DBFields.updated_at] = get_datetime_now()

        repo.update_ws_tasks(ws_tasks)

    @staticmethod
    def delete(task_ids: tuple[int, ...], user_id: int, repo: DataRepository, authorizer):
        """
        Удаляет задачи по их ID.
        Проверяет роль пользователя через authorizer перед удалением.
        """
        # Проверяем доступ к удалению задач
        if not authorizer.check_permissions(user_id, Permissions.del_task.value):
            raise err.AccessDenied(f'Your role can\'t del_task')

        for task_id in task_ids:
            # Получаем задачу для проверки существования
            task_data = repo.get_ws_tasks([task_id])
            if not task_data.content:
                raise err.IncorrectParamError('task', f'There is no task with id {task_id}')

        repo.delete_ws_tasks_by_id(task_ids)


class ProjectService(BaseService):
    """Сервис проектов."""

    @staticmethod
    def create(project: dict, workspace_id: int, user_id: int, repo: DataRepository, authorizer) -> int:
        """
        Создаёт проект в рабочем пространстве.
        Возвращает ID созданного проекта.
        """
        # Проверяем доступ к созданию проектов
        if not authorizer.check_permissions(user_id, Permissions.set_project.value):
            raise err.AccessDenied(f'Your role can\'t set_project')

        if DBFields.name not in project:
            raise err.IncorrectParamError('project', f'No name in project: {project}')
        if len(project.get(DBFields.name)) > CommonStruct.max_name_length:
            raise err.IncorrectParamError('project', f'Length of the name of a project must be in range 1-{CommonStruct.max_name_length}')
        if DBFields.description in project and len(project.get(DBFields.description)) > CommonStruct.max_description_length:
            raise err.IncorrectParamError('project', f'Length of the description of a project must be '
                                                      f'equal to {CommonStruct.max_description_length} or be less.')

        project[DBFields.workspace_id] = workspace_id
        project[DBFields.creator_id] = user_id

        result = repo.add_projects([project])
        return result.ids[0]

    @staticmethod
    def update(project: dict, user_id: int, repo: DataRepository, authorizer):
        """Обновляет проект."""
        if not authorizer.check_permissions(user_id, Permissions.set_project.value):
            raise err.AccessDenied(f'Your role can\'t set_project')

        project_id = project.get(DBFields.id)
        if not project_id:
            raise err.IncorrectParamError('project', 'Project must have id field')

        project[DBFields.updated_at] = get_datetime_now()
        repo.update_projects([project])

    @staticmethod
    def delete(project_ids: tuple[int, ...], user_id: int, repo: DataRepository, authorizer):
        """Удаляет проекты по ID."""
        if not authorizer.check_permissions(user_id, Permissions.del_project.value):
            raise err.AccessDenied(f'Your role can\'t del_project')

        repo.delete_projects(project_ids)

    @staticmethod
    def add_student_to_project(user_id: int, project_id: int, repo: DataRepository, authorizer, requesting_user_id: int):
        """Добавляет студента в проект."""
        if not authorizer.check_permissions(requesting_user_id, Permissions.invite.value):
            raise err.AccessDenied(f'Your role can\'t invite')

        repo.add_project_user(user_id, project_id)

    @staticmethod
    def delete_student_from_project(user_id: int, project_id: int, repo: DataRepository, authorizer, requesting_user_id: int):
        """Удаляет студента из проекта."""
        if not authorizer.check_permissions(requesting_user_id, Permissions.kick.value):
            raise err.AccessDenied(f'Your role can\'t kick')

        repo.delete_project_user(user_id, project_id)

    @staticmethod
    def add_mentor_to_project(user_id: int, project_id: int, repo: DataRepository, authorizer, requesting_user_id: int):
        """Добавляет наставника в проект."""
        if not authorizer.check_permissions(requesting_user_id, Permissions.invite.value):
            raise err.AccessDenied(f'Your role can\'t invite')

        repo.add_project_user(user_id, project_id)

    @staticmethod
    def delete_mentor_from_project(user_id: int, project_id: int, repo: DataRepository, authorizer, requesting_user_id: int):
        """Удаляет наставника из проекта."""
        if not authorizer.check_permissions(requesting_user_id, Permissions.kick.value):
            raise err.AccessDenied(f'Your role can\'t kick')

        repo.delete_project_user(user_id, project_id)


if __name__ == '__main__':
    pass
