"""Объекты для настройки тестовой БД."""
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import delete, select
from faker import Faker

import datetime
import typing as tp

from server.auth.auth_module import hash_password
from server.database.models.db_utils import init_db
import server.database.models.common_models as cm
from common.base import DBFields


class DatabaseManager:

    getting_config_personal_tasks = 1
    getting_config_ws_tasks = 2
    getting_config_workspaces = 3
    getting_config_4 = 4
    searching_config = 5

    def __init__(self, path: str):
        self._database_path = path
        self._faker = Faker()
        engine = init_db(path)
        self.session_maker = sessionmaker(bind=engine)

    def _set_getting_config_personal_tasks(self):

        users_params = [[self._faker.name(), self._faker.email()] for _ in range(10)]
        statuses_params = [[self._faker.name()] for _ in range(5)]
        personal_tasks_params = [
            {
                DBFields.name: self._faker.name(),
                DBFields.description: self._faker.text(1000, ['vodka', 'chay', 'kniga']),
                DBFields.status_id: 1 if i % 2 == 0 else 2,
                DBFields.plan_deadline: datetime.datetime(2026, 2, 14, 0, 10)
                if i % 2 == 0 else datetime.datetime(2026, 3, 3, 0, 10)
            } for i in range(10)
        ]

        personal_tasks_events_params = [
            {
                DBFields.date: datetime.date(2026, 2, 14) if i % 2 == 0 else datetime.date(2026, 3, 15),
                DBFields.time_start: datetime.time(hour=12, minute=15),
                DBFields.time_end: datetime.time(hour=12, minute=30)
            } for i in range(10)
        ]

        personal_daily_events_params = [
            {
                DBFields.name: self._faker.name(),
                DBFields.date: datetime.date(2026, 2, 14) if i % 2 == 0 else datetime.date(2026, 3, 15),
                DBFields.time_start: datetime.time(hour=12, minute=15),
                DBFields.time_end: datetime.time(hour=12, minute=30)
            } for i in range(10)
        ]

        personal_many_days_events_params = [
            {
                DBFields.name: self._faker.name(),
                DBFields.datetime_start: datetime.datetime(2026, 3, 2) if i % 2 == 0 else datetime.datetime(2026, 4, 2),
                DBFields.datetime_end: datetime.datetime(2026, 3, 12) if i % 2 == 0 else datetime.datetime(2026, 4, 12)
            } for i in range(10)
        ]

        workspaces_params = [
            {
                DBFields.name: self._faker.name(),
            } for i in range(2)
        ]

        ws_tasks_params = [  # Дедлайн: 14.02.2026 ИЛИ 15.03.2026
            {
                DBFields.name: self._faker.name(),
                DBFields.status_id: 1 if i % 2 == 0 else 2,
                DBFields.plan_deadline: datetime.datetime(2026, 2, 14) if i % 2 == 0 else datetime.datetime(2026, 3, 15)
            } for i in range(10)
        ]

        ws_tasks_events_params = [
            {
                DBFields.date: datetime.date(2026, 2, 14) if i % 2 == 0 else datetime.date(2026, 3, 15),
                DBFields.time_start: datetime.time(hour=12, minute=15),
                DBFields.time_end: datetime.time(hour=12, minute=30)
            } for i in range(10)
        ]

        other_ws_tasks_params = [  # Дедлайн: 14.02.2026 ИЛИ 14.04.2026
            {
                DBFields.name: self._faker.name(),
                DBFields.status_id: 2 if i % 2 == 0 else 1,
                DBFields.plan_deadline: datetime.datetime(2026, 2, 14) if i % 2 == 0 else datetime.datetime(2026, 4, 14)
            } for i in range(10)
        ]

        ws_daily_events_params = [  # 02.04.2026 ИЛИ 02.03.2026
            {
                DBFields.name: self._faker.name(),
                DBFields.date: datetime.date(2026, 3, 2) if i % 2 == 0 else datetime.date(2026, 4, 2),
                DBFields.time_start: datetime.time(hour=12, minute=15),
                DBFields.time_end: datetime.time(hour=12, minute=30)
            } for i in range(10)
        ]

        other_ws_daily_events_params = [  # 02.03.2026 ИЛИ 03.05.2026
            {
                DBFields.name: self._faker.name(),
                DBFields.date: datetime.date(2026, 3, 2) if i % 2 == 0 else datetime.date(2026, 5, 3),
                DBFields.time_start: datetime.time(hour=12, minute=15),
                DBFields.time_end: datetime.time(hour=12, minute=30)
            } for i in range(10)
        ]

        ws_many_days_events_params = [  # 14.02.2026-14.03.2026 ИЛИ 15.03.2026-14.04.2026
            {
                DBFields.name: self._faker.name(),
                DBFields.datetime_start: datetime.datetime(2026, 2, 14) if i % 2 == 0 else datetime.datetime(2026, 3, 15),
                DBFields.datetime_end: datetime.datetime(2026, 3, 14) if i % 2 == 0 else datetime.datetime(2026, 4, 14)
            } for i in range(10)
        ]

        other_ws_many_days_events_params = [  # 14.02.26-14.03.2026 ИЛИ 14.05.2026-14.06.2026
            {
                DBFields.name: self._faker.name(),
                DBFields.datetime_start: datetime.datetime(2026, 2, 14) if i % 2 == 0 else datetime.datetime(2026, 5, 14),
                DBFields.datetime_end: datetime.datetime(2026, 3, 14) if i % 2 == 0 else datetime.datetime(2026, 6, 14)
            } for i in range(10)
        ]

        with self.session_maker() as session, session.begin():
            users = [cm.User(username=param[0], hashed_password='_', email=param[1]) for param in users_params]

            session.add_all(users)
            user = session.execute(select(cm.User).where(cm.User.id == 1)).scalars().all()[0]
            other_user = session.execute(select(cm.User).where(cm.User.id == 2)).scalars().all()[0]

            statuses = [cm.PersonalTaskStatus(name=param[0], owner=user) for param in statuses_params]
            session.add_all(statuses)
            user.completed_task_status_id = 1

            personal_tasks = [cm.PersonalTask(**param, owner=user) for param in personal_tasks_params]
            session.add_all(personal_tasks)
            personal_tasks_events = [cm.PersonalTaskEvent(**personal_tasks_events_params[i], task=task)
                                     for i, task in enumerate(personal_tasks)]
            session.add_all(personal_tasks_events)

            personal_daily_events = [
                cm.PersonalDailyEvent(**param, owner=user) for param in personal_daily_events_params
            ]
            session.add_all(personal_daily_events)

            personal_many_days_events = [cm.PersonalManyDaysEvent(**param, owner=user)
                                         for param in personal_many_days_events_params]
            session.add_all(personal_many_days_events)

            other_personal_tasks = [
                cm.PersonalTask(owner=other_user, owner_id=other_user.id, name='PT', plan_deadline=datetime.datetime(2026, 2, 14), status_id=1)
                for i in range(10)
            ]
            other_personal_daily_events = [
                cm.PersonalDailyEvent(owner=other_user, name='PDE', date=datetime.date(2026, 2, 14),
                                      time_start=datetime.time(0, 0), time_end=datetime.time(0, 0))
                for i in range(10)
            ]
            other_personal_many_days_events = [
                cm.PersonalManyDaysEvent(owner=other_user, name='PMDE',
                                         datetime_start=datetime.datetime(2026, 3, 10),
                                         datetime_end=datetime.datetime(2026, 4, 10))
                for i in range(10)
            ]
            session.add_all(other_personal_tasks)
            session.add_all(other_personal_daily_events)
            session.add_all(other_personal_many_days_events)
            # Создание объектов РП
            creator = session.execute(select(cm.User).where(cm.User.id == 3)).scalars().all()[0]
            workspaces = [cm.Workspace(**params, creator=creator if i % 2 == 0 else other_user,
                                       users=[creator, user, other_user]) for i, params in enumerate(workspaces_params)]
            session.add_all(workspaces)
            ws_task_status_1 = cm.WSTaskStatus(name='WSStatus', workspace=workspaces[0])
            ws_task_status_2 = cm.WSTaskStatus(name='WSStatus', workspace=workspaces[1])
            workspaces[0].completed_task_status_id = 1
            workspaces[1].completed_task_status_id = 2
            session.add_all([ws_task_status_2, ws_task_status_1])

            ws_tasks = [cm.WSTask(**params, workspace=workspaces[0], creator=creator, executors=[user], entrusted=creator)
                        for params in ws_tasks_params]
            session.add_all(ws_tasks)

            ws_tasks_events = [cm.WSTaskEvent(**ws_tasks_events_params[i], task=task) for i, task in enumerate(ws_tasks)]
            session.add_all(ws_tasks_events)

            other_ws_tasks = [cm.WSTask(**params, workspace=workspaces[1], creator=other_user, entrusted=other_user,
                              executors=[other_user, user]) for params in other_ws_tasks_params]
            session.add_all(other_ws_tasks)

            ws_daily_events = [cm.WSDailyEvent(**params, creator=creator, notified=[other_user, user, creator],
                                               workspace=workspaces[0])
                               for params in ws_daily_events_params]
            session.add_all(ws_daily_events)
            other_ws_daily_events = [cm.WSDailyEvent(**params, creator=other_user, notified=[other_user, user],
                                     workspace=workspaces[1]) for params in other_ws_daily_events_params]
            session.add_all(other_ws_daily_events)

            ws_many_days_events = [cm.WSManyDaysEvent(**params, creator=creator, notified=[other_user, user, creator],
                                                      workspace=workspaces[0]) for params in ws_many_days_events_params]
            session.add_all(ws_many_days_events)

            other_ws_many_days_events = [cm.WSManyDaysEvent(**params, creator=other_user,
                                                            notified=[other_user, creator], workspace=workspaces[1])
                                         for params in other_ws_many_days_events_params]
            session.add_all(other_ws_many_days_events)

    def set_authentication_test_config(self):
        with self.session_maker() as session, session.begin():
            session.execute(delete(cm.User))

    def set_limit_offset_test_config(self, login: str, password: str, email: str, tasks_num: int):
        """Устанавливает конфиг для теста обработки limit&offset"""
        with self.session_maker() as session, session.begin():
            creator = cm.User(username='lo', hashed_password='ps', email='email1')
            session.add(creator)

            workspace = cm.Workspace(name='ws1', creator=creator, description='')
            session.add(workspace)

            status = cm.WSTaskStatus(name=f'status', workspace=workspace)
            session.add(status)

            user = cm.User(username=login, hashed_password=hash_password(password), email=email)
            session.add(user)

        with self.session_maker() as session, session.begin():
            workspace = session.execute(select(cm.Workspace).where(cm.Workspace.name == 'ws1')).scalars().one()
            user = session.execute(select(cm.User).where(cm.User.username == login)).scalars().one()
            creator = session.execute(select(cm.User).where(cm.User.username == 'lo')).scalars().one()

            tasks = []
            for i in range(tasks_num):
                task = cm.WSTask(name=f'ws_task_{i}',
                                 plan_deadline=datetime.datetime.now(),
                                 creator=creator,
                                 entrusted=creator,
                                 executors=[user],
                                 workspace=workspace,
                                 description='',
                                 status=status
                                 )
                tasks.append(task)

            session.add_all(tasks)

    def set_repository_test_config(self, login: str, workspace_name: str, tasks_num: int):
        """
        Создаёт конфиг БД для теста репозитория: двух пользователей (User) (один с username=login),
        одно РП (Workspace(name=workspace_name)), tasks_num задач РП (WSTask).
        """
        with self.session_maker() as session, session.begin():
            creator = cm.User(username='lo', hashed_password='2', email='N')
            session.add(creator)
            workspace = cm.Workspace(name=workspace_name, creator=creator, description='Test ws')
            session.add(workspace)
            creator.linked_workspaces = [workspace]

            user = cm.User(username=login, hashed_password='2', email='M', linked_workspaces=[workspace])
            session.add(user)
            ws_task_status = cm.WSTaskStatus(workspace=workspace, name='NAME', description='DESCRIPTION')
            personal_task_status = cm.PersonalTaskStatus(owner=user, name='NAME', description='DESCRIPTION')
            session.add(ws_task_status)
            session.add(personal_task_status)

            for i in range(tasks_num):
                ws_task = cm.WSTask(name=f'Task_{i}',
                                    plan_deadline=datetime.datetime.now(),
                                    creator=creator,
                                    entrusted=creator,
                                    executors=[user],
                                    workspace=workspace,
                                    description='',
                                    status=ws_task_status
                                    )
                session.add(ws_task)

    def set_workspace_service_test_config(self, users_num: int):
        """
        Устанавливает конфиг для теста сервиса Workspace. (1 пользователь - создатель Workspace, 1 Workspace,
        users_num пользователей).
        """
        with self.session_maker() as session, session.begin():
            creator = cm.User(username='creator', hashed_password='s', email='ss')
            session.add(creator)
            workspace = cm.Workspace(name='ws_1', creator=creator)
            session.add(workspace)
            role = cm.WSRole(name='Role1', workspace=workspace)
            session.add(role)

            workspace.default_role_id = 1
            creator.linked_workspaces = [workspace]
            assert workspace.default_role_id, workspace.default_role_id
            for i in range(users_num):
                user = cm.User(username=f'user_{i}', hashed_password='s', email=f'em{i}')
                session.add(user)
            session.commit()

    def set_name_searching_test_config(self):
        """
        Устанавливает конфиг для тестирования поиска по имени и email.
        Формат имени пользователей: User#<[0-99]><[0-1]>
        Email: email<[0-99]><[0-1]>@sth.com
        Всего создаётся 100 пользователей, из них 50 имеют 0 в качестве последней цифры email и имени, 50 - 1.

        """
        users_params = [
            {
                DBFields.username: f'User#{i}{i % 2}', DBFields.email: f'email{i}{i % 2}@sth.com',
                DBFields.hashed_password: self._faker.text(100, ['Der', 'Lowe', 'aus', 'Mitternacht', 'coms'])
            } for i in range(100)
        ]
        with self.session_maker() as session, session.begin():
            users = [cm.User(**params) for params in users_params]
            session.add_all(users)

    def add_new_user(self):
        """Добавляет пользователя со случайными email и username."""
        with self.session_maker() as session, session.begin():
            user = cm.User(username='____', hashed_password=str(datetime.datetime.now()),
                           email='EMAIL')
            session.add(user)

    def choose_db_config(self, num: int):
        """Устанавливает конфиг БД по номеру."""
        if num == self.getting_config_personal_tasks:
            self._set_getting_config_personal_tasks()
        if num == self.searching_config:
            self.set_name_searching_test_config()

    def show_db_config(self):
        """Выводит в консоль объекты из базы."""
        entities = []

        with self.session_maker() as session, session.begin():
            for model in cm.Base.__subclasses__():
                entities.extend(session.execute(select(model)).scalars().all())

            print([entity.id for entity in entities])
            groups: dict[tp.Type[cm.Base], list] = {}
            for entity in entities:
                type_ = type(entity)
                if type_ not in groups:
                    groups[type_] = [entity]
                else:
                    groups[type_].append(entity)

            print('----------------- TEST DATABASE STATE -----------------')
            for group in groups:
                print(f'\nmodel_class ---- {group} ---- \n')
                for model in groups[group]:
                    if model:
                        print(model.__dict__)


if __name__ == '__main__':

    db_manager = DatabaseManager('sqlite:///database')
    db_manager._set_getting_config_personal_tasks()
    db_manager.show_db_config()
