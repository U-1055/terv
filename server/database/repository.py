import datetime
import logging

from sqlalchemy.orm.session import sessionmaker, Select
from sqlalchemy.sql import select, delete
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

import typing as tp
from dataclasses import dataclass

import server.database.models.common_models as cm
import server.database.models.roles as roles
from common.base import DBFields, get_datetime_now
from server.database.schemes.base import schemes_models


class DataRepository:

    """
    Репозиторий базы данных. В ответах на запросы получения данных возвращает объект RepoSelectResponse.
    RepoSelectResponse.content - список сериализованных моделей, полученных в ответе.
    RepoSelectResponse.last_record_num - номер последней модели (если в запрос передан limit, offset или require_last_rec_num,
    иначе - None)
    """

    def __init__(self, session_maker: sessionmaker, launch_validation: bool = True):
        self._session_maker = session_maker
        if launch_validation:
            self._validate()

    def _validate(self):
        pass

    def _get_permissions(self, query: Select) -> tuple[str, ...]:
        with self._session_maker() as session, session.begin():
            perm_ids = session.execute(query)
            permissions = session.execute(
                select(roles.Permission.type).where(roles.Permission.id.in_(perm_ids))).scalars().all()

        return permissions

    def _execute_select(self, query: Select, limit: int = None, offset: int = None, require_last_rec_num: bool = False,
                        serialize: bool = True) -> 'RepoSelectResponse':
        with self._session_maker() as session, session.begin():

            result = session.execute(query.limit(limit).offset(offset)).scalars().all()
            if serialize:
                models_list = [model for model in result]
                if models_list:  # Сериализуем
                    scheme = schemes_models.get(type(models_list[0]))  # Получаем схему
                    if not scheme:
                        logging.critical(f'There is no scheme for model: {type(models_list[0])}.')
                    content = [scheme.dump(obj=model) for model in result]
                else:
                    content = []
            else:
                content = [model for model in result]

            response = RepoSelectResponse(content=content)
            if limit or offset or require_last_rec_num:  # Поиск номера последней таблицы
                results_num = len(response.content)
                last_rec_num = results_num + offset
                response.last_record_num = last_rec_num
                all_records = session.execute(query.offset(offset)).scalars().all()  # Получаем все записи
                all_records_num = len(all_records)

                response.records_left = all_records_num - results_num  # Осталось: все - полученные

            return response

    def _execute_delete(self, ids: tp.Iterable[int], base_model: tp.Type[cm.Base]):
        with self._session_maker() as session, session.begin():
            session.execute(delete(base_model).where(base_model.id.in_(ids)))

    def _execute_insert(self, models: tp.Iterable[dict], base_model: tp.Type[cm.Base]) -> 'RepoInsertResponse':
        with self._session_maker() as session, session.begin():
            schema: SQLAlchemyAutoSchema = schemes_models.get(base_model)
            schema.sqla_session = session
            models = [schema.load(model, session=session) for model in models]

            session.add_all(models)
            session.flush()
            return RepoInsertResponse(ids=tuple(int(db_model.id) for db_model in models))

    def _execute_update(self, models: tp.Iterable[dict], base_model: tp.Type[cm.Base]):
        """
        Перезаписывает указанные модели с введёнными данными. Автоматически десериализует модели, переданные в
        relationship-полях.
        """
        with self._session_maker() as session, session.begin():
            schema: SQLAlchemyAutoSchema = schemes_models.get(base_model)

            for model in models:  # Сериализация + обновление даты в updated_at
                for field in model:
                    if field == DBFields.updated_at:
                        model[field] = get_datetime_now()
                model = schema.load(model, session=session)
                session.merge(model)

    def get_users_by_username(self, usernames: tp.Iterable[str] = None, require_last_rec_num: bool = False, limit: int = None, offset: int = 0,
                              serialize: bool = True) -> 'RepoSelectResponse':

        query = select(cm.User)
        if usernames:
            query = query.where(cm.User.username.in_(usernames))

        return self._execute_select(query, limit, offset, require_last_rec_num, serialize)

    def get_users_by_email(self, emails: tp.Iterable[str] = None, require_last_rec_num: bool = False,
                               limit: int = None, offset: int = 0) -> 'RepoSelectResponse':
        query = select(cm.User).where(cm.User.email.in_(emails))
        return self._execute_select(query, limit, offset, require_last_rec_num)

    def get_users_by_id(self, ids: tp.Iterable[int], limit: int = None, offset: int = 0, require_last_rec_num: bool = False,
                        serialize: bool = True):
        query = select(cm.User).where(cm.User.id.in_(ids))
        return self._execute_select(query, limit, offset, require_last_rec_num, serialize)

    def get_workspaces(self,
                      workspace_ids: tp.Iterable[int] = None,
                      name: str = None,
                      require_last_rec_num: bool = False,
                      limit: int = None,
                      offset: int = 0,
                      serialize: bool = True
                      ) -> 'RepoSelectResponse':
        """
        Возвращает рабочие пространства (Workspaces).
        :param workspace_ids:
        :param name:
        :param limit:
        :param offset:
        :return:
        """

        query = select(cm.Workspace)
        if workspace_ids:
            query = query.where(cm.Workspace.id.in_(workspace_ids))
        if name:
            query = query.where(cm.Workspace.name.contains(name))

        return self._execute_select(query, limit, offset, require_last_rec_num, serialize)

    def get_user_hashed_password(self, login: str) -> str | None:
        """Возвращает хэш пароля пользователь с заданным логином. Если такого пользователя нет - возвращает None."""
        with self._session_maker() as session, session.begin():
            query = select(cm.User).where(cm.User.username == login)
            result = session.execute(query).scalars().all()
            if result:
                return result[0].hashed_password

    def update_ws_roles(self, models: tp.Iterable[dict]):
        self._execute_update(models, roles.wsRole)

    def get_ws_daily_event_by_notified_id(self, notified_id: int, limit: int = None, offset: int = 0,
                                          require_last_num: bool = False) -> 'RepoSelectResponse':
        query = select(cm.WSDailyEvent).where(cm.WSDailyEvent.notified.contains(notified_id))
        return self._execute_select(query, limit, offset, require_last_num)

    def get_ws_tasks_by_id(self, ws_tasks_ids: list[int] = None, limit: int = None, offset: int = 0, require_last_num: bool = False) -> 'RepoSelectResponse':
        query = select(cm.WSTask)
        if ws_tasks_ids:
            query = query.where(cm.WSTask.id.in_(ws_tasks_ids))

        return self._execute_select(query, limit, offset, require_last_num)

    def get_role_by_user_id(self, workspace_id: int, user_id: int):
        """Получает роль пользователя в проекте."""
        query = (select(roles.wsRole).where(roles.wsRole.workspace_id == workspace_id).
                 where(roles.wsRole.users.any(cm.User.id == user_id)))
        return self._execute_select(query)

    def get_workspace_default_role_id(self, workspace_id: int) -> int:
        """Получает ID роли РП по умолчанию."""
        query = select(cm.Workspace).where(cm.Workspace.id == workspace_id)
        result = self._execute_select(query)
        role_id = result.content[0].get(DBFields.id)

        return role_id

    def get_roles_by_id(self,
                        ids: tp.Iterable[int],
                        limit: int = None,
                        offset: int = None,
                        require_last_num: bool = False) -> 'RepoSelectResponse':
        """Получает роль РП (wsRole) по её ID."""
        query = select(roles.wsRole).where(roles.wsRole.id.in_(ids))
        return self._execute_select(query, limit, offset, require_last_num)

    def update_ws_tasks(self, models: list[cm.WSTask]):
        self._execute_update(models, cm.WSTask)

    def delete_ws_tasks_by_id(self, ids: list[int]):
        self._execute_delete(ids, cm.WSTask)

    def update_personal_tasks(self, models: list[cm.WSTask]):
        self._execute_update(models, cm.WSTask)

    def delete_workspaces(self, workspaces_ids: tp.Iterable[int]):
        self._execute_delete(workspaces_ids, cm.Workspace)

    def update_users(self, models: tp.Iterable[dict]):
        self._execute_update(models, cm.User)

    def add_users(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.User)

    def add_ws_tasks(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.User)

    def delete_users(self, ids: tp.Iterable[int]):
        self._execute_delete(ids, cm.User)

    def add_workspaces(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.Workspace)

    def add_personal_tasks(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.PersonalTask)

    def delete_personal_tasks(self, ids: tp.Iterable[int]):
        self._execute_delete(ids, cm.PersonalTask)

    def get_task_permissions(self, task_id: int, role_id: int) -> tuple[str]:
        query = (select(roles.wsRoleTask.permissions).
                 where(roles.wsRoleTask.task_id == task_id).
                 where(roles.wsRoleTask.role_id == role_id)
                 )
        return self._get_permissions(query)

    def get_project_permissions(self, project_id: int, role_id: int) -> tuple[str]:
        query = (select(roles.wsRoleProject.permissions).
                 where(roles.wsRoleProject.project_id == project_id).
                 where(roles.wsRoleProject.role_id == role_id)
                 )
        return self._get_permissions(query)

    def get_document_permissions(self, document_id: int, role_id: int) -> tuple[str]:
        query = (select(roles.wsRoleDocument.permissions).
                 where(roles.wsRoleDocument.document_id == document_id).
                 where(roles.wsRoleDocument.role_id == role_id)
                 )
        return self._get_permissions(query)

    def get_daily_event_permissions(self, daily_event_id: int, role_id: int) -> tuple[str]:
        query = (select(roles.wsRoleDailyEvent.permissions).
                 where(roles.wsRoleDailyEvent.daily_event_id == daily_event_id).
                 where(roles.wsRoleDailyEvent.role_id == role_id)
                 )
        return self._get_permissions(query)

    def get_personal_tasks_by_id(self, ids: tp.Iterable[int] = None, limit: int = None, offset: int = None,
                                 require_last_num: bool = False, serialize: bool = True):
        query = select(cm.PersonalTask)
        if ids:
            query = query.where(cm.PersonalTask.id.in_(ids))
        return self._execute_select(query, limit, offset, require_last_num, serialize)

    def get_ws_daily_events_by_id(self, ids: tp.Iterable[int] | list[int] = None, notified_id: int = None,
                                  limit: int = None, offset: int = None, require_last_num: bool = False,
                                  serialize: bool = True) -> 'RepoSelectResponse':
        query = select(cm.WSDailyEvent)
        if ids:
            query = query.where(cm.WSDailyEvent.id.in_(ids))
        if notified_id:
            query = query.where(cm.WSDailyEvent.notified.any(cm.User.id == notified_id))

        return self._execute_select(query, limit, offset, require_last_num, serialize)

    def add_ws_daily_events(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.WSDailyEvent)

    def delete_ws_daily_events(self, ids: tp.Iterable[int]):
        self._execute_delete(ids, cm.WSDailyEvent)

    def update_ws_daily_events(self, models: tp.Iterable[dict]):
        self._execute_update(models, cm.WSDailyEvent)

    def get_ws_many_days_events_by_id(self, ids: tp.Iterable[int] = None, notified_id: int = None, limit: int = None,
                                      offset: int = None, require_last_num: bool = False,
                                      serialize: bool = True) -> 'RepoSelectResponse':
        query = select(cm.WSManyDaysEvent)
        if ids:
            query = query.where(cm.WSManyDaysEvent.id.in_(ids))
        if notified_id:
            query = query.where(cm.WSManyDaysEvent.notified.any(cm.User.id == notified_id))

        return self._execute_select(query, limit, offset, require_last_num, serialize)

    def add_ws_many_days_events(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.WSManyDaysEvent)

    def delete_ws_many_days_events(self, ids: tp.Iterable[int]):
        self._execute_delete(ids, cm.WSManyDaysEvent)

    def update_ws_many_days_events(self, models: tp.Iterable[dict]):
        self._execute_update(models, cm.WSManyDaysEvent)

    def get_personal_daily_events_by_id(self, ids: tp.Iterable[int], owner_id: int = None, limit: int = None,
                                        offset: int = None, require_last_num: bool = False,
                                        serialize: bool = True) -> 'RepoSelectResponse':
        query = select(cm.PersonalDailyEvent)
        if ids:
            query = query.where(cm.PersonalDailyEvent.id.in_(ids))
        if owner_id:
            query = query.where(cm.PersonalDailyEvent.owner_id == owner_id)

        return self._execute_select(query, limit, offset, require_last_num, serialize)

    def add_personal_daily_events(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.PersonalDailyEvent)

    def delete_personal_daily_events(self, ids: tp.Iterable[int]):
        self._execute_delete(ids, cm.PersonalDailyEvent)

    def update_personal_daily_events(self, models: tp.Iterable[dict]):
        self._execute_update(models, cm.PersonalDailyEvent)

    def get_personal_many_days_events_by_id(self, ids: tp.Iterable[int] = None, owner_id: int = None, limit: int = None,
                                            offset: int = None, require_last_num: bool = False,
                                            serialize: bool = True) -> 'RepoSelectResponse':
        query = select(cm.PersonalManyDaysEvent)
        if ids:
            query = query.where(cm.PersonalManyDaysEvent.id.in_(ids))
        if owner_id:
            query = query.where(cm.PersonalManyDaysEvent.owner_id == owner_id)
        return self._execute_select(query, limit, offset, require_last_num, serialize)

    def add_personal_many_days_events(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.PersonalManyDaysEvent)

    def delete_personal_many_days_events(self, ids: tp.Iterable[int]):
        self._execute_delete(ids, cm.PersonalDailyEvent)

    def update_personal_many_days_events(self, models: tp.Iterable[dict]):
        self._execute_update(models, cm.PersonalManyDaysEvent)

    def get_many_days_event_permissions(self, many_days_event_id: int, role_id: int) -> tuple[str]:
        query = (select(roles.wsRoleManyDaysEvent.permissions).
                 where(roles.wsRoleManyDaysEvent.many_days_event_id == many_days_event_id).
                 where(roles.wsRoleManyDaysEvent.role_id == role_id)
                 )
        return self._get_permissions(query)

    def get_role_by_id_workspace(self, id_: int, workspace_id: int) -> 'RepoSelectResponse':
        query = select(roles.wsRole).where(roles.wsRole.id == id_).where(roles.wsRole.workspace_id == workspace_id)
        return self._execute_select(query)

    def update_workspaces(self, models: list[dict]):
        self._execute_update(models, cm.Workspace)

    def add_ws_roles(self, models: list[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, roles.wsRole)


@dataclass
class RepoSelectResponse:
    """Ответ DataRepository на запрос по получению данных."""
    content: list
    last_record_num: int = 0
    records_left: int = 0

    def __str__(self):
        return (f'RepoInsertResponse: last_records_num = {self.last_record_num}, records_left = {self.records_left}\n'
                f' content = [{[f'{record}\n' for record in self.content]}]')


@dataclass
class RepoInsertResponse:
    """Ответ DataRepository на запрос по добавлению данных."""
    ids: tp.Iterable[int] = ()


if __name__ == '__main__':
    from server.database.models.db_utils import launch_db
    engine = launch_db('sqlite:///database')
    s_maker = sessionmaker(engine)
    repo = DataRepository(s_maker)
    print(repo.get_ws_daily_events_by_id(notified_id=1, ids=[]).content)


