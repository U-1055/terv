from sqlalchemy.orm.session import Session, sessionmaker
from sqlalchemy.sql import select, insert, update, delete
import models as db


class DataRepository:

    def __init__(self, session_maker: sessionmaker):
        self._session_maker = session_maker

    def get_users(self, workflow_id: int = None, project_id: int = None, user_id: int = None) -> tuple:
        query = select(db.User).where()
        with self._session_maker() as session, session.begin():
            users = session.execute(query)

