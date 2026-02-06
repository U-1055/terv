from pydantic import Field, BaseModel


import datetime
import typing as tp


class Base(BaseModel):

    id: int
    created_at: datetime.datetime = Field(default=datetime.datetime.now())
    updated_at: datetime.datetime = Field(default=datetime.datetime.now())

    def serialize(self) -> dict:
        result = {element: getattr(self, element) for element in list(self.model_fields.keys())}
        return result
