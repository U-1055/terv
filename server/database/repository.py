from sqlalchemy.orm.session import Session, sessionmaker, Select, Query
from sqlalchemy.sql import select, insert, update, delete, func

import typing as tp

import server.database.models.common_models as cm
import server.database.models.roles as roles


def repo_request(func: tp.Callable):  # Декоратор для обработки limit\offset

    def complete(*args, **kwargs):
        limit = kwargs.get('limit')
        offset = kwargs.get('offset')

        result = func(*args, **kwargs)

        if not limit:
            limit = len(result)
        if not offset:
            offset = 0

        if offset < 0:   # Некорректные значения limit\offset
            offset = 0
        if limit < 0:
            limit = None

        if offset >= len(result):  # offset больше\равен индексу последнего элемента
            return {'left': len(result), 'result': []}
        if limit >= len(result) or limit + offset >= len(result):  # limit больше длины или limit с offset больше длины => лимит отсутствует
            limit = None

        result = result[offset:]
        last_record_idx = len(result) - 1

        if limit:
            result = result[:limit]
        return {'left': result - last_record_idx - 1, 'result': result}

    return complete


class DataRepository:

    def __init__(self, session_maker: sessionmaker):
        self._session_maker = session_maker

    def _get_permissions(self, query: Select) -> tuple[str]:
        with self._session_maker() as session, session.begin():
            perm_ids = session.execute(query)
            permissions = session.execute(
                select(roles.Permission.type).where(roles.Permission.id.in_(perm_ids))).scalars().all()

        return permissions

    def _execute_select(self, query: Select, limit: int = None, offset: int = None) -> list:
        with self._session_maker() as session, session.begin():
            result = session.execute(query.limit(limit).offset(offset)).scalars().all()
            return [model.serialize() for model in result]

    def _execute_delete(self, ids: tuple[int, ...], base_model: tp.Type[cm.Base]):
        with self._session_maker() as session, session.begin():
            session.execute(delete(base_model).where(base_model.id.in_(ids)))

    def _execute_insert(self, models: tuple[dict, ...], base_model: tp.Type[cm.Base]):
        with self._session_maker() as session, session.begin():
            session.add_all([base_model(**model) for model in models])

    def _execute_update(self, models: tuple[dict, ...], base_model: tp.Type[cm.Base]):
        with self._session_maker() as session, session.begin():
            session.execute(update(base_model).where(base_model.id.in_(model['id'] for model in models)), models)

    def get_users(self, usernames: tuple[str, ...] = None, email: str = None, limit: int = None, offset: int = None) -> list:
        """
        Базовый метод получения таблиц пользователей.

        :param username:
        :param email:
        :param offset:
        :param limit:
        :return:
        """

        query = select(cm.User)
        if usernames:
            query = query.where(cm.User.username.in_(usernames))
        if email:
            query = query.where(cm.User.email == email)

        with self._session_maker() as session, session.begin():
            session.execute(select(func.count('user')))

        return self._execute_select(query, limit, offset)

    def get_workflows(self,
                      workflow_ids: tuple[int] = None,
                      name: str = None,
                      limit: int = None,
                      offset: int = None
                      ):
        """
        Возвращает рабочие пространства (Workflows).
        :param workflow_ids:
        :param name:
        :param full_compliance:
        :param users_ids:
        :param limit:
        :param offset:
        :return:
        """

        query = select(cm.Workflow)
        if workflow_ids:
            query = query.where(cm.Workflow.id.in_(workflow_ids))
        if name:
            query = query.where(cm.Workflow.name.contains(name))

        return self._execute_select(query, limit, offset)

    def delete_workflows(self, workflows_ids: tuple[int]):
        self._execute_delete(workflows_ids, cm.Workflow)

    def update_users(self, models: tuple[dict, ...]):
        self._execute_update(models, cm.User)

    def add_users(self, models: tuple[dict, ...]):
        self._execute_insert(models, cm.User)

    def delete_users(self, ids: tuple[int, ...]):
        self._execute_delete(ids, cm.User)

    def add_workflows(self, models: tuple[dict, ...]):
        self._execute_insert(models, cm.Workflow)

    def get_task_permissions(self, task_id: int, role_id: int) -> tuple[str]:
        query = (select(roles.WFRoleTask.permissions).
                 where(roles.WFRoleTask.task_id == task_id).
                 where(roles.WFRoleTask.role_id == role_id)
                 )
        return self._get_permissions(query)

    def get_project_permissions(self, project_id: int, role_id: int) -> tuple[str]:
        query = (select(roles.WFRoleProject.permissions).
                 where(roles.WFRoleProject.project_id == project_id).
                 where(roles.WFRoleProject.role_id == role_id)
                 )
        return self._get_permissions(query)

    def get_document_permissions(self, document_id: int, role_id: int) -> tuple[str]:
        query = (select(roles.WFRoleDocument.permissions).
                 where(roles.WFRoleDocument.document_id == document_id).
                 where(roles.WFRoleDocument.role_id == role_id)
                 )
        return self._get_permissions(query)

    def get_daily_event_permissions(self, daily_event_id: int, role_id: int) -> tuple[str]:
        query = (select(roles.WFRoleDailyEvent.permissions).
                 where(roles.WFRoleDailyEvent.daily_event_id == daily_event_id).
                 where(roles.WFRoleDailyEvent.role_id == role_id)
                 )
        return self._get_permissions(query)

    def get_many_days_event_permissions(self, many_days_event_id: int, role_id: int) -> tuple[str]:
        query = (select(roles.WFRoleManyDaysEvent.permissions).
                 where(roles.WFRoleManyDaysEvent.many_days_event_id == many_days_event_id).
                 where(roles.WFRoleManyDaysEvent.role_id == role_id)
                 )
        return self._get_permissions(query)


if __name__ == '__main__':

    # server method example
    def get_workflows(workflows_ids: tuple[int], repo: DataRepository) -> dict:
        repo.get_workflows()


    from server.database.models.base import init_db, config_db

    engine = init_db()
    config_db(engine)
    repo = DataRepository(sessionmaker(bind=engine))
    workflows = repo.get_workflows()
    