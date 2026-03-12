from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy import ForeignKey, Table, Column, Integer
from sqlalchemy.types import String

import datetime

from server.database.models.base import Base
from server.data_const import DBStruct


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String[60], unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String[60], unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String[60], nullable=False)
    completed_task_status_id: Mapped[int] = mapped_column(nullable=True)  # ID статуса выполненной задачи
    default_task_status_id: Mapped[int] = mapped_column(nullable=True)  # ID статуса задачи по умолчанию

    # РП и проекты
    created_workspaces: Mapped[list['Workspace']] = relationship('Workspace', back_populates='creator')
    created_projects: Mapped[list['Project']] = relationship('Project', back_populates='creator')
    linked_workspaces: Mapped[list['Workspace']] = relationship(secondary='workspace_user', back_populates='users')
    linked_projects: Mapped[list['Project']] = relationship(secondary='project_user', back_populates='users')

    # Задачи
    created_ws_tasks: Mapped[list['WSTask']] = relationship('WSTask', foreign_keys='WSTask.creator_id',
                                                            back_populates='creator')  # Созданные задачи workspace
    assigned_to_user_tasks: Mapped[list['WSTask']] = relationship(secondary='executor_task',
                                                                  back_populates='executors')  # Порученные пользователЮ
    assigned_by_user_tasks: Mapped[list['WSTask']] = relationship('WSTask', foreign_keys='WSTask.entrusted_id',
                                                                  back_populates='entrusted')  # Порученные пользователЕМ
    responsibility_tasks: Mapped[list['WSTask']] = relationship(secondary='responsible_task',
                                                                back_populates='responsible')  # Задачи, где пользователь назначен ответственным

    created_personal_tasks: Mapped[list['PersonalTask']] = relationship('PersonalTask',
                                                                        back_populates='owner')  # Личные задачи
    # Роли
    roles: Mapped[list['WSRole']] = relationship(secondary='user_ws_role', back_populates='users')

    # Документы РП
    created_ws_documents: Mapped[list['WSDocument']] = relationship('WSDocument', back_populates='creator')

    # Мероприятия
    created_ws_daily_events: Mapped[list['WSDailyEvent']] = relationship('WSDailyEvent', back_populates='creator')
    created_ws_many_days_events: Mapped[list['WSManyDaysEvent']] = relationship('WSManyDaysEvent', back_populates='creator')
    notified_daily_events: Mapped[list['WSDailyEvent']] = relationship(secondary='ws_daily_event_user',
                                                                       back_populates='notified')
    notified_many_days_events: Mapped[list['WSManyDaysEvent']] = relationship(secondary='ws_many_days_event_user',
                                                                              back_populates='notified')

    # Личные объекты
    work_directions: Mapped[list['PersonalWorkDirection']] = relationship('PersonalWorkDirection', back_populates='owner')
    personal_daily_events: Mapped[list['PersonalDailyEvent']] = relationship('PersonalDailyEvent', back_populates='owner')
    personal_many_days_events: Mapped[list['PersonalManyDaysEvent']] = relationship('PersonalManyDaysEvent', back_populates='owner')
    tags: Mapped[list['PersonalTaskTag']] = relationship('PersonalTaskTag', back_populates='owner')
    statuses: Mapped[list['PersonalTaskStatus']] = relationship('PersonalTaskStatus', back_populates='owner')


