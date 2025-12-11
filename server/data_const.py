import datetime
import enum


class DataStruct:

    date_format = '%d.%m.%Y'
    time_format = '%H:%M:%S'
    datetime_format = f'{date_format}-{time_format}'


class Permissions(enum.Enum):
    # Базовые доступы роли в Workflow
    del_wf = 'del_wf'
    del_project = 'del_project'
    create_event = 'create_event'
    del_event = 'del_event'
    edit_event = 'edit_event'
    create_task = 'create_task'
    del_task = 'del_task'
    edit_task = 'edit_task'
    complete_task = 'complete_task'
    invite = 'invite'
    kick = 'kick'
    create_doc = 'create_doc'
    dec_doc = 'del_doc'
    edit_doc = 'edit_doc'

    set_project = 'set_project'
    set_workflow = 'set_workflow'
    set_roles = 'set_roles'
    view_analytics = 'view_analytics'
    set_analytics = 'set_analytics'

    # Доступы просмотра конкретных ресурсов ()
    create = 'create'
    edit = 'edit'
    delete = 'delete'
    view = 'view'
