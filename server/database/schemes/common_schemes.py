from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy.orm.session import Session

import server.database.models.common_models as cm
import server.database.models.roles as roles


class BaseMeta:
    load_instance = True
    include_relationships = True
    include_fk = True


class BaseSchema(SQLAlchemyAutoSchema):
    class Meta(BaseMeta):
        sqla_session: Session = Session


class UserSchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.User
        load_only = ('hashed_password', )


class WorkspaceSchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.Workspace


class WSTaskSchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.WSTask


class PersonalTaskSchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.PersonalTask


class wsRoleSchema(BaseSchema):
    class Meta(BaseMeta):
        model = roles.wsRole


class PersonalDailyEventSchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.PersonalDailyEvent


class PersonalManyDaysEventSchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.PersonalManyDaysEvent


class PersonalWorkDirectionSchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.PersonalWorkDirection


class ProjectSchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.Project


class WSBaseCategorySchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.WSBaseCategory


class WSDailyEventSchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.WSDailyEvent


class WSDocumentSchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.WSDocument


class WSManyDaysEventSchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.WSManyDaysEvent


class WSWorkDirectionSchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.WSWorkDirection


if __name__ == '__main__':
    for model in dir(cm):
        print(
            f'class {model}Schema(BaseSchema):\n'
            f'    class Meta(BaseMeta):\n'
            f'        model = cm.{model}\n'
        )