class Workspace(Base):
    """Рабочее пространство."""

    __tablename__ = 'workspace'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    default_role_id: Mapped[int] = mapped_column(nullable=True)
    completed_task_status_id: Mapped[int] = mapped_column(nullable=True)  # ID статуса выполненной задачи
    default_task_status_id: Mapped[int] = mapped_column(nullable=True)  # ID статуса задачи по умолчанию
    name: Mapped[str] = mapped_column(String[60])
    description: Mapped[str] = mapped_column(String[1000], default=DBStruct.default_description)

    projects: Mapped[list['Project']] = relationship('Project', back_populates='workspace')
    tasks: Mapped[list['WSTask']] = relationship('WSTask', back_populates='workspace')
    users: Mapped[list['User']] = relationship(secondary='workspace_user', back_populates='linked_workspaces')
    creator: Mapped[User] = relationship(User, back_populates='created_workspaces')
    work_directions: Mapped[list['WSWorkDirection']] = relationship('WSWorkDirection', back_populates='workspace')
    documents: Mapped[list['WSDocument']] = relationship('WSDocument', back_populates='workspace')
    base_categories: Mapped[list['WSBaseCategory']] = relationship('WSBaseCategory', back_populates='workspace')
    daily_events: Mapped[list['WSDailyEvent']] = relationship('WSDailyEvent', back_populates='workspace')
    many_days_events: Mapped[list['WSManyDaysEvent']] = relationship('WSManyDaysEvent', back_populates='workspace')
    tags: Mapped[list['WSTaskTag']] = relationship('WSTaskTag', back_populates='workspace')
    statuses: Mapped[list['WSTaskStatus']] = relationship('WSTaskStatus', back_populates='workspace')
    roles: Mapped[list['WSRole']] = relationship('WSRole', back_populates='workspace')


class Project(Base):
    """Проект."""
    __tablename__ = 'project'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey(Workspace.id))
    creator_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    name: Mapped[str] = mapped_column(String[60])
    description: Mapped[str] = mapped_column(String[1000], default=DBStruct.default_description)

    workspace: Mapped[Workspace] = relationship(Workspace, back_populates='projects')
    users: Mapped[list[User]] = relationship(secondary='project_user', back_populates='linked_projects')
    creator: Mapped[User] = relationship(User, back_populates='created_projects')
    tasks: Mapped[list['WSTask']] = relationship('WSTask', back_populates='project')


project_user = Table(
    'project_user',
    Base.metadata,
    Column('user_id', ForeignKey('user.id'), primary_key=True),
    Column('project_id', ForeignKey('project.id'), primary_key=True)
)

executor_task = Table(
    'executor_task',
    Base.metadata,
    Column('executor_id', ForeignKey('user.id'), primary_key=True),
    Column('task_id', ForeignKey('ws_task.id'), primary_key=True)

)

responsible_task = Table(
    'responsible_task',
    Base.metadata,
    Column('user_id', ForeignKey('user.id'), primary_key=True),
    Column('task_id', ForeignKey('ws_task.id'), primary_key=True)
)

ws_daily_event_user = Table(
    'ws_daily_event_user',
    Base.metadata,
    Column('user_id', ForeignKey('user.id'), primary_key=True),
    Column('event_id', ForeignKey('ws_daily_event.id'), primary_key=True)
)

ws_many_days_event_user = Table(
    'ws_many_days_event_user',
    Base.metadata,
    Column('user_id', ForeignKey('user.id'), primary_key=True),
    Column('event_id', ForeignKey('ws_many_days_event.id'), primary_key=True)
)

workspace_user = Table(
    'workspace_user',
    Base.metadata,
    Column('workspace_id', ForeignKey('workspace.id'), primary_key=True),
    Column('user_id', ForeignKey('user.id'), primary_key=True)
)

user_role = Table(
    'user_ws_role',
    Base.metadata,
    Column('user_id', ForeignKey('user.id'), primary_key=True),
    Column('role_id', ForeignKey('ws_role.id'), primary_key=True)
)

tag_ws_task = Table(
    'tag_ws_task',
    Base.metadata,
    Column('ws_task_id', ForeignKey('ws_task.id'), primary_key=True),
    Column('ws_task_tag_id', ForeignKey('ws_task_tag.id'), primary_key=True)
)

tag_personal_task = Table(
    'tag_personal_task',
    Base.metadata,
    Column('personal_task_id', ForeignKey('personal_task.id'), primary_key=True),
    Column('personal_task_tag_id', ForeignKey('personal_task_tag.id'), primary_key=True)
)


