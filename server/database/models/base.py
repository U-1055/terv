from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm.session import sessionmaker

import server.database.models.common_models as db


class Base(DeclarativeBase):

    fields = []  # Поля с данными об объекте
    one_links = []  # Поля со ссылками на одиночные объекты
    many_links = []  # Поля со ссылками на несколько объектов

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
    return engine


def config_db(engine):

    session = sessionmaker(bind=engine)

    with session() as s, s.begin():
        s.add(db.User(username='username', email='str', hashed_password=''))
        s.add(db.Workflow(creator_id=0, name='Workflow', description='description'))
        workflow = db.Workflow(creator_id=0, name='Workflow', description='description')
        for i in range(150):
            user = db.User(username=f'username#{i}', email=f'str[{i}]', hashed_password='')
            user.linked_workflows.append(workflow)
            s.add(user)


if __name__ == '__main__':
    import roles
    from sqlalchemy.sql import select

    engine = create_engine('sqlite:///')
    Base.metadata.create_all(bind=engine)

