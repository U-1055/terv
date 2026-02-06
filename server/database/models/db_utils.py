import datetime

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import insert

import server.database.models.roles as roles
import server.database.models.common_models as cm
from server.data_const import Permissions


def init_db(path: str) -> Engine:
    """Создаёт базу заново и возвращает её движок."""
    engine = create_engine(path)
    cm.Base.metadata.drop_all(bind=engine)
    cm.Base.metadata.create_all(bind=engine)  # ToDo: в app.py ошибка при добавлении permissions через add_permissions
    add_permissions(engine)
    return engine


def launch_db(path: str) -> Engine:
    """Возвращает движок уже созданной базы данных."""
    engine = create_engine(path)
    return engine


def add_permissions(engine: Engine):
    session = sessionmaker(bind=engine)
    with session() as s, s.begin():
        s.execute(insert(roles.Permission), [{'type': type_} for type_ in Permissions.__dict__])
