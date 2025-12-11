import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql import insert

import server.database.models.common_models as db
from server.data_const import Permissions


class Base(DeclarativeBase):

    fields = ['id', 'created_at', 'updated_at']  # Поля с данными об объекте
    one_links = []  # Поля со ссылками на одиночные объекты
    many_links = []  # Поля со ссылками на несколько объектов

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now())

    def serialize(self) -> dict:
        result = {element: getattr(self, element) for element in dir(self) if element in self.fields}
        result.update({f'{element}_id': getattr(self, element).id for element in dir(self) if element in self.one_links})
        result.update(
            {
                f'{element}_id':
                    [obj.id for obj in getattr(self, element)]
                for element in dir(self) if element in self.many_links
            }
        )

        return result


def init_db() -> Engine:
    engine = create_engine('sqlite:///')
    Base.metadata.create_all(bind=engine)
    add_permissions(engine)
    return engine


def add_permissions(engine):
    import server.database.models.roles as roles
    session = sessionmaker(bind=engine)
    with session() as s, s.begin():
        s.execute(insert(roles.Permission), [{'type': type_} for type_ in Permissions.__dict__])


def config_db(engine):

    session = sessionmaker(bind=engine)

    with session() as s, s.begin():
        workflow = db.Workflow(creator_id=0, name='Workflow', description='description')
        s.add(db.User(username='username', email='str', hashed_password=''))
        s.add(workflow)

        for i in range(150):
            user = db.User(username=f'username#{i}', email=f'str[{i}]', hashed_password='')
            user.linked_workflows.append(workflow)
            s.add(user)
        s.commit()


if __name__ == '__main__':
    from server.database.repository import DataRepository
    from server.database.models.common_models import *

    engine = create_engine('sqlite:///')
    Base.metadata.create_all(bind=engine)
    config_db(engine)
    s = sessionmaker(bind=engine)

    repo = DataRepository(s)

    print(repo.get_workflows())