from sqlalchemy.orm import relationship, mapped_column, DeclarativeBase, MappedColumn, Mapped
from sqlalchemy import ForeignKey, engine, create_engine, Table, Column, Integer
from sqlalchemy.types import String
from sqlalchemy.orm.session import sessionmaker

import datetime
from abc import abstractmethod, ABC

from server.database.models.base import Base
from server.data_const import DataStruct


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String[30])
    email: Mapped[str] = mapped_column(String[30], unique=True)
    hashed_password: Mapped[str] = mapped_column(String[30])

    # РП и проекты
    created_workflows: Mapped[list['Workflow']] = relationship('Workflow', back_populates='creator')
    created_projects: Mapped[list['Project']] = relationship('Project', back_populates='creator')
    linked_workflows: Mapped[list['Workflow']] = relationship(secondary='workflow_user', back_populates='users')
    linked_projects: Mapped[list['Project']] = relationship(secondary='project_user', back_populates='users')


    # Задачи
    created_wf_tasks: Mapped[list['WFTask']] = relationship('WFTask', foreign_keys='WFTask.creator_id',
                                                            back_populates='creator')  # Созданные задачи workflow
    assigned_to_user_tasks: Mapped[list['WFTask']] = relationship(secondary='executor_task',
                                                                  back_populates='executors')  # Порученные пользователЮ
    assigned_by_user_tasks: Mapped[list['WFTask']] = relationship('WFTask', foreign_keys='WFTask.entrusted_id',
                                                                  back_populates='entrusted')  # Порученные пользователЕМ
    responsibility_tasks: Mapped[list['WFTask']] = relationship(secondary='responsible_task',
                                                                back_populates='responsible')  # Задачи, где пользователь назначен ответственным

    created_personal_tasks: Mapped[list['PersonalTask']] = relationship('PersonalTask',
                                                                      back_populates='owner')  # Личные задачи
    # Роли
    roles: Mapped[list['WFRole']] = relationship(secondary='user_wf_role', back_populates='users')

    # Документы РП
    created_wf_documents: Mapped[list['WFDocument']] = relationship('WFDocument', back_populates='creator')

    # Мероприятия
    created_wf_daily_events: Mapped[list['WFDailyEvent']] = relationship('WFDailyEvent', back_populates='creator')
    created_wf_many_days_events: Mapped[list['WFManyDaysEvent']] = relationship('WFManyDaysEvent', back_populates='creator')
    notified_daily_events: Mapped[list['WFDailyEvent']] = relationship(secondary='wf_daily_event_user',
                                                                       back_populates='notified')
    notified_many_days_events: Mapped[list['WFManyDaysEvent']] = relationship(secondary='wf_many_days_event_user',
                                                                              back_populates='notified')

    # Личные объекты
    work_directions: Mapped[list['PersonalWorkDirection']] = relationship('PersonalWorkDirection', back_populates='owner')
    personal_daily_events: Mapped[list['PersonalDailyEvent']] = relationship('PersonalDailyEvent', back_populates='owner')
    personal_many_days_events: Mapped[list['PersonalManyDaysEvent']] = relationship('PersonalManyDaysEvent', back_populates='owner')

    fields = ['id', 'username', 'email']
    one_links = []
    many_links = [
        'created_workflows', 'created_projects', 'linked_workflows', 'linked_projects', 'created_wf_tasks',
        'assigned_to_user_tasks', 'assigned_by_user_tasks', 'responsibility_tasks', 'created_personal_tasks',
        'created_wf_documents', 'created_wf_daily_events', 'created_wf_many_days_events', 'notified_daily_events',
        'notified_many_days_events', 'work_directions', 'personal_daily_events', 'personal_many_days_events'
                  ]


class Workflow(Base):
    """Рабочее пространство."""

    __tablename__ = 'workflow'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    name: Mapped[str] = mapped_column(String[30])
    description: Mapped[str] = mapped_column(String[500])

    projects: Mapped[list['Project']] = relationship('Project', back_populates='workflow')
    tasks: Mapped[list['WFTask']] = relationship('WFTask', back_populates='workflow')
    users: Mapped[list['User']] = relationship(secondary='workflow_user', back_populates='linked_workflows')
    creator: Mapped[User] = relationship(User, back_populates='created_workflows')
    work_directions: Mapped[list['WFWorkDirection']] = relationship('WFWorkDirection', back_populates='workflow')
    documents: Mapped[list['WFDocument']] = relationship('WFDocument', back_populates='workflow')
    base_categories: Mapped[list['WFBaseCategory']] = relationship('WFBaseCategory', back_populates='workflow')


