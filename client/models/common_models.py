from pydantic import Field, BaseModel

import datetime
from abc import abstractmethod, ABC
import typing as tp

from client.models.base import Base


class User(Base):
    __tablename__ = 'user'

    id: int
    username: str = Field(max_length=30)
    email: str = Field(max_length=30)

    # РП и проекты
    created_workflows: list[int]
    created_projects: list[int] 
    linked_workflows: list[int] 

    # Задачи
    created_wf_tasks: list[int]  # Созданные задачи workflow
    assigned_to_user_tasks: list[int]  # Порученные пользователЮ
    assigned_by_user_tasks: list[int]  # Порученные пользователЕМ
    responsibility_tasks: list[int]  # Задачи, где пользователь назначен ответственным

    created_personal_tasks: list[int] | None # Личные задачи
    # Роли
    roles: list[int] | None

    # Документы РП
    created_wf_documents: list[int] | None

    # Мероприятия
    created_wf_daily_events: list[int] | None
    created_wf_many_days_events: list[int] | None
    notified_daily_events: list[int] | None
    notified_many_days_events: list[int] | None

    # Личные объекты
    work_directions: list[int] | None
    personal_daily_events: list[int] | None
    personal_many_days_events: list[int] | None

    one_links: tp.ClassVar = []
    many_links: tp.ClassVar = [
        'created_workflows', 'created_projects', 'linked_workflows', 'linked_projects', 'created_wf_tasks',
        'assigned_to_user_tasks', 'assigned_by_user_tasks', 'responsibility_tasks', 'created_personal_tasks',
        'created_wf_documents', 'created_wf_daily_events', 'created_wf_many_days_events', 'notified_daily_events',
        'notified_many_days_events', 'work_directions', 'personal_daily_events', 'personal_many_days_events'
                  ]


class Workflow(Base):
    """Рабочее пространство."""

    __tablename__ = 'workflow'

    id: int
    creator_id: int 
    name: str = Field(max_length=30)
    description: str = Field(max_length=2000)

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
    workflow_id: int
    creator_id: int
    name: str = Field(max_length=30) 
    description: str = Field(max_length=2000)


class WFTask(Base):

    __tablename__ = 'wf_task'
    id: int
    workflow_id: int  # РП
    project_id: int  # Проект
    creator_id: int # Создатель
    entrusted_id: int  # Поручивший
    work_direction_id: int  # Направление работы
    parent_task_id: int  # Родительская задача

    name: str = Field(max_length=30) 
    description: str = Field(max_length=2000)
    plan_deadline: datetime.datetime
    fact_deadline: datetime.datetime
    plan_time: datetime.datetime
    fact_time: datetime.datetime
    plan_start_work_date: datetime.datetime
    fact_start_work_date: datetime.datetime

    responsible: list[int]
    executors: list[int]
    child_tasks: list[int]


class PersonalTask(Base):
    """Личная задача"""
    __tablename__ = 'personal_task'
    id: int
    owner_id: int
    work_direction_id: int

    name: str = Field(max_length=30)
    description: str = Field(max_length=2000)
    plan_deadline: datetime.datetime
    fact_deadline: datetime.datetime
    plan_time: datetime.datetime
    fact_time: datetime.datetime
    plan_start_work_date: datetime.datetime
    fact_start_work_date: datetime.datetime


class WFWorkDirection(Base):
    """Направление работы РП"""
    __tablename__ = 'wf_work_direction'

    id: int
    workflow_id: int
    name: str = Field(max_length=30)

    tasks: list[int]


class PersonalWorkDirection(Base):
    """Личное направление работы"""
    __tablename__ = 'personal_work_direction'

    id: int
    owner_id: int
    name: str = Field(max_length=30)

    owner: int
    tasks: list[int]


class PersonalDailyEvent(Base):
    """Личное однодневное мероприятие."""
    __tablename__ = 'personal_daily_event'

    id: int
    owner_id: int

    name: str = Field(max_length=30)
    description: str = Field(max_length=2000)
    date: datetime.date
    time_start: datetime.time
    time_end: datetime.time


class PersonalManyDaysEvent(Base):
    """Личное многодневное мероприятие."""
    __tablename__ = 'personal_many_days_event'

    id: int
    owner_id: int
    name: str = Field(max_length=30)
    description: str = Field(max_length=2000)
    datetime_start: datetime.datetime
    datetime_end: datetime.datetime


class WFDailyEvent(Base):
    """Однодневное мероприятие РП."""
    __tablename__ = 'wf_daily_event'

    id: int
    workflow_id: int 
    creator_id: int 

    name: str = Field(max_length=30)
    description: str = Field(max_length=2000)
    date: datetime.date
    time_start: datetime.time
    time_end: datetime.time

    notified: list[int]  # Оповещаемые пользователи


class WFManyDaysEvent(Base):
    """Многодневное мероприятие РП."""
    __tablename__ = 'wf_many_days_event'

    id: int
    workflow_id: int
    creator_id: int

    name: str = Field(max_length=30)
    description: str = Field(max_length=2000)
    datetime_start: datetime.datetime
    datetime_end: datetime.datetime

    notified: list[int] # Оповещаемые пользователи


class WFBaseCategory(Base):
    """Раздел базы РП."""
    __tablename__ = 'wf_base_category'

    id: int
    workflow_id: int
    parent_category_id: int
    name: str = Field(max_length=30)
    description: str = Field(max_length=2000)

    child_categories: list[int]
    documents: list[int]


class WFDocument(Base):
    """
    Документ базы РП.
    В key-value базе /database/data/data под id документа хранится его контент.
    """
    __tablename__ = 'wf_document'

    id: int
    workflow_id: int
    creator_id: int
    base_category_id: int


if __name__ == '__main__':
    pass
