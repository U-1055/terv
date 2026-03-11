import datetime
import logging

from sqlalchemy.orm.session import sessionmaker, Select, Session
from sqlalchemy.sql import select, delete, text
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

import typing as tp
from dataclasses import dataclass

import server.database.models.common_models as cm
from common.base import DBFields, get_datetime_now
from server.database.schemes.base import schemes_models
from common.logger import config_logger, SERVER
from server.api.base import LOG_DIR, MAX_FILE_SIZE, MAX_BACKUP_FILES, LOGGING_LEVEL
from server.database.exceptions import exc_mapped, BaseRepoException

logger = config_logger(__name__, SERVER, LOG_DIR, MAX_BACKUP_FILES, MAX_FILE_SIZE, LOGGING_LEVEL)


class DataRepository:

    """
    Репозиторий базы данных. В ответах на запросы получения данных возвращает объект RepoSelectResponse.
    RepoSelectResponse.content - список сериализованных моделей, полученных в ответе.
    RepoSelectResponse.last_record_num - номер последней модели (если в запрос передан limit, offset или require_last_rec_num,
    иначе - None)

    :param session_maker: Фабрика сессий sessionmaker, используемая для создания сессий в репозитории.
    :param launch_validation: Запускать ли проверку целостности БД при инициализации? По умолчанию: да.
    :param enable_fk_check: Включать ли проверку FK при создании сессий? (Только для SQLite). По умолчанию: да.

    """

    def __init__(self, session_maker: sessionmaker, launch_validation: bool = True, enable_fk_check: bool = True):
        self._session_maker = session_maker
        self._enable_fk_check = enable_fk_check
        if launch_validation:
            self._validate()

    def _validate(self):
        pass

    def _prepare_session(self, session: Session):
        """
        Выполняет действия с сессией перед обработкой запросов. Включает проверку FK при соответствующем параметре.
        """
        if self._enable_fk_check:
            session.execute(text('PRAGMA foreign_keys=ON'))

    def _get_permissions(self, query: Select) -> tuple[str, ...]:
        with self._session_maker() as session, session.begin():
            perm_ids = session.execute(query)
            permissions = session.execute(
                select(cm.Permission.type).where(cm.Permission.id.in_(perm_ids))).scalars().all()

        return permissions

    def _execute_select(self, query: Select, limit: int = None, offset: int = None, require_last_rec_num: bool = False,
                        serialize: bool = True) -> 'RepoSelectResponse':
        with self._session_maker() as session, session.begin():
            self._prepare_session(session)
            result = session.execute(query.limit(limit).offset(offset)).scalars().all()
            if serialize:
                models_list = [model for model in result]
                if models_list:  # Сериализуем
                    scheme = schemes_models.get(type(models_list[0]))  # Получаем схему
                    if not scheme:
                        logger.critical(f'There is no scheme for model: {type(models_list[0])}.')
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
            self._prepare_session(session)
            session.execute(delete(base_model).where(base_model.id.in_(ids)))

    def _execute_insert(self, models: tp.Iterable[dict], base_model: tp.Type[cm.Base]) -> 'RepoInsertResponse':
        with self._session_maker() as session, session.begin():
            self._prepare_session(session)
            schema: SQLAlchemyAutoSchema = schemes_models.get(base_model)
            schema.sqla_session = session
            models = [schema.load(model, session=session) for model in models]

            session.add_all(models)
            session.flush()
            return RepoInsertResponse(ids=list(int(db_model.id) for db_model in models))

    def _execute_update(self, models: tp.Iterable[dict], base_model: tp.Type[cm.Base]):
        """
        Частично обновляет указанные модели введёнными данными. Автоматически десериализует модели, ID которых передан в
        relationship-полях. В переданных моделях обязательно должно быть поле id (ID обновляемого объекта), кроме него
        могут быть любые другие поля, значения которых будут обновлены.
        """
        with self._session_maker() as session, session.begin():
            self._prepare_session(session)
            schema: SQLAlchemyAutoSchema = schemes_models.get(base_model)
            ids = []
            for model in models:
                id_ = model.get(DBFields.id)
                if not id_:
                    raise BaseRepoException.get_no_required_param_error(DBFields.id)
                ids.append(id_)

            db_models = session.execute(select(base_model).where(base_model.id.in_(ids))).scalars().all()
            db_models = {db_model.id: db_model for db_model in db_models}

            result = [(user.username, user.email) for user in session.execute(select(cm.User)).scalars().all()]

            for model in models:  # Сериализация + обновление даты в updated_at
                model[DBFields.updated_at] = get_datetime_now()
                db_model = db_models.get(model.get(DBFields.id))
                schema.load(model, session=session, partial=True, instance=db_model)
                pass

    @exc_mapped
    def get_users_by_username(self, usernames: tp.Iterable[str] = None, require_last_rec_num: bool = False, limit: int = None, offset: int = 0,
                              serialize: bool = True) -> 'RepoSelectResponse':

        query = select(cm.User)
        if usernames:
            query = query.where(cm.User.username.in_(usernames))

        return self._execute_select(query, limit, offset, require_last_rec_num, serialize)

    @exc_mapped
    def get_users_by_email(self, emails: tp.Iterable[str] = None, require_last_rec_num: bool = False,
                               limit: int = None, offset: int = 0) -> 'RepoSelectResponse':
        query = select(cm.User).where(cm.User.email.in_(emails))
        return self._execute_select(query, limit, offset, require_last_rec_num)

    @exc_mapped
    def get_users_by_id(self, ids: tp.Iterable[int], limit: int = None, offset: int = 0, require_last_rec_num: bool = False,
                        serialize: bool = True):
        query = select(cm.User).where(cm.User.id.in_(ids))
        return self._execute_select(query, limit, offset, require_last_rec_num, serialize)

    @exc_mapped
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

    @exc_mapped
    def get_user_hashed_password(self, login: str) -> str | None:
        """Возвращает хэш пароля пользователь с заданным логином. Если такого пользователя нет - возвращает None."""
        with self._session_maker() as session, session.begin():
            query = select(cm.User).where(cm.User.username == login)
            result = session.execute(query).scalars().all()
            if result:
                return result[0].hashed_password

    @exc_mapped
    def update_ws_roles(self, models: tp.Iterable[dict]):
        self._execute_update(models, cm.WSRole)

    @exc_mapped
    def get_ws_daily_event_by_notified_id(self, notified_id: int, limit: int = None, offset: int = 0,
                                          require_last_num: bool = False) -> 'RepoSelectResponse':
        query = select(cm.WSDailyEvent).where(cm.WSDailyEvent.notified.contains(notified_id))
        return self._execute_select(query, limit, offset, require_last_num)

    @exc_mapped
    def get_ws_tasks(self, ids: tp.Sequence[int], workspace_id: int = None, executor_id: int = None,
                     working_date: datetime.date = None, plan_deadline: datetime.datetime = None, status_ids: tp.Sequence[int] = None,
                     not_completed: bool = False, limit: int = None, offset: int = None,
                     require_last_num: bool = False, serialize: bool = True) -> 'RepoSelectResponse':
        query = select(cm.WSTask)
        if ids:
            query = query.where(cm.WSTask.id.in_(ids))
        if executor_id:
            query = query.where(cm.WSTask.executors.any(cm.User.id == executor_id))
        if workspace_id:
            query = query.where(cm.WSTask.workspace_id == workspace_id)
        if working_date:
            query = query.where(cm.WSTask.task_events.any(cm.WSTaskEvent.date == working_date))
        if status_ids:
            query = query.where(cm.WSTask.status_id.in_(status_ids))
        if not_completed:
            query = query.where(cm.WSTask.workspace.has(cm.WSTask.status_id != cm.Workspace.completed_task_status_id))
        if plan_deadline:
            query = query.where(cm.WSTask.plan_deadline == plan_deadline)

        return self._execute_select(query, limit, offset, require_last_num, serialize)

    @exc_mapped
    def get_role_by_user_id(self, workspace_id: int, user_id: int):
        """Получает роль пользователя в проекте."""
        query = (select(cm.WSRole).where(cm.WSRole.workspace_id == workspace_id).
                 where(cm.WSRole.users.any(cm.User.id == user_id)))
        return self._execute_select(query)

    @exc_mapped
    def get_workspace_default_role_id(self, workspace_id: int) -> int:
        """Получает ID роли РП по умолчанию."""
        query = select(cm.Workspace).where(cm.Workspace.id == workspace_id)
        result = self._execute_select(query)
        role_id = result.content[0].get(DBFields.id)

        return role_id

    @exc_mapped
    def get_roles_by_id(self,
                        ids: tp.Iterable[int],
                        limit: int = None,
                        offset: int = None,
                        require_last_num: bool = False) -> 'RepoSelectResponse':
        """Получает роль РП (WSRole) по её ID."""
        query = select(cm.WSRole).where(cm.WSRole.id.in_(ids))
        return self._execute_select(query, limit, offset, require_last_num)

    @exc_mapped
    def update_ws_tasks(self, models: list[cm.WSTask]):
        self._execute_update(models, cm.WSTask)

    @exc_mapped
    def delete_ws_tasks_by_id(self, ids: list[int]):
        self._execute_delete(ids, cm.WSTask)

    @exc_mapped
    def update_personal_tasks(self, models: list[cm.PersonalTask]):
        self._execute_update(models, cm.PersonalTask)

    @exc_mapped
    def delete_workspaces(self, workspaces_ids: tp.Iterable[int]):
        self._execute_delete(workspaces_ids, cm.Workspace)

    @exc_mapped
    def update_users(self, models: tp.Iterable[dict]):
        self._execute_update(models, cm.User)

    @exc_mapped
    def add_users(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.User)

    @exc_mapped
    def add_ws_tasks(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.User)

    @exc_mapped
    def delete_users(self, ids: tp.Iterable[int]):
        self._execute_delete(ids, cm.User)

    @exc_mapped
    def add_workspaces(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.Workspace)

    @exc_mapped
    def add_personal_tasks(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.PersonalTask)

    @exc_mapped
    def delete_personal_tasks(self, ids: tp.Iterable[int]):
        self._execute_delete(ids, cm.PersonalTask)

    @exc_mapped
    def get_task_permissions(self, task_id: int, role_id: int) -> tuple[str]:
        query = (select(cm.WSRoleTask.permissions).
                 where(cm.WSRoleTask.task_id == task_id).
                 where(cm.WSRoleTask.role_id == role_id)
                 )
        return self._get_permissions(query)

    @exc_mapped
    def get_project_permissions(self, project_id: int, role_id: int) -> tuple[str]:
        query = (select(cm.WSRoleProject.permissions).
                 where(cm.WSRoleProject.project_id == project_id).
                 where(cm.WSRoleProject.role_id == role_id)
                 )
        return self._get_permissions(query)

    @exc_mapped
    def get_document_permissions(self, document_id: int, role_id: int) -> tuple[str]:
        query = (select(cm.WSRoleDocument.permissions).
                 where(cm.WSRoleDocument.document_id == document_id).
                 where(cm.WSRoleDocument.role_id == role_id)
                 )
        return self._get_permissions(query)

    @exc_mapped
    def get_daily_event_permissions(self, daily_event_id: int, role_id: int) -> tuple[str]:
        query = (select(cm.WSRoleDailyEvent.permissions).
                 where(cm.WSRoleDailyEvent.daily_event_id == daily_event_id).
                 where(cm.WSRoleDailyEvent.role_id == role_id)
                 )
        return self._get_permissions(query)

    @exc_mapped
    def get_personal_tasks_by_id(self, ids: tp.Iterable[int] = None, working_date: datetime.date = None,
                                 plan_deadline: datetime.datetime = None, status_ids: tp.Sequence[int] = None,
                                 not_completed: bool = False, limit: int = None,
                                 offset: int = None, require_last_num: bool = False, serialize: bool = True):
        query = select(cm.PersonalTask)
        if ids:
            query = query.where(cm.PersonalTask.id.in_(ids))
        if working_date:
            query = query.where(cm.PersonalTask.task_events.any(cm.PersonalTaskEvent.date == working_date))
        if status_ids:
            query = query.where(cm.PersonalTask.status_id.in_(status_ids))
        if not_completed:
            query = query.where(cm.PersonalTask.owner.has(cm.User.completed_task_status_id != cm.PersonalTask.status_id))
        if plan_deadline:
            query = query.where(cm.PersonalTask.plan_deadline == plan_deadline)

        return self._execute_select(query, limit, offset, require_last_num, serialize)

    @exc_mapped
    def get_ws_daily_events_by_id(self, ids: tp.Iterable[int] | list[int] = None, notified_id: int = None,
                                  limit: int = None, offset: int = None, require_last_num: bool = False,
                                  serialize: bool = True) -> 'RepoSelectResponse':
        query = select(cm.WSDailyEvent)
        if ids:
            query = query.where(cm.WSDailyEvent.id.in_(ids))
        if notified_id:
            query = query.where(cm.WSDailyEvent.notified.any(cm.User.id == notified_id))

        return self._execute_select(query, limit, offset, require_last_num, serialize)

    @exc_mapped
    def add_ws_daily_events(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.WSDailyEvent)

    @exc_mapped
    def delete_ws_daily_events(self, ids: tp.Iterable[int]):
        self._execute_delete(ids, cm.WSDailyEvent)

    @exc_mapped
    def update_ws_daily_events(self, models: tp.Iterable[dict]):
        self._execute_update(models, cm.WSDailyEvent)

    @exc_mapped
    def get_ws_many_days_events_by_id(self, ids: tp.Iterable[int] = None, notified_id: int = None, limit: int = None,
                                      offset: int = None, require_last_num: bool = False,
                                      serialize: bool = True) -> 'RepoSelectResponse':
        query = select(cm.WSManyDaysEvent)
        if ids:
            query = query.where(cm.WSManyDaysEvent.id.in_(ids))
        if notified_id:
            query = query.where(cm.WSManyDaysEvent.notified.any(cm.User.id == notified_id))

        return self._execute_select(query, limit, offset, require_last_num, serialize)

    @exc_mapped
    def add_ws_many_days_events(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.WSManyDaysEvent)

    @exc_mapped
    def delete_ws_many_days_events(self, ids: tp.Iterable[int]):
        self._execute_delete(ids, cm.WSManyDaysEvent)

    @exc_mapped
    def update_ws_many_days_events(self, models: tp.Iterable[dict]):
        self._execute_update(models, cm.WSManyDaysEvent)

    @exc_mapped
    def get_personal_daily_events_by_id(self, ids: tp.Iterable[int], owner_id: int = None, limit: int = None,
                                        offset: int = None, require_last_num: bool = False,
                                        serialize: bool = True) -> 'RepoSelectResponse':
        query = select(cm.PersonalDailyEvent)
        if ids:
            query = query.where(cm.PersonalDailyEvent.id.in_(ids))
        if owner_id:
            query = query.where(cm.PersonalDailyEvent.owner_id == owner_id)

        return self._execute_select(query, limit, offset, require_last_num, serialize)

    @exc_mapped
    def add_personal_daily_events(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.PersonalDailyEvent)

    @exc_mapped
    def delete_personal_daily_events(self, ids: tp.Iterable[int]):
        self._execute_delete(ids, cm.PersonalDailyEvent)

    @exc_mapped
    def update_personal_daily_events(self, models: tp.Iterable[dict]):
        self._execute_update(models, cm.PersonalDailyEvent)

    @exc_mapped
    def get_personal_many_days_events_by_id(self, ids: tp.Iterable[int] = None, owner_id: int = None, limit: int = None,
                                            offset: int = None, require_last_num: bool = False,
                                            serialize: bool = True) -> 'RepoSelectResponse':
        query = select(cm.PersonalManyDaysEvent)
        if ids:
            query = query.where(cm.PersonalManyDaysEvent.id.in_(ids))
        if owner_id:
            query = query.where(cm.PersonalManyDaysEvent.owner_id == owner_id)
        return self._execute_select(query, limit, offset, require_last_num, serialize)

    @exc_mapped
    def add_personal_many_days_events(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.PersonalManyDaysEvent)

    @exc_mapped
    def delete_personal_many_days_events(self, ids: tp.Iterable[int]):
        self._execute_delete(ids, cm.PersonalDailyEvent)

    @exc_mapped
    def update_personal_many_days_events(self, models: tp.Iterable[dict]):
        self._execute_update(models, cm.PersonalManyDaysEvent)

    @exc_mapped
    def get_many_days_event_permissions(self, many_days_event_id: int, role_id: int) -> tuple[str]:
        query = (select(cm.WSRoleManyDaysEvent.permissions).
                 where(cm.WSRoleManyDaysEvent.many_days_event_id == many_days_event_id).
                 where(cm.WSRoleManyDaysEvent.role_id == role_id)
                 )
        return self._get_permissions(query)

    @exc_mapped
    def get_role_by_id_workspace(self, id_: int, workspace_id: int) -> 'RepoSelectResponse':
        query = select(cm.WSRole).where(cm.WSRole.id == id_).where(cm.WSRole.workspace_id == workspace_id)
        return self._execute_select(query)

    @exc_mapped
    def update_workspaces(self, models: tp.Iterable[dict]):
        self._execute_update(models, cm.Workspace)

    @exc_mapped
    def add_ws_roles(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.WSRole)

    @exc_mapped
    def add_ws_task_statuses(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.WSTaskStatus)

    @exc_mapped
    def update_ws_task_statuses(self, models: tp.Iterable[dict]):
        self._execute_update(models, cm.WSTaskStatus)

    @exc_mapped
    def delete_ws_task_statuses(self, ids: tp.Iterable[int]):
        self._execute_delete(ids, cm.WSTaskStatus)

    @exc_mapped
    def get_ws_task_statuses_by_id(self, ids: tp.Iterable[int], limit: int = None, offset: int = None,
                                   require_last_num: bool = False, serialize: bool = True) -> 'RepoSelectResponse':
        query = select(cm.WSTaskStatus).where(cm.WSTaskStatus.id.in_(ids))
        return self._execute_select(query, limit, offset, require_last_num, serialize)

    @exc_mapped
    def add_ws_task_tags(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.WSTaskTag)

    @exc_mapped
    def update_ws_task_tags(self, models: tp.Iterable[dict]):
        self._execute_update(models, cm.WSTaskTag)

    @exc_mapped
    def delete_ws_task_tags(self, ids: tp.Iterable[int]):
        self._execute_delete(ids, cm.WSTaskTag)

    @exc_mapped
    def get_ws_task_tags_by_id(self, ids: tp.Iterable[int], limit: int = None, offset: int = None,
                               require_last_num: bool = False, serialize: bool = True) -> 'RepoSelectResponse':
        query = select(cm.WSTaskTag).where(cm.WSTaskTag.id.in_(ids))
        return self._execute_select(query, limit, offset, require_last_num, serialize)

    @exc_mapped
    def add_personal_task_statuses(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.PersonalTaskStatus)

    @exc_mapped
    def update_personal_task_statuses(self, models: tp.Iterable[dict]):
        self._execute_update(models, cm.PersonalTaskStatus)

    @exc_mapped
    def delete_personal_task_statuses(self, ids: tp.Iterable[int]):
        self._execute_delete(ids, cm.PersonalTaskStatus)

    @exc_mapped
    def get_personal_task_statuses_by_id(self, ids: tp.Iterable[int], limit: int = None, offset: int = None,
                                   require_last_num: bool = False, serialize: bool = True) -> 'RepoSelectResponse':
        query = select(cm.PersonalTaskStatus).where(cm.PersonalTaskStatus.id.in_(ids))
        return self._execute_select(query, limit, offset, require_last_num, serialize)

    @exc_mapped
    def add_personal_task_tags(self, models: tp.Iterable[dict]) -> 'RepoInsertResponse':
        return self._execute_insert(models, cm.PersonalTaskTag)

    @exc_mapped
    def update_personal_task_tags(self, models: tp.Iterable[dict]):
        self._execute_update(models, cm.PersonalTaskTag)

    @exc_mapped
    def delete_personal_task_tags(self, ids: tp.Iterable[int]):
        self._execute_delete(ids, cm.PersonalTaskTag)

    @exc_mapped
    def get_personal_task_tags_by_id(self, ids: tp.Iterable[int], limit: int = None, offset: int = None,
                                     require_last_num: bool = False, serialize: bool = True) -> 'RepoSelectResponse':
        query = select(cm.PersonalTaskTag).where(cm.PersonalTaskTag.id.in_(ids))
        return self._execute_select(query, limit, offset, require_last_num, serialize)

    @exc_mapped
    def get_personal_task_tags_by_user(self, user_id: int, limit: int = None, offset: int = None,
                                       require_last_num: bool = False, serialize: bool = True):
        query = select(cm.PersonalTaskTag).where(cm.PersonalTaskTag.owner_id == user_id)
        return self._execute_select(query, limit, offset, require_last_num, serialize)

    @exc_mapped
    def get_personal_task_statuses_by_user(self, user_id: int, limit: int = None, offset: int = None,
                                           require_last_num: bool = False, serialize: bool = True):
        query = select(cm.PersonalTaskStatus).where(cm.PersonalTaskStatus.owner_id == user_id)
        return self._execute_select(query, limit, offset, require_last_num, serialize)

    @exc_mapped
    def get_ws_task_tags_by_workspace(self, workspace_id: int, limit: int = None, offset: int = None,
                                      require_last_num: bool = False, serialize: bool = True):
        query = select(cm.WSTaskTag).where(cm.WSTaskTag.workspace == workspace_id)
        return self._execute_select(query, limit, offset, require_last_num, serialize)

    @exc_mapped
    def get_ws_task_statuses_by_workspace(self, workspace_id: int, limit: int = None, offset: int = None,
                                          require_last_num: bool = False, serialize: bool = True):
        query = select(cm.WSTaskStatus).where(cm.WSTaskStatus.workspace_id == workspace_id)
        return self._execute_select(query, limit, offset, require_last_num, serialize)

    @exc_mapped
    def get_ws_task_events(self, ids: tp.Sequence[int], workspace_id: int, executor_id: int = None,
                           date: datetime.date = None, limit: int = None, offset: int = None, require_last_num: bool = False,
                           serialize: bool = True) -> 'RepoSelectResponse':
        query = select(cm.WSTaskEvent)
        if ids:
            query = query.where(cm.WSTaskEvent.id.in_(ids))
        if workspace_id:
            query = query.where(cm.WSTaskEvent.task.workspace_id == workspace_id)
        if executor_id:
            query = query.where(cm.WSTaskEvent.task.executor_id == executor_id)
        if date:
            query = query.where(cm.WSTaskEvent.date == date)
        return self._execute_select(query, limit, offset, require_last_num, serialize)

    @exc_mapped
    def get_personal_task_events_by_user(self, ids: tp.Sequence[int], user_id: int, date: datetime.date = None,
                                         limit: int = None, offset: int = None, require_last_num: bool = False,
                                         serialize: bool = True) -> 'RepoSelectResponse':
        query = select(cm.PersonalTaskEvent)
        if ids:
            query = query.where(cm.PersonalTaskEvent.id.in_(ids))
        if user_id:
            query = query.where(cm.PersonalTaskEvent.task.owner_id == user_id)
        if date:
            query = query.where(cm.PersonalTaskEvent.date == date)

        return self._execute_select(query, limit, offset, require_last_num, serialize)

    @exc_mapped
    def search_users(self, username: str, email: str, limit: int = None, offset: int = None, require_last_num: bool = False,
                     serialize: bool = True) -> 'RepoSelectResponse':
        query = select(cm.User)

        if username:
            query = query.where(cm.User.username.contains(username))
        if email:
            query = query.where(cm.User.email.contains(email))
        return self._execute_select(query, limit, offset, require_last_num, serialize)


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
    ids: list[int] = ()


if __name__ == '__main__':
    from server.database.models.db_utils import launch_db
    from sqlalchemy.exc import SQLAlchemyError, IntegrityError
    from marshmallow.exceptions import MarshmallowError, ValidationError

    engine = launch_db('sqlite:///database')
    s_maker = sessionmaker(engine)
    repo = DataRepository(s_maker)
    try:
        repo.add_personal_tasks([{DBFields.name: 'Name', DBFields.description: 'Desc', DBFields.status_id: 1, DBFields.owner_id: 1,
                                  DBFields.plan_deadline: datetime.datetime.now()}])
        repo.update_personal_tasks({DBFields.status_id: 2})
        # print(repo.get_personal_task_statuses_by_id([]).content)
    except IntegrityError as e:
        print(e.orig)

    except MarshmallowError as e:
        print(e.args[0])
