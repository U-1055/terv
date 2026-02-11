"""Объекты для настройки тестовой БД."""
import datetime

from sqlalchemy.orm.session import Session, sessionmaker
from sqlalchemy.sql.expression import delete, select

from server.auth.auth_module import hash_password
from server.database.models.db_utils import init_db
import server.database.models.common_models as cm
import server.database.models.roles as roles


class DatabaseManager:

    def __init__(self, path: str):
        self._database_path = path
        engine = init_db(path)
        self.session_maker = sessionmaker(bind=engine)

    def set_authentication_test_config(self):
        with self.session_maker() as session, session.begin():
            session.execute(delete(cm.User))

    def set_limit_offset_test_config(self, login: str, password: str, email: str, tasks_num: int):
        """Устанавливает конфиг для теста обработки limit&offset"""
        with self.session_maker() as session, session.begin():
            creator = cm.User(username='lo', hashed_password='ps', email='email1')
            session.add(creator)

            workspace = cm.Workspace(name='wf1', creator=creator, description='')
            session.add(workspace)

            user = cm.User(username=login, hashed_password=hash_password(password), email=email)
            session.add(user)

        with self.session_maker() as session, session.begin():
            workspace = session.execute(select(cm.Workspace).where(cm.Workspace.name == 'wf1')).scalars().one()
            user = session.execute(select(cm.User).where(cm.User.username == login)).scalars().one()
            creator = session.execute(select(cm.User).where(cm.User.username == 'lo')).scalars().one()

            tasks = []
            for i in range(tasks_num):
                task = cm.WFTask(name=f'wf_task_{i}',
                              plan_deadline=datetime.datetime.now(),
                              creator=creator,
                              entrusted=creator,
                              executors=[user],
                              workspace=workspace,
                              description=''
                              )
                tasks.append(task)

            session.add_all(tasks)

    def set_repository_test_config(self, login: str, workspace_name: str, tasks_num: int):
        """
        Создаёт конфиг БД для теста репозитория: двух пользователей (User) (один с username=login),
        одно РП (Workspace(name=workspace_name)), tasks_num задач РП (WFTask).
        """
        with self.session_maker() as session, session.begin():
            creator = cm.User(username='lo', hashed_password='2', email='N')
            session.add(creator)
            workspace = cm.Workspace(name=workspace_name, creator=creator, description='Test WF')
            session.add(workspace)
            creator.linked_workspaces = [workspace]

            user = cm.User(username=login, hashed_password='2', email='M', linked_workspaces=[workspace])
            session.add(user)
            for i in range(tasks_num):
                wf_task = cm.WFTask(name=f'Task_{i}',
                                    plan_deadline=datetime.datetime.now(),
                                    creator=creator,
                                    entrusted=creator,
                                    executors=[user],
                                    workspace=workspace,
                                    description=''
                                    )
                session.add(wf_task)

    def set_workspace_service_test_config(self, users_num: int):
        """
        Устанавливает конфиг для теста сервиса Workspace. (1 пользователь - создатель Workspace, 1 Workspace,
        users_num пользователей).
        """
        with self.session_maker() as session, session.begin():
            creator = cm.User(username='creator', hashed_password='s', email='ss')
            session.add(creator)
            workspace = cm.Workspace(name='wf_1', creator=creator)
            session.add(workspace)
            creator.linked_workspaces = [workspace]
            for i in range(users_num):
                user = cm.User(username=f'user_{i}', hashed_password='s', email=f'em{i}')
                session.add(user)


if __name__ == '__main__':

    db_manager = DatabaseManager('sqlite:///database')
    db_manager.set_workspace_service_test_config(15)
