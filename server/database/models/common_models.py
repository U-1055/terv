from sqlalchemy.orm import relationship, mapped_column, DeclarativeBase, MappedColumn, Mapped
from sqlalchemy import ForeignKey, engine, create_engine, Table, Column, Integer
from sqlalchemy.types import String
from sqlalchemy.orm.session import sessionmaker

from server.data_const import DataStruct

import datetime
from abc import abstractmethod, ABC


class Base(DeclarativeBase):
    pass


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
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', ForeignKey('user.id')),
    Column('project_id', ForeignKey('project.id'))
)

executor_task = Table(
    'executor_task',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('executor_id', ForeignKey('user.id')),
    Column('task_id', ForeignKey('wf_task.id'))

)

responsible_task = Table(
    'responsible_task',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', ForeignKey('user.id')),
    Column('task_id', ForeignKey('wf_task.id'))
)

wf_daily_event_user = Table(
    'wf_daily_event_user',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', ForeignKey('user.id')),
    Column('event_id', ForeignKey('wf_daily_event.id'))
)

wf_many_days_event_user = Table(
    'wf_many_days_event_user',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', ForeignKey('user.id')),
    Column('event_id', ForeignKey('wf_many_days_event.id'))
)

workflow_user = Table(
    'workflow_user',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('workflow_id', ForeignKey('workflow.id')),
    Column('user_id', ForeignKey('user.id'))
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


    @property
    def plan_deadline_(self):
        return self.plan_deadline

    @plan_deadline_.setter
    def set_plan_deadline(self, plan_deadline: datetime.datetime):
        self.plan_deadline = datetime.datetime.isoformat(DataStruct.time_format, plan_deadline)

    @property
    def fact_deadline_(self):
        return self.fact_deadline

    def serialize(self):
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'project_id': self.project_id,
            'creator_id': self.creator_id,
            'entrusted_id': self.entrusted_id,
            'work_direction_id': self.work_direction_id,
            'parent_task_id': self.parent_task_id,

            'executors': [executor.id for executor in self.executors],
            'responsible': [responsible.id for responsible in self.responsible],
            'child_tasks': [task.id for task in self.child_tasks],

            'name': self.name,
            'description': self.description,
            'plan_deadline': self.plan_deadline,
            'fact_deadline': self.fact_deadline,
            'plan_time': self.plan_time,
            'fact_time': self.fact_time,
            'plan_start_work_date': self.plan_start_work_date,
            'fact_start_work_date': self.fact_start_work_date
        }


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


if __name__ == '__main__':
    engine = create_engine('sqlite:///')
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)
    with session() as s, s.begin():
        s.add(User(username='username', email='str', hashed_password=''))
        s.add(Workflow(creator_id=0, name='Workflow', description='description'))
        workflow = Workflow(creator_id=0, name='Workflow', description='description')
        for i in range(150):
            user = User(username=f'username#{i}', email=f'str[{i}]', hashed_password='')
            user.linked_workflows.append(workflow)
            s.add(user)
