from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field, fields

import server.database.models.common_models as cm
import server.database.models.roles as roles


class BaseSchema(SQLAlchemyAutoSchema):
    class Meta:
        pass


class UserSchema(BaseSchema):
    class Meta:
        model = cm.User
        include_relationships = True
        load_only = ('hashed_password', )


class WorkflowSchema(BaseSchema):
    class Meta:
        model = cm.Workflow
        include_relationships = True


class WFTaskSchema(BaseSchema):
    class Meta:
        model = cm.WFTask
        include_relationships = True
    created_workflows = fields.Nested(WorkflowSchema, many=True)


class PersonalTaskSchema(BaseSchema):
    class Meta:
        model = cm.PersonalTask
        include_relationships = True


class WFRoleSchema(BaseSchema):
    class Meta:
        model = roles.WFRole
        include_relationships = True
