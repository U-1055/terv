from pydantic import Field, BaseModel

import datetime
from abc import abstractmethod, ABC
import typing as tp

from client.models.base import Base


class User(Base):
    __tablename__ = 'user'

    id: int
    username: str = Field(max_length=30)
    email: str = Field(max_length=60)

    # РП и проекты
    created_workspaces: list[int]
    created_projects: list[int] 
    linked_workspaces: list[int] 

    # Задачи
    created_ws_tasks: list[int]  # Созданные задачи workspace
    assigned_to_user_tasks: list[int]  # Порученные пользователЮ
    assigned_by_user_tasks: list[int]  # Порученные пользователЕМ
    responsibility_tasks: list[int]  # Задачи, где пользователь назначен ответственным

    created_personal_tasks: list[int] | None  # Личные задачи
    # Роли
    roles: list[int] | None

    # Документы РП
    created_ws_documents: list[int] | None

    # Мероприятия
    created_ws_daily_events: list[int] | None
    created_ws_many_days_events: list[int] | None
    notified_daily_events: list[int] | None
    notified_many_days_events: list[int] | None

    # Личные объекты
    work_directions: list[int] | None
    personal_daily_events: list[int] | None
    personal_many_days_events: list[int] | None


class Workspace(Base):
    """Рабочее пространство."""

    __tablename__ = 'workspace'

    id: int
    creator_id: int | None
    name: str = Field(max_length=60)
    description: str = Field(max_length=2000)

    creator: int
    projects: list[int]
    tasks: list[int]
    users: list[int]
    work_directions: list[int]
    documents: list[int]
    base_categories: list[int]


class Project(Base):
    """Проект."""
    __tablename__ = 'project'
    id: int 
    workspace_id: int | None
    creator_id: int | None
    name: str = Field(max_length=60)
    description: str = Field(max_length=2000)


class WSTask(Base):

    __tablename__ = 'ws_task'
    id: int
    workspace_id: int | None = None  # РП
    project_id: int | None = None  # Проект
    creator_id: int | None = None  # Создатель
    entrusted_id: int | None = None  # Поручивший
    work_direction_id: int | None = None  # Направление работы
    parent_task_id: int | None = None  # Родительская задача

    name: str = Field(max_length=60)
    description: str = Field(max_length=2000)
    plan_deadline: datetime.datetime
    fact_deadline: datetime.datetime | None
    plan_time: datetime.datetime | None
    fact_time: datetime.datetime | None
    plan_start_work_date: datetime.datetime | None
    fact_start_work_date: datetime.datetime | None

    creator: int
    project: int | None = None
    workspace: int
    work_direction: int | None = None
    parent_task: int | None = None

    responsible: list[int]
    executors: list[int]
    child_tasks: list[int]


class PersonalTask(Base):
    """Личная задача"""
    __tablename__ = 'personal_task'
    id: int
    owner_id: int | None = None
    work_direction_id: int | None  = None

    name: str = Field(max_length=60)
    description: str = Field(max_length=2000)
    owner: int
    plan_deadline: datetime.datetime
    fact_deadline: datetime.datetime | None
    plan_time: datetime.datetime | None
    fact_time: datetime.datetime | None
    plan_start_work_date: datetime.datetime | None
    fact_start_work_date: datetime.datetime | None


class WSWorkDirection(Base):
    """Направление работы РП"""
    __tablename__ = 'ws_work_direction'

    id: int
    workspace_id: int | None = None
    name: str = Field(max_length=30)

    workspace: int
    tasks: list[int]


class PersonalWorkDirection(Base):
    """Личное направление работы"""
    __tablename__ = 'personal_work_direction'

    id: int
    owner_id: int | None = None
    name: str = Field(max_length=60)

    owner: int
    tasks: list[int]


class PersonalDailyEvent(Base):
    """Личное однодневное мероприятие."""
    __tablename__ = 'personal_daily_event'

    id: int
    owner_id: int | None = None

    name: str = Field(max_length=60)
    description: str = Field(max_length=2000)
    owner: int
    date: datetime.date
    time_start: datetime.time
    time_end: datetime.time


class PersonalManyDaysEvent(Base):
    """Личное многодневное мероприятие."""
    __tablename__ = 'personal_many_days_event'

    id: int
    owner_id: int | None = None
    name: str = Field(max_length=60)
    description: str = Field(max_length=2000)
    datetime_start: datetime.datetime
    datetime_end: datetime.datetime

    owner: int


class WSDailyEvent(Base):
    """Однодневное мероприятие РП."""
    __tablename__ = 'ws_daily_event'

    id: int
    workspace_id: int | None = None  # ToDo: переделать модели клиента
    creator_id: int | None = None

    name: str = Field(max_length=60)
    description: str = Field(max_length=2000)
    date: datetime.date
    time_start: datetime.time
    time_end: datetime.time

    creator: int
    workspace: int
    notified: list[int]  # Оповещаемые пользователи


class WSManyDaysEvent(Base):
    """Многодневное мероприятие РП."""
    __tablename__ = 'ws_many_days_event'

    id: int
    workspace_id: int | None = None
    creator_id: int | None = None

    name: str = Field(max_length=60)
    description: str = Field(max_length=2000)
    datetime_start: datetime.datetime
    datetime_end: datetime.datetime

    creator: int
    workspace: int
    notified: list[int] # Оповещаемые пользователи


class WSBaseCategory(Base):
    """Раздел базы РП."""
    __tablename__ = 'ws_base_category'

    id: int
    workspace_id: int | None
    parent_category_id: int | None
    name: str = Field(max_length=60)
    description: str = Field(max_length=2000)

    child_categories: list[int]
    documents: list[int]


class WSDocument(Base):
    """
    Документ базы РП.
    В key-value базе /database/data/data под id документа хранится его контент.
    """
    __tablename__ = 'ws_document'

    id: int
    workspace_id: int | None
    creator_id: int | None
    base_category_id: int | None


if __name__ == '__main__':
    pass
