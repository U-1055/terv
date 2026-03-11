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
        current_date = datetime.date.today()

        users_params = [[self._faker.name(), self._faker.email()] for _ in range(10)]
        statuses_params = [[self._faker.name()] for _ in range(5)]
        personal_tasks_params = [
            {
                DBFields.name: self._faker.name(),
                DBFields.description: self._faker.text(1000, ['vodka', 'chay', 'kniga']),
                DBFields.status_id: 1 if i % 2 == 0 else 2,
                DBFields.plan_deadline: self._faker.date_time()
            } for i in range(10)
        ]
        personal_tasks_events_params = [
            {
                DBFields.task_id: i,
                DBFields.date: datetime.date.today(),
                DBFields.time_start: datetime.time(hour=i * 2, minute=15 * (i % 2)),
                DBFields.time_end: datetime.time(hour=i * 2 + 2, minute=15 * (i % 2))
            } for i in range(10)]

        with self.session_maker() as session, session.begin():
            users = [cm.User(username=param[0], hashed_password='_', email=param[1]) for param in users_params]

            session.add_all(users)
            user = session.execute(select(cm.User).where(cm.User.id == 1)).scalars().all()[0]

            statuses = [cm.PersonalTaskStatus(name=param[0], owner=user) for param in statuses_params]
            session.add_all(statuses)
            user.completed_task_status_id = 1

            personal_tasks = [cm.PersonalTask(**param, owner=user) for param in personal_tasks_params]
            session.add_all(personal_tasks)

            personal_tasks_events = [cm.PersonalTaskEvent(**param) for param in personal_tasks_events_params]
            session.add_all(personal_tasks_events)

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
            user = cm.User(username=self._faker.name(), hashed_password=str(datetime.datetime.now()),
                           email=self._faker.email())
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
    db_manager.set_name_searching_test_config()
    db_manager.show_db_config()
