"""
Схемы моделей SQLAlchemy.

"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_sqlalchemy.fields import fields
from marshmallow import EXCLUDE, post_dump, pre_load
from sqlalchemy.orm.session import Session

from server.data_const import DBStruct
import server.database.models.common_models as cm
from common.base import DBFields


class BaseMeta:
    load_instance = True
    include_relationships = True
    include_fk = True
    dump_only = ("id", "created_at")
    unknown = EXCLUDE


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
    creator_id = fields.Int(load_only=True)
    creator = auto_field(dump_only=True)
    description = fields.Str(load_default=DBStruct.default_description)


class ProjectSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.Project
    workspace_id = fields.Int(load_only=True)
    workspace = auto_field(dump_only=True)
    creator_id = fields.Int(load_only=True)
    creator = auto_field(dump_only=True)
    description = fields.Str(load_default=DBStruct.default_description)


class WSTaskSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.WSTask
    workspace_id = fields.Int(load_only=True)
    workspace = auto_field(dump_only=True)
    project_id = fields.Int(load_only=True)
    project = auto_field(dump_only=True)
    creator_id = fields.Int(load_only=True)
    creator = auto_field(dump_only=True)
    entrusted_id = fields.Int(load_only=True)
    entrusted = auto_field(dump_only=True)
    work_direction_id = fields.Int(load_only=True)
    work_direction = auto_field(dump_only=True)
    parent_task_id = fields.Int(load_only=True)
    parent_task = auto_field(dump_only=True)
    status_id = fields.Int(load_only=True)
    status = auto_field(dump_only=True)
    description = fields.Str(load_default=DBStruct.default_description)


class PersonalTaskSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.PersonalTask
    owner_id = fields.Int(load_only=True)
    owner = auto_field(dump_only=True)
    work_direction_id = fields.Int(load_only=True)
    work_direction = auto_field(dump_only=True)
    parent_task_id = fields.Int(load_only=True)
    parent_task = auto_field(dump_only=True)
    status_id = fields.Int(load_only=True)
    status = auto_field(dump_only=True)
    description = fields.Str(load_default=DBStruct.default_description)


class WSWorkDirectionSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.WSWorkDirection
    workspace_id = fields.Int(load_only=True)
    workspace = auto_field(dump_only=True)


class PersonalWorkDirectionSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.PersonalWorkDirection
    owner_id = fields.Int(load_only=True)
    owner = auto_field(dump_only=True)


class PersonalDailyEventSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.PersonalDailyEvent
    owner_id = fields.Int(load_only=True)
    owner = auto_field(dump_only=True)
    description = fields.Str(load_default=DBStruct.default_description)


class PersonalManyDaysEventSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.PersonalManyDaysEvent
    owner_id = fields.Int(load_only=True)
    owner = auto_field(dump_only=True)
    description = fields.Str(load_default=DBStruct.default_description)


class WSDailyEventSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.WSDailyEvent
    workspace_id = fields.Int(load_only=True)
    workspace = auto_field(dump_only=True)
    creator_id = fields.Int(load_only=True)
    creator = auto_field(dump_only=True)
    description = fields.Str(load_default=DBStruct.default_description)


class WSManyDaysEventSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.WSManyDaysEvent
    workspace_id = fields.Int(load_only=True)
    workspace = auto_field(dump_only=True)
    creator_id = fields.Int(load_only=True)
    creator = auto_field(dump_only=True)
    description = fields.Str(load_default=DBStruct.default_description)


class WSBaseCategorySchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.WSBaseCategory
    workspace_id = fields.Int(load_only=True)
    workspace = auto_field(dump_only=True)
    parent_category_id = fields.Int(load_only=True)
    parent_category = auto_field(dump_only=True)
    description = fields.Str(load_default=DBStruct.default_description)


class WSDocumentSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.WSDocument
    workspace_id = fields.Int(load_only=True)
    workspace = auto_field(dump_only=True)
    creator_id = fields.Int(load_only=True)
    creator = auto_field(dump_only=True)
    base_category_id = fields.Int(load_only=True)
    base_category = auto_field(dump_only=True)


class WSTaskTagSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.WSTaskTag
    workspace_id = fields.Int(load_only=True)
    workspace = auto_field(dump_only=True)
    description = fields.Str(load_default=DBStruct.default_description)


class WSTaskStatusSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.WSTaskStatus
    workspace_id = fields.Int(load_only=True)
    workspace = auto_field(dump_only=True)
    description = fields.Str(load_default=DBStruct.default_description)


class PersonalTaskTagSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.PersonalTaskTag
    owner_id = fields.Int(load_only=True)
    owner = auto_field(dump_only=True)
    description = fields.Str(load_default=DBStruct.default_description)


class PersonalTaskStatusSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.PersonalTaskStatus
    owner_id = fields.Int(load_only=True)
    owner = auto_field(dump_only=True)
    description = fields.Str(load_default=DBStruct.default_description)


class WSRoleSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.WSRole
    workspace_id = fields.Int(load_only=True)
    workspace = auto_field(dump_only=True)


class PermissionSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.Permission


class WSRoleTaskSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.WSRoleTask
    role_id = fields.Int(load_only=True)
    task_id = fields.Int(load_only=True)


class WSRoleProjectSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.WSRoleProject
    role_id = fields.Int(load_only=True)
    project_id = fields.Int(load_only=True)


class WSRoleDailyEventSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.WSRoleDailyEvent
    role_id = fields.Int(load_only=True)
    daily_event_id = fields.Int(load_only=True)


class WSRoleManyDaysEventSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.WSRoleManyDaysEvent
    role_id = fields.Int(load_only=True)
    many_days_event_id = fields.Int(load_only=True)


class WSRoleDocumentSchema(BaseSchema):

    class Meta(BaseMeta):
        model = cm.WSRoleDocument
    role_id = fields.Int(load_only=True)
    document_id = fields.Int(load_only=True)


if __name__ == '__main__':
    for model in dir(cm):
        print(
            f'class {model}Schema(BaseSchema):\n'
            f'    class Meta(BaseMeta):\n'
            f'        model = cm.{model}\n\n'
        )
