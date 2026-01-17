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
        self._session_maker = sessionmaker(bind=engine)

    def set_authentication_test_config(self):
        with self._session_maker() as session, session.begin():
            session.execute(delete(cm.User))

    def set_limit_offset_test_config(self, login: str, password: str, email: str, tasks_num: int):
        """Устанавливает конфиг для теста обработки limit&offset"""
        with self._session_maker() as session, session.begin():
            creator = cm.User(username='lo', hashed_password='ps', email='email1')
            session.add(creator)

            workflow = cm.Workflow(name='wf1', creator=creator, description='')
            session.add(workflow)

            user = cm.User(username=login, hashed_password=hash_password(password), email=email)
            session.add(user)

        with self._session_maker() as session, session.begin():
            workflow = session.execute(select(cm.Workflow).where(cm.Workflow.name == 'wf1')).scalars().one()
            user = session.execute(select(cm.User).where(cm.User.username == login)).scalars().one()
            creator = session.execute(select(cm.User).where(cm.User.username == 'lo')).scalars().one()

            tasks = []
            for i in range(tasks_num):
                task = cm.WFTask(name=f'wf_task_{i}',
                              plan_deadline=datetime.datetime.now(),
                              creator=creator,
                              entrusted=creator,
                              executors=[user],
                              workflow=workflow,
                              description=''
                              )
                tasks.append(task)

            session.add_all(tasks)


if __name__ == '__main__':

    db_manager = DatabaseManager('sqlite:///database')
    db_manager.set_limit_offset_test_config('log', 'pass', 'em', 15)
