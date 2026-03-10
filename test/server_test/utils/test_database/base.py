"""Объекты для настройки тестовой БД."""
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import delete, select
from faker import Faker

import datetime

from server.auth.auth_module import hash_password
from server.database.models.db_utils import init_db
import server.database.models.common_models as cm


class DatabaseManager:

    getting_config_personal_tasks = 1
    getting_config_ws_tasks = 2
    getting_config_workspaces = 3
    getting_config_4 = 4

    def __init__(self, path: str):
        self._database_path = path
        self._faker = Faker()
        engine = init_db(path)
        self.session_maker = sessionmaker(bind=engine)

    def _set_getting_config_personal_tasks(self):
        with self.session_maker() as session, session.begin():
            pass


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

    def add_new_user(self):
        """Добавляет пользователя со случайными email и username."""
        with self.session_maker() as session, session.begin():
            user = cm.User(username=self._faker.name(), hashed_password=str(datetime.datetime.now()),
                           email=self._faker.email())
            session.add(user)

    def choose_db_config(self, num: int):
        pass


if __name__ == '__main__':

    db_manager = DatabaseManager('sqlite:///database')
    db_manager.set_workspace_service_test_config(15)