class Project(Base):
    """Проект."""
    __tablename__ = 'project'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey(Workflow.id))
    creator_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    name: Mapped[str] = mapped_column(String[30])
    description: Mapped[str] = mapped_column(String[500])

    workflow: Mapped[Workflow] = relationship(Workflow, back_populates='projects')
    users: Mapped[list[User]] = relationship(secondary='project_user', back_populates='linked_projects')
    creator: Mapped[User] = relationship(User, back_populates='created_projects')


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
    Column('task_id', ForeignKey('wf_task.id'), primary_key=True)

)

responsible_task = Table(
    'responsible_task',
    Base.metadata,
    Column('user_id', ForeignKey('user.id'), primary_key=True),
    Column('task_id', ForeignKey('wf_task.id'), primary_key=True)
)

wf_daily_event_user = Table(
    'wf_daily_event_user',
    Base.metadata,
    Column('user_id', ForeignKey('user.id'), primary_key=True),
    Column('event_id', ForeignKey('wf_daily_event.id'), primary_key=True)
)

wf_many_days_event_user = Table(
    'wf_many_days_event_user',
    Base.metadata,
    Column('user_id', ForeignKey('user.id'), primary_key=True),
    Column('event_id', ForeignKey('wf_many_days_event.id'), primary_key=True)
)

workflow_user = Table(
    'workflow_user',
    Base.metadata,
    Column('workflow_id', ForeignKey('workflow.id'), primary_key=True),
    Column('user_id', ForeignKey('user.id'), primary_key=True)
)

user_role = Table(
    'user_wf_role',
    Base.metadata,
    Column('user_id', ForeignKey('user.id'), primary_key=True),
    Column('role_id', ForeignKey('wf_role.id'), primary_key=True)
)


class WFTask(Base):  # ToDo: нужно ли делить на ProjectTask и WFTask

    __tablename__ = 'wf_task'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey(Workflow.id))  # РП
    project_id: Mapped[int] = mapped_column(ForeignKey(Project.id))  # Проект
    creator_id: Mapped[int] = mapped_column(ForeignKey(User.id))  # Создатель
    entrusted_id: Mapped[int] = mapped_column(ForeignKey(User.id))  # Поручивший
    work_direction_id: Mapped[int] = mapped_column(ForeignKey('wf_work_direction.id'))  # Направление работы
    parent_task_id: Mapped[int] = mapped_column(ForeignKey('wf_task.id'))  # Родительская задача

    name: Mapped[str] = mapped_column(String[30])
    description: Mapped[str] = mapped_column(String[1000])
    plan_deadline: Mapped[datetime.datetime] = mapped_column(nullable=False)
    fact_deadline: Mapped[datetime.datetime] = mapped_column()
    plan_time: Mapped[datetime.datetime] = mapped_column()
    fact_time: Mapped[datetime.datetime] = mapped_column()
    plan_start_work_date: Mapped[datetime.datetime] = mapped_column()
    fact_start_work_date: Mapped[datetime.datetime] = mapped_column()

    responsible: Mapped[list[User]] = relationship(secondary='responsible_task', back_populates='responsibility_tasks')
    executors: Mapped[list[User]] = relationship(secondary='executor_task', back_populates='assigned_to_user_tasks')
    creator: Mapped[User] = relationship(User, foreign_keys='WFTask.creator_id', back_populates='created_wf_tasks')
    entrusted: Mapped[User] = relationship(User, foreign_keys='WFTask.entrusted_id', back_populates='assigned_by_user_tasks')
    workflow: Mapped[Workflow] = relationship(Workflow, back_populates='tasks')
    work_direction: Mapped[Workflow] = relationship('WFWorkDirection', back_populates='tasks')
    parent_task: Mapped['WFTask'] = relationship('WFTask', back_populates='child_tasks', remote_side='WFTask.id')
    child_tasks: Mapped[list['WFTask']] = relationship('WFTask', back_populates='parent_task')


class PersonalTask(Base):
    """Личная задача"""
    __tablename__ = 'personal_task'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    work_direction_id: Mapped[int] = mapped_column(ForeignKey('personal_work_direction.id'))

    name: Mapped[str] = mapped_column(String[30])
    description: Mapped[str] = mapped_column(String[1000])
    plan_deadline: Mapped[datetime.datetime] = mapped_column(nullable=False)
    fact_deadline: Mapped[datetime.datetime] = mapped_column()
    plan_time: Mapped[datetime.datetime] = mapped_column()
    fact_time: Mapped[datetime.datetime] = mapped_column()
    plan_start_work_date: Mapped[datetime.datetime] = mapped_column()
    fact_start_work_date: Mapped[datetime.datetime] = mapped_column()

    owner: Mapped[User] = relationship(User, back_populates='created_personal_tasks')
    work_direction: Mapped['PersonalWorkDirection'] = relationship('PersonalWorkDirection', back_populates='tasks')