class WSTask(Base):
    """Задача РП."""

    __tablename__ = 'ws_task'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey(Workspace.id))  # РП
    project_id: Mapped[int] = mapped_column(ForeignKey(Project.id), nullable=True)  # Проект
    creator_id: Mapped[int] = mapped_column(ForeignKey(User.id))  # Создатель
    entrusted_id: Mapped[int] = mapped_column(ForeignKey(User.id))  # Поручивший
    work_direction_id: Mapped[int] = mapped_column(ForeignKey('ws_work_direction.id'), nullable=True)  # Направление работы
    parent_task_id: Mapped[int] = mapped_column(ForeignKey('ws_task.id'), nullable=True)  # Родительская задача
    status_id: Mapped[int] = mapped_column(ForeignKey('ws_task_status.id'))  # Статус задачи

    name: Mapped[str] = mapped_column(String[60])
    description: Mapped[str] = mapped_column(String[1000], default=DBStruct.default_description)
    plan_deadline: Mapped[datetime.datetime] = mapped_column()
    fact_deadline: Mapped[datetime.datetime] = mapped_column(nullable=True)
    plan_time: Mapped[datetime.datetime] = mapped_column(nullable=True)
    fact_time: Mapped[datetime.datetime] = mapped_column(nullable=True)
    plan_start_work_date: Mapped[datetime.datetime] = mapped_column(nullable=True)
    fact_start_work_date: Mapped[datetime.datetime] = mapped_column(nullable=True)

    responsible: Mapped[list[User]] = relationship(secondary='responsible_task', back_populates='responsibility_tasks')
    executors: Mapped[list[User]] = relationship(secondary='executor_task', back_populates='assigned_to_user_tasks')
    creator: Mapped[User] = relationship(User, foreign_keys='WSTask.creator_id', back_populates='created_ws_tasks')
    entrusted: Mapped[User] = relationship(User, foreign_keys='WSTask.entrusted_id', back_populates='assigned_by_user_tasks')
    workspace: Mapped[Workspace] = relationship(Workspace, back_populates='tasks')
    work_direction: Mapped[Workspace] = relationship('WSWorkDirection', back_populates='tasks')
    parent_task: Mapped['WSTask'] = relationship('WSTask', back_populates='child_tasks', remote_side='WSTask.id')
    child_tasks: Mapped[list['WSTask']] = relationship('WSTask', back_populates='parent_task')
    project: Mapped[Project] = relationship(Project, back_populates='tasks')
    status: Mapped['WSTaskStatus'] = relationship('WSTaskStatus', back_populates='tasks')
    tags: Mapped['WSTaskTag'] = relationship(secondary='tag_ws_task', back_populates='tasks')
    task_events: Mapped[list['WSTaskEvent']] = relationship('WSTaskEvent', back_populates='task')


class PersonalTask(Base):
    """Личная задача"""
    __tablename__ = 'personal_task'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    work_direction_id: Mapped[int] = mapped_column(ForeignKey('personal_work_direction.id'), nullable=True)
    parent_task_id: Mapped[int] = mapped_column(ForeignKey('personal_task.id'), nullable=True)
    status_id: Mapped[int] = mapped_column(ForeignKey('personal_task_status.id'))

    name: Mapped[str] = mapped_column(String[60], nullable=False)
    description: Mapped[str] = mapped_column(String[1000], default=DBStruct.default_description)
    plan_deadline: Mapped[datetime.datetime] = mapped_column(nullable=False)
    fact_deadline: Mapped[datetime.datetime] = mapped_column(nullable=True)
    plan_time: Mapped[datetime.datetime] = mapped_column(nullable=True)
    fact_time: Mapped[datetime.datetime] = mapped_column(nullable=True)
    plan_start_work_date: Mapped[datetime.datetime] = mapped_column(nullable=True)
    fact_start_work_date: Mapped[datetime.datetime] = mapped_column(nullable=True)

    owner: Mapped[User] = relationship(User, back_populates='created_personal_tasks')
    work_direction: Mapped['PersonalWorkDirection'] = relationship('PersonalWorkDirection', back_populates='tasks')
    parent_task: Mapped['PersonalTask'] = relationship('PersonalTask', back_populates='child_tasks', remote_side='PersonalTask.id')
    child_tasks: Mapped[list['PersonalTask']] = relationship('PersonalTask', back_populates='parent_task')
    status: Mapped['PersonalTaskStatus'] = relationship('PersonalTaskStatus', back_populates='tasks')
    tags: Mapped['PersonalTaskTag'] = relationship(secondary='tag_personal_task', back_populates='tasks')
    task_events: Mapped[list['PersonalTaskEvent']] = relationship('PersonalTaskEvent', back_populates='task')


