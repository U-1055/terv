from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Table, Column, Integer, String

from server.database.models.base import Base
import typing as tp
from pydantic import Field

import server.database.models.common_models as db


class WSRole(Base):
    """Роль рабочего пространства."""
    __tablename__ = 'ws_role'

    id: int
    workspace_id: int | None
    name: str = Field(max_length=30)
    color: str = Field(max_length=30)

    permissions: list[int]
    users: list[int]


class Permission(Base):
    """Разрешение (доступ)"""
    __tablename__ = 'permission'

    id: int = mapped_column(primary_key=True, autoincrement=True)
    type: str = Field(max_length=30)

    roles: list[int]
    project_roles: list[int]
    task_roles: list[int]
    daily_event_roles: list[int]
    many_days_event_roles: list[int]
    document_roles: list[int]


class WSRoleTask(Base):
    """Роль РП - задача."""
    __tablename__ = 'ws_role_task'

    id: int = mapped_column(primary_key=True, autoincrement=True)
    role_id: int = mapped_column(ForeignKey('ws_role.id'))
    task_id: int = mapped_column(ForeignKey('ws_task.id'))
    permissions: list[int]


class WSRoleProject(Base):
    __tablename__ = 'ws_role_project'

    id: int = mapped_column(primary_key=True, autoincrement=True)
    role_id: int = mapped_column(ForeignKey('ws_role.id'))
    project_id: int = mapped_column(ForeignKey('project.id'))
    permissions: list[int]


class WSRoleDailyEvent(Base):
    __tablename__ = 'ws_role_daily_event'

    id: int = mapped_column(primary_key=True, autoincrement=True)
    role_id: int = mapped_column(ForeignKey('ws_role.id'))
    daily_event_id: int = mapped_column(ForeignKey('ws_daily_event.id'))
    permissions: list[int]


class WSRoleManyDaysEvent(Base):
    __tablename__ = 'ws_role_many_days_event'

    id: int = mapped_column(primary_key=True, autoincrement=True)
    role_id: int = mapped_column(ForeignKey('ws_role.id'))
    many_days_event_id: int = mapped_column(ForeignKey('ws_many_days_event.id'))
    permissions: list[int]


class WSRoleDocument(Base):
    __tablename__ = 'ws_role_document'

    id: int = mapped_column(primary_key=True, autoincrement=True)
    role_id: int = mapped_column(ForeignKey('ws_role.id'))
    document_id: int = mapped_column(ForeignKey('ws_document.id'))
    permissions: list[int]

