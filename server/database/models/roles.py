from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Table, Column, Integer, String

from server.database.models.base import Base
import typing as tp

import server.database.models.common_models as db


class WFRole(Base):
    """Роль рабочего пространства."""
    __tablename__ = 'wf_role'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey('workflow.id'))
    name: Mapped[str] = mapped_column(String[30])
    color: Mapped[str] = mapped_column(String[30])

    permissions: Mapped[list['Permission']] = relationship(secondary='wf_role_permission', back_populates='roles')
    users: Mapped[list[db.User]] = relationship(secondary='user_wf_role', back_populates='roles')


class Permission(Base):
    """Разрешение (доступ)"""
    __tablename__ = 'permission'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String[30], unique=True)  # Тип разрешения (CRUD-<Объект>)

    roles: Mapped[list[WFRole]] = relationship(secondary='wf_role_permission', back_populates='permissions')
    project_roles: Mapped[list['WFRoleProject']] = relationship(secondary='wf_role_project_permission', back_populates='permissions')
    task_roles: Mapped[list['WFRoleTask']] = relationship(secondary='wf_role_task_permission', back_populates='permissions')
    daily_event_roles: Mapped[list['WFRoleDailyEvent']] = relationship(secondary='wf_role_daily_event_permission', back_populates='permissions')
    many_days_event_roles: Mapped[list['WFRoleManyDaysEvent']] = relationship(secondary='wf_role_many_days_event_permission', back_populates='permissions')
    document_roles: Mapped[list['WFRoleDocument']] = relationship(secondary='wf_role_document_permission', back_populates='permissions')


class WFRoleTask(Base):
    """Роль РП - задача."""
    __tablename__ = 'wf_role_task'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('wf_role.id'))
    task_id: Mapped[int] = mapped_column(ForeignKey('wf_task.id'))
    permissions: Mapped[list[Permission]] = relationship(secondary='wf_role_task_permission',
                                                         back_populates='task_roles')


class WFRoleProject(Base):
    __tablename__ = 'wf_role_project'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('wf_role.id'))
    project_id: Mapped[int] = mapped_column(ForeignKey('project.id'))
    permissions: Mapped[list[Permission]] = relationship(secondary='wf_role_project_permission', back_populates='project_roles')


class WFRoleDailyEvent(Base):
    __tablename__ = 'wf_role_daily_event'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('wf_role.id'))
    daily_event_id: Mapped[int] = mapped_column(ForeignKey('wf_daily_event.id'))
    permissions: Mapped[list[Permission]] = relationship(secondary='wf_role_daily_event_permission', back_populates='daily_event_roles')


class WFRoleManyDaysEvent(Base):
    __tablename__ = 'wf_role_many_days_event'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('wf_role.id'))
    many_days_event_id: Mapped[int] = mapped_column(ForeignKey('wf_many_days_event.id'))
    permissions: Mapped[list[Permission]] = relationship(secondary='wf_role_many_days_event_permission', back_populates='many_days_event_roles')


class WFRoleDocument(Base):
    __tablename__ = 'wf_role_document'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('wf_role.id'))
    document_id: Mapped[int] = mapped_column(ForeignKey('wf_document.id'))
    permissions: Mapped[list[Permission]] = relationship(secondary='wf_role_document_permission',
                                                         back_populates='document_roles')


wf_role_project_permission = Table(
    'wf_role_project_permission',
    db.Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('role_project_id', ForeignKey('wf_role_project.id')),
    Column('permissions_id', ForeignKey('permission.id'))
)

wf_role_permission = Table(
    'wf_role_permission',
    db.Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('role_id', ForeignKey('wf_role.id')),
    Column('permissions_id', ForeignKey('permission.id'))

)

wf_role_task_permission = Table(
    'wf_role_task_permission',
    db.Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('role_task_id', ForeignKey('wf_role_task.id')),
    Column('permissions_id', ForeignKey('permission.id'))
)

wf_role_daily_event_permissions = Table(
    'wf_role_daily_event_permission',
    db.Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('role_daily_event_id', ForeignKey('wf_role_daily_event.id')),
    Column('permissions_id', ForeignKey('permission.id'))
)

wf_role_many_days_event_permission = Table(
    'wf_role_many_days_event_permission',
    db.Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('role_many_days_event_id', ForeignKey('wf_role_many_days_event.id')),
    Column('permissions_id', ForeignKey('permission.id'))
)


wf_role_document_permission = Table(
    'wf_role_document_permission',
    db.Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('role_document_id', ForeignKey('wf_role_document.id')),
    Column('permissions_id', ForeignKey('permission.id'))

)