class WSWorkDirection(Base):
    """Направление работы РП"""
    __tablename__ = 'ws_work_direction'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey('workspace.id'))
    name: Mapped[str] = mapped_column(String[60])

    workspace: Mapped[Workspace] = relationship(Workspace, back_populates='work_directions')
    tasks: Mapped[list[WSTask]] = relationship(WSTask, back_populates='work_direction')


class PersonalWorkDirection(Base):
    """Личное направление работы"""
    __tablename__ = 'personal_work_direction'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    name: Mapped[str] = mapped_column(String[60])

    owner: Mapped[Workspace] = relationship(User, back_populates='work_directions')
    tasks: Mapped[list[WSTask]] = relationship(PersonalTask, back_populates='work_direction')


class PersonalDailyEvent(Base):
    """Личное однодневное мероприятие."""
    __tablename__ = 'personal_daily_event'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('user.id'))

    name: Mapped[str] = mapped_column(String[60])
    description: Mapped[str] = mapped_column(String[1000], default=DBStruct.default_description)
    date: Mapped[datetime.date] = mapped_column()
    time_start: Mapped[datetime.time] = mapped_column()
    time_end: Mapped[datetime.time] = mapped_column()

    owner: Mapped[User] = relationship(User, back_populates='personal_daily_events')


class PersonalManyDaysEvent(Base):
    """Личное многодневное мероприятие."""
    __tablename__ = 'personal_many_days_event'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    name: Mapped[str] = mapped_column(String[60])
    description: Mapped[str] = mapped_column(String[1000], default=DBStruct.default_description)
    datetime_start: Mapped[datetime.datetime] = mapped_column()
    datetime_end: Mapped[datetime.datetime] = mapped_column()

    owner: Mapped[User] = relationship(User, back_populates='personal_many_days_events')


class WSDailyEvent(Base):
    """Однодневное мероприятие РП."""
    __tablename__ = 'ws_daily_event'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey('workspace.id'))
    creator_id: Mapped[int] = mapped_column(ForeignKey('user.id'))

    name: Mapped[str] = mapped_column(String[60])
    description: Mapped[str] = mapped_column(String[1000], default=DBStruct.default_description)
    date: Mapped[datetime.date] = mapped_column()
    time_start: Mapped[datetime.time] = mapped_column()
    time_end: Mapped[datetime.time] = mapped_column()

    creator: Mapped[User] = relationship(User, back_populates='created_ws_daily_events')
    notified: Mapped[list['User']] = relationship(secondary='ws_daily_event_user', back_populates='notified_daily_events')  # Оповещаемые пользователи
    workspace: Mapped[Workspace] = relationship(Workspace, back_populates='daily_events')


class WSManyDaysEvent(Base):
    """Многодневное мероприятие РП."""
    __tablename__ = 'ws_many_days_event'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey('workspace.id'))
    creator_id: Mapped[int] = mapped_column(ForeignKey('user.id'))

    name: Mapped[str] = mapped_column(String[60])
    description: Mapped[str] = mapped_column(String[1000], default=DBStruct.default_description)
    datetime_start: Mapped[datetime.datetime] = mapped_column()
    datetime_end: Mapped[datetime.datetime] = mapped_column()

    creator: Mapped[User] = relationship(User, back_populates='created_ws_many_days_events')
    notified: Mapped[list['User']] = relationship(secondary='ws_many_days_event_user', back_populates='notified_many_days_events')  # Оповещаемые пользователи
    workspace: Mapped[Workspace] = relationship(Workspace, back_populates='many_days_events')


class WSBaseCategory(Base):
    """Раздел базы РП."""
    __tablename__ = 'ws_base_category'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey('workspace.id'))
    parent_category_id: Mapped[int] = mapped_column(ForeignKey('ws_base_category.id'), nullable=True)
    name: Mapped[str] = mapped_column(String[60])
    description: Mapped[str] = mapped_column(String[1000], default=DBStruct.default_description)

    parent_category: Mapped['WSBaseCategory'] = relationship('WSBaseCategory', back_populates='child_categories', remote_side='WSBaseCategory.id')
    child_categories: Mapped['WSBaseCategory'] = relationship('WSBaseCategory', back_populates='parent_category')
    workspace: Mapped[Workspace] = relationship(Workspace, back_populates='base_categories')
    documents: Mapped[list['WSDocument']] = relationship('WSDocument', back_populates='base_category')