class WFWorkDirection(Base):
    """Направление работы РП"""
    __tablename__ = 'wf_work_direction'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey('workflow.id'))
    name: Mapped[str] = mapped_column(String[30])

    workflow: Mapped[Workflow] = relationship(Workflow, back_populates='work_directions')
    tasks: Mapped[list[WFTask]] = relationship(WFTask, back_populates='work_direction')


class PersonalWorkDirection(Base):
    """Личное направление работы"""
    __tablename__ = 'personal_work_direction'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    name: Mapped[str] = mapped_column(String[30])

    owner: Mapped[Workflow] = relationship(User, back_populates='work_directions')
    tasks: Mapped[list[WFTask]] = relationship(PersonalTask, back_populates='work_direction')


class PersonalDailyEvent(Base):
    """Личное однодневное мероприятие."""
    __tablename__ = 'personal_daily_event'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('user.id'))

    name: Mapped[str] = mapped_column(String[30])
    description: Mapped[str] = mapped_column(String[500])
    date: Mapped[datetime.date] = mapped_column()
    time_start: Mapped[datetime.time] = mapped_column()
    time_end: Mapped[datetime.time] = mapped_column()

    owner: Mapped[User] = relationship(User, back_populates='personal_daily_events')


class PersonalManyDaysEvent(Base):
    """Личное многодневное мероприятие."""
    __tablename__ = 'personal_many_days_event'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    name: Mapped[str] = mapped_column(String[30])
    description: Mapped[str] = mapped_column(String[500])
    datetime_start: Mapped[datetime.datetime] = mapped_column()
    datetime_end: Mapped[datetime.datetime] = mapped_column()

    owner: Mapped[User] = relationship(User, back_populates='personal_many_days_events')


class WFDailyEvent(Base):
    """Однодневное мероприятие РП."""
    __tablename__ = 'wf_daily_event'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey('workflow.id'))
    creator_id: Mapped[int] = mapped_column(ForeignKey('user.id'))

    name: Mapped[str] = mapped_column(String[30])
    description: Mapped[str] = mapped_column(String[500])
    date: Mapped[datetime.date] = mapped_column()
    time_start: Mapped[datetime.time] = mapped_column()
    time_end: Mapped[datetime.time] = mapped_column()

    creator: Mapped[User] = relationship(User, back_populates='created_wf_daily_events')
    notified: Mapped[list['User']] = relationship(secondary='wf_daily_event_user', back_populates='notified_daily_events')  # Оповещаемые пользователи


class WFManyDaysEvent(Base):
    """Многодневное мероприятие РП."""
    __tablename__ = 'wf_many_days_event'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey('workflow.id'))
    creator_id: Mapped[int] = mapped_column(ForeignKey('user.id'))

    name: Mapped[str] = mapped_column(String[30])
    description: Mapped[str] = mapped_column(String[500])
    datetime_start: Mapped[datetime.datetime] = mapped_column()
    datetime_end: Mapped[datetime.datetime] = mapped_column()

    creator: Mapped[User] = relationship(User, back_populates='created_wf_many_days_events')
    notified: Mapped[list['User']] = relationship(secondary='wf_many_days_event_user', back_populates='notified_many_days_events')  # Оповещаемые пользователи


class WFBaseCategory(Base):
    """Раздел базы РП."""
    __tablename__ = 'wf_base_category'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey('workflow.id'))
    parent_category_id: Mapped[int] = mapped_column(ForeignKey('wf_base_category.id'))
    name: Mapped[str] = mapped_column(String[30])
    description: Mapped[str] = mapped_column(String[250])

    parent_category: Mapped['WFBaseCategory'] = relationship('WFBaseCategory', back_populates='child_categories', remote_side='WFBaseCategory.id')
    child_categories: Mapped['WFBaseCategory'] = relationship('WFBaseCategory', back_populates='parent_category')
    workflow: Mapped[Workflow] = relationship(Workflow, back_populates='base_categories')
    documents: Mapped[list['WFDocument']] = relationship('WFDocument', back_populates='base_category')


class WFDocument(Base):
    """
    Документ базы РП.
    В key-value базе /database/data/data под id документа хранится его контент.
    """
    __tablename__ = 'wf_document'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey('workflow.id'))
    creator_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    base_category_id: Mapped[WFBaseCategory] = mapped_column(ForeignKey('wf_base_category.id'))

    workflow: Mapped[Workflow] = relationship(Workflow, back_populates='documents')
    creator: Mapped[User] = relationship(User, back_populates='created_wf_documents')
    base_category: Mapped[WFBaseCategory] = relationship(WFBaseCategory, back_populates='documents')


if __name__ == '__main__':
    pass
