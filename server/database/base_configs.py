from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm.session import sessionmaker

import datetime

from server.auth.auth_module import hash_password
import server.database.models.common_models as cm
import server.database.models.roles as roles


def set_db_config_1(engine: Engine,
                    personal_tasks_params: tuple[tuple[str, str], ...] = None,
                    workflow_name: str = 'Workflow',
                    workflow_tasks_params: tuple[tuple[str, str], ...] = None,
                    personal_daily_events_params: tuple[
                        tuple[str, str, datetime.datetime, datetime.datetime], ...] = None,
                    personal_many_days_events_params: tuple[tuple[str, str, datetime.date, datetime.date], ...] = None,
                    wf_daily_events_params: tuple[tuple[str, str, datetime.datetime, datetime.datetime], ...] = None,
                    wf_many_days_events_params: tuple[tuple[str, str, datetime.date, datetime.date], ...] = None
                    ):
    """
    Устанавливает конфиг БД. По умолчанию - два пользователя, 1 РП, 10 личных задач, 10 задач РП, 10 личных однодневных
    мероприятий, 10 личных многодневных мероприятий, 10 однодневных мероприятий РП, 10 многодневных мероприятий РП.
    Логин пользователя, которому принадлежат личные объекты (и который участвует в объектах РП): User. Пароль:x41822n_.
    :param engine: Движок для подключения к БД.
    :param personal_tasks_params: Параметры личных задач вида: ((<name>, <description>), ...).
    :param workflow_name: Название РП.
    :param workflow_tasks_params: Параметры задач РП вида: ((<name>, <description>), ...).
    :param personal_daily_events_params: Параметры личных однодневных мероприятий вида:
                                         ((<name>, <description>, <время начала>, <время окончания>), ...)
    :param personal_many_days_events_params: Параметры личных многодневных мероприятий вида:
                                             ((<name>, <description>, <дата начала>, <дата окончания>)).
    :param wf_daily_events_params: Параметры однодневных мероприятий РП вида:
                                   ((<name>, <description>, <время начала>, <время окончания>), ...)
    :param wf_many_days_events_params: Параметры многодневных мероприятий РП вида:
                                       ((<name>, <description>, <дата начала>, <дата окончания>)).

    """

    session_maker = sessionmaker(bind=engine)
    with session_maker() as session, session.begin():
        user = cm.User(username='User', hashed_password=hash_password('x41822n_'), email='something@email.sth')
        wf_creator = cm.User(username='Creator', hashed_password='password', email='email_1')
        session.add(user)
        session.add(wf_creator)

        if personal_tasks_params:
            personal_tasks = [
                cm.PersonalTask(owner=user, name=params[0], description=params[1], plan_deadline=datetime.date.today())
                for params in personal_tasks_params]
        else:
            personal_tasks = [
                cm.PersonalTask(owner=user, name=f'personal_task.{i}', plan_deadline=datetime.date.today(),
                                description=''.join(['Description ' for i in range(50)])) for i in range(10)]
        session.add_all(personal_tasks)

        workflow = cm.Workflow(creator=wf_creator, users=[wf_creator], name=workflow_name)
        session.add(workflow)

        if workflow_tasks_params:
            workflow_tasks = [cm.WFTask(name=params[0], description=params[1], workflow=workflow, creator=wf_creator,
                                        entrusted=wf_creator, executors=[user], plan_deadline=datetime.date.today())
                              for params in workflow_tasks_params]
        else:
            workflow_tasks = [
                cm.WFTask(name=f'wf_task.{i}', description='Description', creator=wf_creator, entrusted=wf_creator,
                          executors=[user], workflow=workflow, plan_deadline=datetime.date.today())
                for i in range(10)]
        session.add_all(workflow_tasks)

        today = datetime.date.today()
        datetime_now = datetime.datetime.now()
        time_now = datetime.datetime.now().time()
        if personal_daily_events_params:
            personal_daily_events = [cm.PersonalDailyEvent(name=params[0], description=params[1], time_start=params[2],
                                                           time_end=params[3], date=today, owner=user)
                                     for params in personal_daily_events_params]
        else:
            personal_daily_events = [cm.PersonalDailyEvent(name=f'personal_daily_event.{i}', description='Description',
                                                           time_start=datetime.time(hour=i, minute=time_now.minute),
                                                           time_end=datetime.time(hour=i + 1, minute=time_now.minute),
                                                           date=today, owner=user)
                                     for i in range(10)]
        session.add_all(personal_daily_events)

        if wf_daily_events_params:
            wf_daily_events = [cm.WFDailyEvent(name=params[0], description=params[1], time_start=params[2], workflow=workflow,
                                               time_end=params[3], date=today, creator=wf_creator, notified=[user])
                               for params in personal_daily_events_params]
        else:
            wf_daily_events = [cm.WFDailyEvent(name=f'wf_daily_event.{i}', description='Description',
                                               time_start=datetime.time(hour=i, minute=time_now.minute),
                                               time_end=datetime.time(hour=i + 1, minute=time_now.minute),
                                               date=today, workflow=workflow, creator=wf_creator)
                               for i in range(10)]
        session.add_all(wf_daily_events)

        last_day = datetime_now - datetime.timedelta(days=1)
        next_day = datetime_now + datetime.timedelta(days=1)

        if personal_many_days_events_params:
            personal_many_days_events = [cm.PersonalManyDaysEvent(
                name=params[0], description=params[1], owner=user,
                datetime_start=datetime.datetime(year=params[2].year, month=params[2].month, day=params[2].day),
                datetime_end=datetime.datetime(year=params[3].year, month=params[3].month, day=params[3].day))
                                         for params in personal_many_days_events_params]
        else:
            personal_many_days_events = [cm.PersonalManyDaysEvent(
                name=f'personal_many_days_event.{i}', description='Description',
                datetime_start=last_day, owner=user,
                datetime_end=next_day,)
                                         for i in range(10)]

        session.add_all(personal_many_days_events)

        if personal_many_days_events_params:
            wf_many_days_events = [cm.WFManyDaysEvent(
                name=params[0], description=params[1], workflow=workflow, creator=wf_creator, notified=[user],
                datetime_start=datetime.datetime(year=params[2].year, month=params[2].month, day=params[2].day),
                datetime_end=datetime.datetime(year=params[3].year, month=params[3].month, day=params[3].day))
                                         for params in personal_many_days_events_params]
        else:
            wf_many_days_events = [cm.WFManyDaysEvent(
                name=f'wf_many_days_event.{i}', description='Description', workflow=workflow, creator=wf_creator,
                notified=[user], datetime_start=last_day, datetime_end=next_day)
                                         for i in range(10)]

        session.add_all(wf_many_days_events)


if __name__ == '__main__':
    engine = create_engine('sqlite:///database')
    set_db_config_1(engine=engine)