class WSDocument(Base):
    """
    Документ базы РП.
    В key-value базе /database/data/data под id документа хранится его контент.
    """
    __tablename__ = 'ws_document'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey('workspace.id'))
    creator_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    base_category_id: Mapped[WSBaseCategory] = mapped_column(ForeignKey('ws_base_category.id'))

    workspace: Mapped[Workspace] = relationship(Workspace, back_populates='documents')
    creator: Mapped[User] = relationship(User, back_populates='created_ws_documents')
    base_category: Mapped[WSBaseCategory] = relationship(WSBaseCategory, back_populates='documents')


class WSTaskTag(Base):
    """Метка задачи РП."""
    __tablename__ = 'ws_task_tag'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey('workspace.id'))
    name: Mapped[str] = mapped_column(String[60])
    description: Mapped[str] = mapped_column(String[1000], default=DBStruct.default_description)
    workspace: Mapped[Workspace] = relationship(Workspace, back_populates='tags')
    tasks: Mapped[list[WSTask]] = relationship(secondary='tag_ws_task', back_populates='tags')


class WSTaskStatus(Base):
    """Статус задачи РП."""
    __tablename__ = 'ws_task_status'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey('workspace.id'))

    name: Mapped[str] = mapped_column(String[60])
    description: Mapped[str] = mapped_column(String[1000], default=DBStruct.default_description)
    workspace: Mapped[Workspace] = relationship(Workspace, back_populates='statuses')
    tasks: Mapped[list[WSTask]] = relationship(WSTask, back_populates='status')


class PersonalTaskTag(Base):
    """Метка личной задачи."""
    __tablename__ = 'personal_task_tag'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('user.id'))

    name: Mapped[int] = mapped_column(String[60])
    description: Mapped[str] = mapped_column(String[1000], default=DBStruct.default_description)
    owner: Mapped[User] = relationship(User, back_populates='tags')
    tasks: Mapped[list[PersonalTask]] = relationship(secondary='tag_personal_task', back_populates='tags')


class PersonalTaskStatus(Base):
    """Статус личной задачи."""
    __tablename__ = 'personal_task_status'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('user.id'))

    name: Mapped[int] = mapped_column(String[60])
    description: Mapped[str] = mapped_column(String[1000], default=DBStruct.default_description)
    owner: Mapped[User] = relationship(User, back_populates='statuses')
    tasks: Mapped[list[PersonalTask]] = relationship(PersonalTask, back_populates='status')


class PersonalTaskEvent(Base):
    """Мероприятие - личная задача."""
    __tablename__ = 'personal_task_event'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('personal_task.id'))

    date: Mapped[datetime.date] = mapped_column()
    time_start: Mapped[datetime.time] = mapped_column()
    time_end: Mapped[datetime.time] = mapped_column()

    task: Mapped[PersonalTask] = relationship(PersonalTask, back_populates='task_events')


class WSTaskEvent(Base):
    """Мероприятие - задача РП."""
    __tablename__ = 'ws_task_event'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('ws_task.id'))

    date: Mapped[datetime.date] = mapped_column()
    time_start: Mapped[datetime.time] = mapped_column()
    time_end: Mapped[datetime.time] = mapped_column()

    task: Mapped[WSTask] = relationship(WSTask, back_populates='task_events')


class WSRole(Base):
    """Роль рабочего пространства."""
    __tablename__ = 'ws_role'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey('workspace.id'))
    name: Mapped[str] = mapped_column(String[60])
    color: Mapped[str] = mapped_column(String[30], default='#FFFFFF')

    permissions: Mapped[list['Permission']] = relationship(secondary='ws_role_permission', back_populates='roles')
    users: Mapped[list[User]] = relationship(secondary='user_ws_role', back_populates='roles')
    workspace: Mapped[Workspace] = relationship(Workspace, back_populates='roles')

    fields = ['workspace_id', 'name', 'color']
    many_links = ['users', 'permissions']


