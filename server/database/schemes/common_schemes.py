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


class WorkflowSchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.Workflow


class WFTaskSchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.WFTask


class PersonalTaskSchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.PersonalTask


class WFRoleSchema(BaseSchema):
    class Meta(BaseMeta):
        model = roles.WFRole


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


class WFBaseCategorySchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.WFBaseCategory


class WFDailyEventSchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.WFDailyEvent


class WFDocumentSchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.WFDocument


class WFManyDaysEventSchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.WFManyDaysEvent


class WFWorkDirectionSchema(BaseSchema):
    class Meta(BaseMeta):
        model = cm.WFWorkDirection


if __name__ == '__main__':
    for model in dir(cm):
        print(
            f'class {model}Schema(BaseSchema):\n'
            f'    class Meta(BaseMeta):\n'
            f'        model = cm.{model}\n'
        )
