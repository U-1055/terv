import datetime

from sqlalchemy.orm.session import Session, sessionmaker, Select, Query
from sqlalchemy.sql import select, insert, update, delete, func
from sqlalchemy.types import DATETIME, DATE, TIME
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy.orm import Mapped

import typing as tp
from dataclasses import dataclass

import server.database.models.common_models as cm
import server.database.models.roles as roles
from common.base import DBFields, get_datetime_now, CommonStruct
from server.database.schemes.base import schemes_models
from server.data_const import DataStruct


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

    def _get_permissions(self, query: Select) -> tuple[str]:
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

    def _execute_delete(self, ids: tuple[int, ...], base_model: tp.Type[cm.Base]):
        with self._session_maker() as session, session.begin():
            session.execute(delete(base_model).where(base_model.id.in_(ids)))

    def _execute_insert(self, models: tuple[dict, ...], base_model: tp.Type[cm.Base]) -> 'RepoInsertResponse':
        with self._session_maker() as session, session.begin():
            schema: SQLAlchemyAutoSchema = schemes_models.get(base_model)
            schema.sqla_session = session
            models = [schema.load(model, session=session) for model in models]

            session.add_all(models)
            session.flush()
            return RepoInsertResponse(ids=tuple(int(db_model.id) for db_model in models))

    def _execute_update(self, models: tuple[dict, ...], base_model: tp.Type[cm.Base]):
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

    def get_users_by_username(self, usernames: tuple[str, ...] = None, require_last_rec_num: bool = False, limit: int = None, offset: int = 0,
                              serialize: bool = True) -> 'RepoSelectResponse':

        query = select(cm.User)
        if usernames:
            query = query.where(cm.User.username.in_(usernames))

        return self._execute_select(query, limit, offset, require_last_rec_num, serialize)

    def get_users_by_email(self, emails: tuple[str, ...] = None, require_last_rec_num: bool = False,
                               limit: int = None, offset: int = 0) -> 'RepoSelectResponse':
        query = select(cm.User).where(cm.User.email.in_(emails))
        return self._execute_select(query, limit, offset, require_last_rec_num)

    def get_users_by_id(self, ids: tuple[int], limit: int = None, offset: int = 0, require_last_rec_num: bool = False,
                        serialize: bool = True):
        query = select(cm.User).where(cm.User.id.in_(ids))
        return self._execute_select(query, limit, offset, require_last_rec_num, serialize)

    def get_workflows(self,
                      workflow_ids: tuple[int] = None,
                      name: str = None,
                      require_last_rec_num: bool = False,
                      limit: int = None,
                      offset: int = 0,
                      serialize: bool = True
                      ) -> 'RepoSelectResponse':
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

        return self._execute_select(query, limit, offset, require_last_rec_num, serialize)

    def get_user_hashed_password(self, login: str) -> str | None:
        """Возвращает хэш пароля пользователь с заданным логином. Если такого пользователя нет - возвращает None."""
        with self._session_maker() as session, session.begin():
            query = select(cm.User).where(cm.User.username == login)
            result = session.execute(query).scalars().all()
            if result:
                return result[0].hashed_password

    def update_wf_roles(self, models: tuple[dict, ...] | list[dict]):
        self._execute_update(models, roles.WFRole)

    def get_wf_tasks_by_id(self, wf_tasks_ids: list[int] = None, limit: int = None, offset: int = 0, require_last_num: bool = False) -> 'RepoSelectResponse':
        query = select(cm.WFTask)
        if wf_tasks_ids:
            query = query.where(cm.WFTask.id.in_(wf_tasks_ids))

        return self._execute_select(query, limit, offset, require_last_num)

    def get_role_by_user_id(self, workflow_id: int, user_id: int):
        """Получает роль пользователя в проекте."""
        query = (select(roles.WFRole).where(roles.WFRole.workflow_id == workflow_id).
                 where(roles.WFRole.users.any(cm.User.id == user_id)))
        return self._execute_select(query)

    def get_workflow_default_role_id(self, workflow_id: int) -> int:
        """Получает ID роли РП по умолчанию."""
        query = select(cm.Workflow).where(cm.Workflow.id == workflow_id)
        result = self._execute_select(query)
        role_id = result.content[0].get(DBFields.id)

        return role_id

    def get_roles_by_id(self,
                        ids: tuple[int],
                        limit: int = None,
                        offset: int = None,
                        require_last_num: bool = False) -> 'RepoSelectResponse':
        """Получает роль РП (WFRole) по её ID."""
        query = select(roles.WFRole).where(roles.WFRole.id.in_(ids))
        return self._execute_select(query, limit, offset, require_last_num)

    def update_wf_tasks(self, models: list[cm.WFTask]):
        self._execute_update(models, cm.WFTask)

    def delete_wf_tasks_by_id(self, ids: list[int]):
        self._execute_delete(ids, cm.WFTask)

    def update_personal_tasks(self, models: list[cm.WFTask]):
        self._execute_update(models, cm.WFTask)

    def delete_workflows(self, workflows_ids: tuple[int]):
        self._execute_delete(workflows_ids, cm.Workflow)

    def update_users(self, models: tuple[dict, ...]):
        self._execute_update(models, cm.User)

    def add_users(self, models: tuple[dict, ...]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.User)

    def add_wf_tasks(self, models: tuple[dict, ...]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.User)

    def delete_users(self, ids: tuple[int, ...]):
        self._execute_delete(ids, cm.User)

    def add_workflows(self, models: tuple[dict, ...]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.Workflow)

    def add_personal_tasks(self, models: tuple[dict, ...]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.PersonalTask)

    def delete_personal_tasks(self, ids: tuple[int]):
        self._execute_delete(ids, cm.PersonalTask)

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

    def get_personal_tasks_by_id(self, ids: tuple[int, ...] | list[int] = None, limit: int = None, offset: int = None,
                                 require_last_num: bool = False, serialize: bool = True):
        query = select(cm.PersonalTask)
        if ids:
            query = query.where(cm.PersonalTask.id.in_(ids))
        return self._execute_select(query, limit, offset, require_last_num, serialize)

    def get_wf_daily_events_by_id(self, ids: tuple[int, ...] | list[int] = None, limit: int = None, offset: int = None,
                                  require_last_num: bool = False, serialize: bool = True) -> 'RepoSelectResponse':
        query = select(cm.WFDailyEvent)
        if ids:
            query = query.where(cm.WFDailyEvent.id.in_(ids))
        return self._execute_select(query, limit, offset, require_last_num, serialize)

    def add_wf_daily_events(self, models: tuple[dict, ...]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.WFDailyEvent)

    def delete_wf_daily_events(self, ids: tuple[int, ...] | list[int]):
        self._execute_delete(ids, cm.WFDailyEvent)

    def update_wf_daily_events(self, models: tuple[dict, ...]):
        self._execute_update(models, cm.WFDailyEvent)

    def get_wf_many_days_events_by_id(self, ids: tuple[int, ...] | list[int] = None, limit: int = None, offset: int = None,
                                  require_last_num: bool = False, serialize: bool = True) -> 'RepoSelectResponse':
        query = select(cm.WFManyDaysEvent)
        if ids:
            query = query.where(cm.WFManyDaysEvent.id.in_(ids))
        return self._execute_select(query, limit, offset, require_last_num, serialize)

    def add_wf_many_days_events(self, models: tuple[dict, ...]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.WFManyDaysEvent)

    def delete_wf_many_days_events(self, ids: tuple[int, ...] | list[int]):
        self._execute_delete(ids, cm.WFManyDaysEvent)

    def update_wf_many_days_events(self, models: tuple[dict, ...]):
        self._execute_update(models, cm.WFManyDaysEvent)

    def get_personal_daily_events_by_id(self, ids: tuple[int, ...] | list[int] = None, limit: int = None, offset: int = None,
                                  require_last_num: bool = False, serialize: bool = True) -> 'RepoSelectResponse':
        query = select(cm.PersonalTask)
        if ids:
            query = query.where(cm.PersonalDailyEvent.id.in_(ids))
        return self._execute_select(query, limit, offset, require_last_num, serialize)

    def add_personal_daily_events(self, models: tuple[dict, ...]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.PersonalDailyEvent)

    def delete_personal_daily_events(self, ids: tuple[int, ...] | list[int]):
        self._execute_delete(ids, cm.PersonalDailyEvent)

    def update_personal_daily_events(self, models: tuple[dict, ...]):
        self._execute_update(models, cm.PersonalDailyEvent)

    def get_personal_many_days_events_by_id(self, ids: tuple[int, ...] | list[int] = None, limit: int = None, offset: int = None,
                                  require_last_num: bool = False, serialize: bool = True) -> 'RepoSelectResponse':
        query = select(cm.PersonalManyDaysEvent)
        if ids:
            query = query.where(cm.PersonalManyDaysEvent.id.in_(ids))
        return self._execute_select(query, limit, offset, require_last_num, serialize)

    def add_personal_many_days_events(self, models: tuple[dict, ...]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.PersonalManyDaysEvent)

    def delete_personal_many_days_events(self, ids: tuple[int, ...] | list[int]):
        self._execute_delete(ids, cm.PersonalDailyEvent)

    def update_personal_many_days_events(self, models: tuple[dict, ...]):
        self._execute_update(models, cm.PersonalManyDaysEvent)

    def get_many_days_event_permissions(self, many_days_event_id: int, role_id: int) -> tuple[str]:
        query = (select(roles.WFRoleManyDaysEvent.permissions).
                 where(roles.WFRoleManyDaysEvent.many_days_event_id == many_days_event_id).
                 where(roles.WFRoleManyDaysEvent.role_id == role_id)
                 )
        return self._get_permissions(query)

    def get_role_by_id_workflow(self, id_: int, workflow_id: int) -> 'RepoSelectResponse':
        query = select(roles.WFRole).where(roles.WFRole.id == id_).where(roles.WFRole.workflow_id == workflow_id)
        return self._execute_select(query)

    def update_workflows(self, models: list[dict]):
        self._execute_update(models, cm.Workflow)

    def add_wf_roles(self, models: list[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, roles.WFRole)


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
    ids: tuple[int, ...] = ()


if __name__ == '__main__':
    from server.database.models.db_utils import launch_db
    engine = launch_db('database')
    s_maker = sessionmaker(engine)
    repo = DataRepository(s_maker)
    repo.add_personal_tasks({})


