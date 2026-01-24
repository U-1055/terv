import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from common.base import CommonStruct, get_datetime_now


class Base(DeclarativeBase):

    fields = ['id', 'created_at', 'updated_at']  # Поля с данными об объекте
    one_links = []  # FK объектов otm-отношений
    many_links = []  # Поля со ссылками на несколько объектов

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=get_datetime_now())
    updated_at: Mapped[datetime.datetime] = mapped_column(default=get_datetime_now())


if __name__ == '__main__':
    from server.database.models.db_utils import init_db
    from server.database.models.roles import *
    init_db('sqlite:///../database')
