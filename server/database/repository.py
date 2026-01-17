from sqlalchemy.orm.session import Session, sessionmaker, Select, Query
from sqlalchemy.sql import select, insert, update, delete, func

import typing as tp
from dataclasses import dataclass

import server.database.models.common_models as cm
import server.database.models.roles as roles


class DataRepository:

    """
    Репозиторий базы данных. В ответах на запросы получения данных возвращает объект RepoResponse.
    RepoResponse.content - список сериализованных моделей, полученных в ответе.
    RepoResponse.last_record_num - номер последней модели (если в запрос передан limit, offset или require_last_rec_num,
    иначе - None)
    """

    def __init__(self, session_maker: sessionmaker):
        self._session_maker = session_maker

    def _get_permissions(self, query: Select) -> tuple[str]:
        with self._session_maker() as session, session.begin():
            perm_ids = session.execute(query)
            permissions = session.execute(
                select(roles.Permission.type).where(roles.Permission.id.in_(perm_ids))).scalars().all()

        return permissions

    def _execute_select(self, query: Select, limit: int = None, offset: int = None, require_last_rec_num: bool = False) -> 'RepoResponse':
        with self._session_maker() as session, session.begin():
            result = session.execute(query.limit(limit).offset(offset)).scalars().all()
            response = RepoResponse(content=[model.serialize() for model in result])
            if limit or offset or require_last_rec_num:  # Поиск номера последней таблицы
                results_num = result.count(cm.Base)
                last_rec_num = results_num + offset
                response.last_record_num = last_rec_num

            return response

    def _execute_delete(self, ids: tuple[int, ...], base_model: tp.Type[cm.Base]):
        with self._session_maker() as session, session.begin():
            session.execute(delete(base_model).where(base_model.id.in_(ids)))

    def _execute_insert(self, models: tuple[dict, ...], base_model: tp.Type[cm.Base]):
        with self._session_maker() as session, session.begin():
            session.add_all([base_model(**model) for model in models])

    def _execute_update(self, models: tuple[dict, ...], base_model: tp.Type[cm.Base]):
        with self._session_maker() as session, session.begin():
            session.execute(update(base_model).where(base_model.id.in_(model['id'] for model in models)), models)

    def get_users(self, usernames: tuple[str, ...] = None, email: str = None, require_last_rec_num: bool = False, limit: int = None, offset: int = 0) -> 'RepoResponse':

        query = select(cm.User)
        if usernames:
            query = query.where(cm.User.username.in_(usernames))
        if email:
            query = query.where(cm.User.email == email)

        return self._execute_select(query, limit, offset, require_last_rec_num)

    def get_workflows(self,
                      workflow_ids: tuple[int] = None,
                      name: str = None,
                      require_last_rec_num: bool = False,
                      limit: int = None,
                      offset: int = 0
                      ) -> 'RepoResponse':
        """
        Возвращает рабочие пространства (Workflows).
        :param workflow_ids:
        :param name:
        :param limit:
        :param offset:
        :return:
        """

        query = select(cm.Workflow)
        if workflow_ids:
            query = query.where(cm.Workflow.id.in_(workflow_ids))
        if name:
            query = query.where(cm.Workflow.name.contains(name))

        return self._execute_select(query, require_last_rec_num, limit, offset)

    def get_wf_tasks(self, wf_tasks_ids: list[int], limit: int = None, offset: int = 0, require_last_num: bool = False) -> 'RepoResponse':
        query = select(cm.WFTask)
        if wf_tasks_ids:
            query = query.where(cm.WFTask.id.in_(wf_tasks_ids))

        return self._execute_select(query, limit, offset, require_last_num)

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


@dataclass
class RepoResponse:
    """Ответ DataRepository."""
    content: list
    last_record_num: int = None


if __name__ == '__main__':
    pass
