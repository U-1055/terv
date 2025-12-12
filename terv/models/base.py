import datetime

from pydantic import Field, BaseModel
import server.database.models.common_models as db
from server.data_const import Permissions


class Base(BaseModel):

    fields = ['id', 'created_at', 'updated_at']  # Поля с данными об объекте
    one_links = []  # FK объектов otm-отношений
    many_links = []  # Поля со ссылками на несколько объектов

    id: int
    created_at: datetime.datetime = Field(default=datetime.datetime.now())
    updated_at: datetime.datetime = Field(default=datetime.datetime.now())

    def serialize(self) -> dict:
        result = {element: getattr(self, element) for element in dir(self) if
                  element in [*self.fields, *self.one_links]}
        result.update(
            {
                element:
                    [obj.id for obj in getattr(self, element)]
                for element in dir(self) if element in self.many_links
            }
        )

        return result