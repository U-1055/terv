import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):

    fields = ['id', 'created_at', 'updated_at']  # Поля с данными об объекте
    one_links = []  # FK объектов otm-отношений
    many_links = []  # Поля со ссылками на несколько объектов

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now())

    def serialize(self) -> dict:
        result = {element: getattr(self, element) for element in dir(self) if element in [*self.fields, *self.one_links]}
        result.update(
            {
                element:
                    [obj.id for obj in getattr(self, element)]
                for element in dir(self) if element in self.many_links
            }
        )

        return result


if __name__ == '__main__':
    from server.database.models.db_utils import init_db
    from server.database.models.roles import *
    init_db('sqlite:///../database')