class Permission(Base):
    """Разрешение (доступ)"""
    __tablename__ = 'permission'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String[60], unique=True)  # Тип разрешения (CRUD-<Объект>)

    roles: Mapped[list[WSRole]] = relationship(secondary='ws_role_permission', back_populates='permissions')
    project_roles: Mapped[list['WSRoleProject']] = relationship(secondary='ws_role_project_permission',
                                                                back_populates='permissions')
    task_roles: Mapped[list['WSRoleTask']] = relationship(secondary='ws_role_task_permission',
                                                          back_populates='permissions')
    daily_event_roles: Mapped[list['WSRoleDailyEvent']] = relationship(secondary='ws_role_daily_event_permission',
                                                                       back_populates='permissions')
    many_days_event_roles: Mapped[list['WSRoleManyDaysEvent']] = relationship(
        secondary='ws_role_many_days_event_permission', back_populates='permissions')
    document_roles: Mapped[list['WSRoleDocument']] = relationship(secondary='ws_role_document_permission',
                                                                  back_populates='permissions')


class WSRoleTask(Base):
    """Роль РП - задача."""
    __tablename__ = 'ws_role_task'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('ws_role.id'))
    task_id: Mapped[int] = mapped_column(ForeignKey('ws_task.id'))
    permissions: Mapped[list[Permission]] = relationship(secondary='ws_role_task_permission',
                                                         back_populates='task_roles')


class WSRoleProject(Base):
    __tablename__ = 'ws_role_project'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('ws_role.id'))
    project_id: Mapped[int] = mapped_column(ForeignKey('project.id'))
    permissions: Mapped[list[Permission]] = relationship(secondary='ws_role_project_permission',
                                                         back_populates='project_roles')


class WSRoleDailyEvent(Base):
    __tablename__ = 'ws_role_daily_event'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('ws_role.id'))
    daily_event_id: Mapped[int] = mapped_column(ForeignKey('ws_daily_event.id'))
    permissions: Mapped[list[Permission]] = relationship(secondary='ws_role_daily_event_permission',
                                                         back_populates='daily_event_roles')


class WSRoleManyDaysEvent(Base):
    __tablename__ = 'ws_role_many_days_event'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('ws_role.id'))
    many_days_event_id: Mapped[int] = mapped_column(ForeignKey('ws_many_days_event.id'))
    permissions: Mapped[list[Permission]] = relationship(secondary='ws_role_many_days_event_permission',
                                                         back_populates='many_days_event_roles')


class WSRoleDocument(Base):
    __tablename__ = 'ws_role_document'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('ws_role.id'))
    document_id: Mapped[int] = mapped_column(ForeignKey('ws_document.id'))
    permissions: Mapped[list[Permission]] = relationship(secondary='ws_role_document_permission',
                                                         back_populates='document_roles')


ws_role_project_permission = Table(
    'ws_role_project_permission',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('role_project_id', ForeignKey('ws_role_project.id')),
    Column('permissions_id', ForeignKey('permission.id'))
)

ws_role_permission = Table(
    'ws_role_permission',
    Base.metadata,
    Column('role_id', ForeignKey('ws_role.id'), primary_key=True),
    Column('permissions_id', ForeignKey('permission.id'), primary_key=True)

)

ws_role_task_permission = Table(
    'ws_role_task_permission',
    Base.metadata,
    Column('role_task_id', ForeignKey('ws_role_task.id'), primary_key=True),
    Column('permissions_id', ForeignKey('permission.id'), primary_key=True)
)

ws_role_daily_event_permissions = Table(
    'ws_role_daily_event_permission',
    Base.metadata,
    Column('role_daily_event_id', ForeignKey('ws_role_daily_event.id'), primary_key=True),
    Column('permissions_id', ForeignKey('permission.id'), primary_key=True)
)

ws_role_many_days_event_permission = Table(
    'ws_role_many_days_event_permission',
    Base.metadata,
    Column('role_many_days_event_id', ForeignKey('ws_role_many_days_event.id'), primary_key=True),
    Column('permissions_id', ForeignKey('permission.id'), primary_key=True)
)

ws_role_document_permission = Table(
    'ws_role_document_permission',
    Base.metadata,
    Column('role_document_id', ForeignKey('ws_role_document.id'), primary_key=True),
    Column('permissions_id', ForeignKey('permission.id'), primary_key=True)

)

if __name__ == '__main__':
    pass
