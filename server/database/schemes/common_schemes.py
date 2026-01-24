from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field, fields
from sqlalchemy.orm.session import Session

import server.database.models.common_models as cm
import server.database.models.roles as roles


class BaseSchema(SQLAlchemyAutoSchema):
    class Meta:
        sqla_session: Session = Session


class UserSchema(BaseSchema):  # ToDo: как возвращать хэш пароля?
    class Meta:
        model = cm.User
        include_relationships = True
        include_fk = True
        load_only = ('hashed_password', )
        load_instance = True


class WorkflowSchema(BaseSchema):
    class Meta:
        model = cm.Workflow
        include_fk = True
        include_relationships = True
        load_instance = True


class WFTaskSchema(BaseSchema):
    class Meta:
        model = cm.WFTask
        include_fk = True
        load_instance = True
        include_relationships = True
    created_workflows = fields.Nested(WorkflowSchema, many=True)


class PersonalTaskSchema(BaseSchema):
    class Meta:
        model = cm.PersonalTask
        include_fk = True
        include_relationships = True
        load_instance = True


class WFRoleSchema(BaseSchema):
    class Meta:
        model = roles.WFRole
        include_fk = True
        include_relationships = True
        load_instance = True
