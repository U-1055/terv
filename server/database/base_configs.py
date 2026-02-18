from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql import select

import datetime

from server.auth.auth_module import hash_password
import server.database.models.common_models as cm
import server.database.models.roles as roles


def set_db_config_1(engine: Engine,
                    personal_tasks_params: tuple[tuple[str, str], ...] = None,
                    workspace_name: str = 'Workspace',
                    workspace_tasks_params: tuple[tuple[str, str], ...] = None,
                    personal_daily_events_params: tuple[
                        tuple[str, str, datetime.time, datetime.time], ...] = None,
                    personal_many_days_events_params: tuple[tuple[str, str, datetime.date, datetime.date], ...] = None,
                    wf_daily_events_params: tuple[tuple[str, str, datetime.time, datetime.time], ...] = None,
                    wf_many_days_events_params: tuple[tuple[str, str, datetime.date, datetime.date], ...] = None
                    ):
    """
    Устанавливает конфиг БД. По умолчанию - три пользователя, 1 РП, 10 личных задач, 10 задач РП, 10 личных однодневных
    мероприятий, 10 личных многодневных мероприятий, 10 однодневных мероприятий РП, 10 многодневных мероприятий РП.
    Логин пользователя, которому принадлежат личные объекты (и который участвует в объектах РП): Terv. Пароль: x41822jnk_.
    :param engine: Движок для подключения к БД.
    :param personal_tasks_params: Параметры личных задач вида: ((<name>, <description>), ...).
    :param workspace_name: Название РП.
    :param workspace_tasks_params: Параметры задач РП вида: ((<name>, <description>), ...).
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
        user_1 = cm.User(username='Terv_', hashed_password=hash_password('x41822jnk_'), email='sth@someemail.terv')
        user_2 = cm.User(username='User1', hashed_password='a_234567890', email='emaiL1@email')
        wf_creator = cm.User(username='User_', hashed_password='a_234567890', email='email@email')
        session.add(user_1)
        session.add(user_2)
        session.add(wf_creator)

        if personal_tasks_params:
            personal_tasks = [
                cm.PersonalTask(owner=user_1, name=params[0], description=params[1], plan_deadline=datetime.date.today())
                for params in personal_tasks_params]
        else:
            personal_tasks = [
                cm.PersonalTask(owner=user_1, name=f'personal_task.{i}', plan_deadline=datetime.date.today(),
                                description=''.join(['Description ' for i in range(50)])) for i in range(10)]
        session.add_all(personal_tasks)

        workspace = cm.Workspace(creator=wf_creator, users=[wf_creator, user_2, user_1], name=workspace_name)
        session.add(workspace)

        if workspace_tasks_params:
            workspace_tasks = [cm.WFTask(name=params[0], description=params[1], workspace=workspace, creator=wf_creator,
                                        entrusted=wf_creator, executors=[user_1, user_2], plan_deadline=datetime.date.today())
                              for params in workspace_tasks_params]
        else:
            workspace_tasks = [
                cm.WFTask(name=f'wf_task.{i}', description='Description', creator=wf_creator, entrusted=wf_creator,
                          executors=[user_1, user_2], workspace=workspace, plan_deadline=datetime.date.today())
                for i in range(10)]
        session.add_all(workspace_tasks)

        today = datetime.date.today()
        datetime_now = datetime.datetime.now()
        time_now = datetime.datetime.now().time()
        if personal_daily_events_params:
            personal_daily_events = [cm.PersonalDailyEvent(name=params[0], description=params[1], time_start=params[2],
                                                           time_end=params[3], date=today, owner=user_1)
                                     for params in personal_daily_events_params]
        else:
            personal_daily_events = [cm.PersonalDailyEvent(name=f'personal_daily_event.{i}', description='Description',
                                                           time_start=datetime.time(hour=i, minute=time_now.minute),
                                                           time_end=datetime.time(hour=i + 1, minute=time_now.minute),
                                                           date=today, owner=user_1)
                                     for i in range(10)]
        session.add_all(personal_daily_events)

        if wf_daily_events_params:
            wf_daily_events = [cm.WFDailyEvent(name=params[0], description=params[1], time_start=params[2], workspace=workspace,
                                               time_end=params[3], date=today, creator=wf_creator, notified=[user_1, user_2])
                               for params in wf_daily_events_params]
        else:
            wf_daily_events = [cm.WFDailyEvent(name=f'wf_daily_event.{i}', description='Description',
                                               time_start=datetime.time(hour=i + 10, minute=time_now.minute),
                                               time_end=datetime.time(hour=i + 11, minute=time_now.minute),
                                               date=today, workspace=workspace, creator=wf_creator, notified=[user_1, user_2])
                               for i in range(10)]
        session.add_all(wf_daily_events)

        last_day = datetime_now - datetime.timedelta(days=1)
        next_day = datetime_now + datetime.timedelta(days=1)

        if personal_many_days_events_params:
            personal_many_days_events = [cm.PersonalManyDaysEvent(
                name=params[0], description=params[1], owner=user_1,
                datetime_start=datetime.datetime(year=params[2].year, month=params[2].month, day=params[2].day),
                datetime_end=datetime.datetime(year=params[3].year, month=params[3].month, day=params[3].day))
                                         for params in personal_many_days_events_params]
        else:
            personal_many_days_events = [cm.PersonalManyDaysEvent(
                name=f'personal_many_days_event.{i}', description='Description',
                datetime_start=last_day, owner=user_1,
                datetime_end=next_day,)
                                         for i in range(10)]

        session.add_all(personal_many_days_events)

        if wf_many_days_events_params:
            wf_many_days_events = [cm.WFManyDaysEvent(
                name=params[0], description=params[1], workspace=workspace, creator=wf_creator, notified=[user_1, user_2],
                datetime_start=datetime.datetime(year=params[2].year, month=params[2].month, day=params[2].day),
                datetime_end=datetime.datetime(year=params[3].year, month=params[3].month, day=params[3].day))
                                         for params in wf_many_days_events_params]
        else:
            wf_many_days_events = [cm.WFManyDaysEvent(
                name=f'wf_many_days_event.{i}', description='Description', workspace=workspace, creator=wf_creator,
                notified=[user_1, user_2], datetime_start=last_day, datetime_end=next_day)
                                         for i in range(10)]

        session.add_all(wf_many_days_events)


if __name__ == '__main__':
    from server.database.models.db_utils import init_db
    from server.database.repository import DataRepository

    init_db('sqlite:///database')
    engine = create_engine('sqlite:///database')
    set_db_config_1(engine=engine, personal_tasks_params=(('Сделать презентацию', 'Титульный слайд - переделать; доработать вывод'),
                                                          ('Переписать тесты', 'В тесте аутентификации устаревшие фиктивные объекты'),
                                                          ('Согласовать требования', 'К Т.В. - по проекту.'),
                                                          ('Изучить модуль "Напряжённость"', "Из курса по электростатике"),
                                                          ('Изучить модуль "Потенциал"', ''),
                                                          ('Изучить модуль "Уравнение адиабаты"', 'МКТ'),
                                                          ('Решить 10 иррациональных неравенств', 'Из сборника Ларина'),
                                                          ('Решить 10 З-17', ''),
                                                          ('Рассмотреть З-19', ''),
                                                          ('Изучить раздел №2 книги по БД', 'Реляционные БД в примерах')
                                                          ),
                    workspace_tasks_params=(('Реализовать утилиту для замера памяти' , ''),
                                            ('Реализовать утилиту для запросов', ''),
                                            ('Настроить стиль GUI', ''),
                                            ('Отладить настройки', ''),
                                            ('Составить ПМИ', 'По ГОСТ'),
                                            ('Описать автотесты', 'В ПМИ - доработать'),
                                            ('Сделать тестовый конфиг', 'По ПМИ'),
                                            ('Провести испытания производительности', 'По ПМИ'),
                                            ('Записать видео функционального теста', ''),
                                            ('Изучить документацию nginx', '')
                    ),
                    personal_daily_events_params=(('Проект', "...", datetime.time(9, 00), datetime.time(12, 00)),
                                                  ('Физика', 'Разбор хитрых задач с Сириус-курса', datetime.time(12, 30), datetime.time(14, 30)),
                                                  ('Матеша', 'Неравенства из книжки', datetime.time(14, 45), datetime.time(16, 45))),
                    wf_daily_events_params=(('Созвон', 'Согласовать требования с начальством', datetime.time(17, 00), datetime.time(18, 00)),
                                            ('Проект', 'Доработка документации', datetime.time(18, 45), datetime.time(20, 15))),
                    personal_many_days_events_params=(('Разбор физики', 'Закрыть модули курса по электростатике',
                                                       datetime.date(2026, 2, 14), datetime.date(2026, 2, 20)), ),

                    wf_many_days_events_params=(('Окончательная доработка проекта', 'Оформить результаты', datetime.date(2026, 2, 14), datetime.date(2026, 2, 20)
                                                     ), ))


    repo = DataRepository(sessionmaker(bind=engine))
    print(repo.get_wf_daily_events_by_id())


