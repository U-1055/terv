from sqlalchemy.orm.session import Session, sessionmaker
from sqlalchemy.sql import select, insert, update, delete

import typing as tp

import server.database.models.common_models as cm
import server.database.models.roles as roles


def repo_request(func: tp.Callable):  # Декоратор для обработки limit\offset

    def complete(*args, **kwargs):
        limit = kwargs.get('limit')
        offset = kwargs.get('offset')

        result = func(*args, **kwargs)

        if not limit:
            limit = len(result)
        if not offset:
            offset = 0

        if offset < 0:   # Некорректные значения limit\offset
            offset = 0
        if limit < 0:
            limit = None

        if offset >= len(result):  # offset больше\равен индексу последнего элемента
            return {'left': len(result), 'result': []}
        if limit >= len(result) or limit + offset >= len(result):  # limit больше длины или limit с offset больше длины => лимит отсутствует
            limit = None

        result = result[offset:]
        last_record_idx = len(result) - 1

        if limit:
            result = result[:limit]
        return {'left': result - last_record_idx - 1, 'result': result}

    return complete


class DataRepository:

    def __init__(self, session_maker: sessionmaker):
        self._session_maker = session_maker

    def get_users(self, workflow_id: int = None, project_id: int = None, user_id: int = None, limit: int = None, offset: int = None) -> dict:
        query = select(cm.User).limit(limit).offset(offset)

        with self._session_maker() as session, session.begin():
            users = session.execute(query).tuples()
            return tuple(users)


if __name__ == '__main__':
    from server.database.models.base import init_db, config_db
    engine = init_db()
    config_db(engine)
    repo = DataRepository(sessionmaker(bind=engine))
    users = repo.get_users(offset=20)
    assert len(users) == 131, len(users)
