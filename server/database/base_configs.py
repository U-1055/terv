import random

from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql import select

import datetime
from faker import Faker

from server.auth.auth_module import hash_password
from common.base import WorkStages, TasksStatuses
import server.database.models.common_models as cm
from server.data_const import Roles


fake = Faker()


def set_db_config_1(engine: Engine,
                    workspace_name: str = 'Инженерная смена будущего',
                    ):
    """
    Устанавливает конфиг БД для тестирования функционала проектов.
    Создаёт:
    - 1 Workspace
    - 7 проектов этого Workspace
    - 51 пользователя:
      - 1 Администратор
      - 10 Наставников
      - 10 Тимлидов
      - 30 Участников (Студентов)
    - Каждый проект получает группу из 5 участников: 1 Наставник, 1 Тимлид, 3 Участника
    - В каждом проекте создаётся несколько задач с разными статусами
    - В каждом проекте создаётся 6 этапов работы

    :param engine: Движок для подключения к БД.
    :param workspace_name: Название РП.
    """

    session_maker = sessionmaker(bind=engine)
    with session_maker() as session, session.begin():
        # Создание администратора
        admin_user = cm.User(username='Моисеенко Е.С.', hashed_password=hash_password('x41822jnk_'), email='mes@donso.su')
        session.add(admin_user)

        # Создание 10 наставников
        mentors = []
        mentors_names = ['А.В.Иванов', 'С.П.Петров', 'М.К.Сидоров', 'Д.Н.Кузнецов', 'Е.Р.Смирнов',
                         'В.Л.Васильев', 'Н.Т.Попов', 'И.О.Соколов', 'А.А.Михайлов', 'П.З.Новиков']
        for i in range(10):
            mentor = cm.User(username=mentors_names[i], hashed_password=hash_password('password123'),
                           email=f'mentor{i+1}@terv.com')
            mentors.append(mentor)
            session.add(mentor)

        # Создание 10 тимлидов
        teamleads = []
        teamleads_names = ['К.Д.Федоров', 'Ю.Г.Морозов', 'Л.В.Волков', 'А.С.Алексеев', 'Е.М.Лебедев',
                           'С.А.Семенов', 'О.И.Егоров', 'Т.Б.Павлов', 'Н.Р.Козлов', 'М.П.Степанов']
        for i in range(10):
            teamlead = cm.User(username=teamleads_names[i], hashed_password=hash_password('password123'),
                              email=f'teamlead{i+1}@terv.com')
            teamleads.append(teamlead)
            session.add(teamlead)

        # Создание 30 студентов
        students_names = [
            'Б.А.Андреев', 'В.Б.Баранов', 'Г.В.Гришин', 'Д.Г.Дмитриев', 'Е.Д.Ефимов',
            'Ж.Е.Жуков', 'З.Ж.Захаров', 'И.З.Ильин', 'К.И.Калинин', 'Л.К.Лазарев',
            'М.Л.Макаров', 'Н.М.Нестеров', 'О.Н.Орлов', 'П.О.Поляков', 'Р.П.Романов',
            'С.Р.Савельев', 'Т.С.Тихонов', 'У.Т.Ульянов', 'Ф.У.Фролов', 'Х.Ф.Харитонов',
            'Ц.Х.Цветков', 'Ч.Ц.Чернов', 'Ш.Ч.Шестаков', 'Щ.Ш.Щербаков', 'Э.Щ.Яшин',
            'Ю.Э.Юрлов', 'Я.Ю.Яковлев', 'А.Я.Авдеев', 'Б.А.Беляков', 'В.Б.Богданов'
        ]
        students = []
        for i in range(30):
            student = cm.User(username=students_names[i], hashed_password=hash_password('password123'),
                             email=f'student{i+1}@terv.com')
            students.append(student)
            session.add(student)

        session.flush()  # Получаем ID всех пользователей

        # Создание Workspace с пользователями
        all_users = [admin_user] + mentors + teamleads + students
        workspace = cm.Workspace(creator=admin_user, name=workspace_name, users=all_users, description='РЦ "Альтаир"')
        session.add(workspace)
        session.flush()  # Получаем ID workspace

        # Создание ролей пользователей
        mentor_role = cm.WSRole(name=Roles.mentor.value, workspace=workspace, users=mentors)
        student_role = cm.WSRole(name=Roles.student.value, workspace=workspace, users=students)
        teamlead_role = cm.WSRole(name=Roles.team_lead.value, workspace=workspace, users=teamleads)
        admin_role = cm.WSRole(name=Roles.admin.value, workspace=workspace, users=[admin_user])

        session.add_all([mentor_role, student_role, teamlead_role, admin_role])

        # Создание статусов задач
        default_task_status = cm.WSTaskStatus(name=TasksStatuses.planned_name.value, workspace=workspace)
        session.add(default_task_status)
        in_work_status = cm.WSTaskStatus(name=TasksStatuses.in_work_name.value, workspace=workspace)
        session.add(in_work_status)
        review_status = cm.WSTaskStatus(name=TasksStatuses.on_check.value, workspace=workspace)
        session.add(review_status)
        completed_status = cm.WSTaskStatus(name=TasksStatuses.completed_name.value, workspace=workspace)
        session.add(completed_status)
        to_rework_status = cm.WSTaskStatus(name=TasksStatuses.to_rework.value, workspace=workspace)
        session.add(to_rework_status)
        session.flush()

        workspace.default_task_status_id = default_task_status.id
        workspace.completed_task_status_id = completed_status.id

        task_templates = [
            ('Разработать концепцию устройства и подобрать датчики', ''),
            ('Спроектировать корпус в CAD-системе', ''),
            ('Написать прошивку микроконтроллера для опроса датчиков', ''),
            ('Реализовать беспроводную передачу данных о заполненности на сервер', ''),
            ('Создать простой веб-дашборд для мониторинга состояния контейнеров', ''),
            ('Подготовить презентацию и демонстрационный прототип', ''),
            ('Изучить требования к поливу для выбранных культур', ''),
            ('Разработать алгоритм полива на основе влажности почвы и прогноза погоды', ''),
            ('Собрать макет системы с датчиками и исполнительными механизмами', ''),
            ('Написать управляющую программу на Python (Raspberry Pi)', ''),
            ('Реализовать удалённый мониторинг и управление через веб-интерфейс', ''),
            ('Провести тестирование системы на реальных растениях', ''),
            ('Разработать схему базы данных зданий и аудиторий', ''),
            ('Реализовать поиск и прокладку маршрута между корпусами', ''),
            ('Создать прототип мобильного приложения с картой (Flutter/Kotlin)', ''),
            ('Интегрировать расписание занятий из внешнего API', ''),
            ('Добавить функцию голосового ввода пункта назначения', ''),
            ('Подготовить демо-версию для презентации', ''),
            ('Провести анализ потребностей и сценариев общения', ''),
            ('Спроектировать диалоговую архитектуру на основе деревьев решений', ''),
            ('Написать серверную часть бота на Python (aiogram)', ''),
            ('Интегрировать базу знаний со статьями и советами', ''),
            ('Обучить простую NLP-модель для определения тональности сообщений', ''),
            ('Провести тестирование с фокус-группой и доработать сценарии', ''),
            ('Подготовить итоговый отчёт и презентацию', ''),
            ('Изучить нормативные требования и технику безопасности', ''),
            ('Собрать раму и подобрать силовую установку для дрона', ''),
            ('Настроить полётный контроллер и GPS-модуль', ''),
            ('Написать программу автоматического патрулирования по маршруту', ''),
            ('Реализовать передачу видео с бортовой камеры на наземную станцию', ''),
            ('Разработать алгоритм детектирования дыма на изображениях', ''),
            ('Выбрать 3 лабораторные работы для реализации', ''),
            ('Разработать 3D-модели экспериментальных установок (Unity/Blender)', ''),
            ('Создать интерактивные симуляции физических процессов', ''),
            ('Реализовать систему сбора и отображения «измеренных» данных', ''),
            ('Интегрировать лабораторию в веб-приложение (WebGL)', ''),
            ('Подготовить методические указания для учеников и учителей', ''),
            ('Провести пилотное тестирование с группой школьников', ''),
            ('Спроектировать архитектуру системы и выбрать оборудование (камеры, шлагбаум)', ''),
            ('Реализовать алгоритм распознавания автомобильных номеров (OpenCV + нейросеть)', ''),
            ('Создать базу данных для хранения событий въезда/выезда', ''),
            ('Разработать REST API для интеграции с мобильным приложением', ''),
            ('Собрать демо-стенд с веб-камерой и макетом шлагбаума', ''),
            ('Провести нагрузочное тестирование системы при большом потоке машин', ''),
        ]

        # Этапы работы (одинаковые для всех проектов)
        work_stages_data = [
            (WorkStages.idea_generating_name.value, 'На этом этапе вам следует найти проблему, определить целевую аудиторию,'
                                                    ' решить в общем виде '
                                                    'вопросы об анализе проблемной области (какие исследования вам потребуются,'
                                                    'кого вы будете опрашивать, требуется ли экспертиза и какая), '
                                                    'выдвинуть ряд гипотез, которые вы будете проверять при анализе '
                                                    'проблемной области.'),
            (WorkStages.thesis_proofing_name.value, 'На этом этапе вам нужно проанализировать проблемную область: '
                                                    'найти литературу, провести глубинные интервью и опросы. На их '
                                                    'основе нужно сделать вывод по каждой из гипотез, выдвинутых на '
                                                    'предыдущем этапе - верна она, или нет. Результатом этого этапа '
                                                    'должна стать точно определённая проблема проекта, его актуальность, '
                                                    'цель и задачи.'),
            (WorkStages.solution_projecting_name.value, 'На этом этапе вам нужно спланировать разработку решения: '
                                                        'определите функциональную архитектуру и концепцию (как именно '
                                                        'разработка будет решать проблему, как она будет выглядеть), '
                                                        'спроектировать архитектуру, составить технические требования к '
                                                        'разрабатываемому решению.'),
            (WorkStages.development_name.value, 'На этом этапе вам предстоит разработать ваше решение и проверить его '
                                                'соответствие техническим требованиям.'),
            (WorkStages.testing_name.value, 'На этом этапе вам нужно представить своё решение целевой аудитории и получить '
                                            'обратную связь (возможно, путём опросов и глубинных интервью). Если '
                                            'обратная связь положительная - постарайтесь внедрить ваше решение '
                                            'для использования целевой аудиторией. Соберите обратную связь по внедрению '
                                            'и сделайте выводы.'),
            (WorkStages.results_preparation_name.value, 'На этом этапе нужно оформить результаты: описать, что и как вы делали,'
                                                        'почему именно так, а не иначе, что в итоге получилось и что '
                                                        'будете делать дальше.'),
        ]

        # Создание 7 проектов
        projects_data = [
            ('Умный контейнер для раздельного сбора отходов',
             'Разработка IoT-устройства для умного сбора и мониторинга отходов'),
            ('Система автоматического полива для школьной теплицы',
             'Автоматизация полива на основе данных датчиков и прогноза погоды'),
            ('Мобильный помощник для навигации по кампусу',
             'Приложение для построения маршрутов и интеграции с расписанием'),
            ('Чат-бот для психологической поддержки школьников',
             'Диалоговая система поддержки на базе NLP и деревьев решений'),
            ('Беспилотный летательный аппарат для мониторинга лесных пожаров',
             'Дрон с системой видеонаблюдения и детекции дыма'),
            ('Виртуальная лаборатория по физике для дистанционного обучения',
             '3D-симуляции физических лабораторных работ в браузере'),
            ('Умная парковка с автоматическим распознаванием номеров',
             'Система учёта въезда/выезда с распознаванием номеров'),
        ]
        projects = ['']
        for i in range(7):
            project_name, project_description = projects_data[i]

            # Выбираем участников проекта (1 наставник, 1 тимлид, 3 студента)
            mentor_idx = i % len(mentors)
            teamlead_idx = i % len(teamleads)
            student_start = i * 3
            student_end = student_start + 3

            project_mentor = mentors[mentor_idx]
            project_teamlead = teamleads[teamlead_idx]
            project_students = students[student_start:student_end]

            project = cm.Project(
                name=project_name,
                description=project_description,
                workspace=workspace,
                creator=admin_user,
                mentors=[project_mentor],
                users=[project_teamlead] + project_students
            )
            projects.append(project)
            session.add(project)
            session.flush()  # Получаем ID проекта

            # Создаём этапы для проекта
            date_start = datetime.date.today() + datetime.timedelta(days=i * 10)
            stages = []
            for stage_idx, (stage_name, result_desc) in enumerate(work_stages_data):
                stage = cm.WorkStage(
                    name=stage_name,
                    result=result_desc,
                    project_id=project.id,
                    date_start=date_start + datetime.timedelta(days=stage_idx * 7),
                    date_end=date_start + datetime.timedelta(days=(stage_idx + 1) * 7),
                    is_finished=stage_idx < i % 3,  # Первые 2 этапа завершены
                    is_future=stage_idx >= i % 3 + 1,   # Последние 2 этапа будущие
                    is_current=stage_idx == i % 3
                )
                session.add(stage)
                stages.append(stage)

            # Установка текущего этапа проекта (3-й этап - Проектирование решения)
            project.current_stage = stages[i % 3]
            session.add(project)

            # Создание задач для проекта (3-5 задач с разными статусами)
            num_tasks = 3 + (i % 3)  # 3, 4 или 5 задач
            status_ids = [default_task_status.id, in_work_status.id, review_status.id, completed_status.id, to_rework_status.id]

            for task_idx in range(num_tasks):
                template_idx = (i * 3 + task_idx) % len(task_templates)
                task_name, task_description = task_templates[template_idx]

                # Выбираем статус циклично
                status_id = status_ids[(task_idx + i) % len(status_ids)]

                # Выбираем исполнителя из студентов проекта
                executor = project_students[task_idx % len(project_students)]

                task = cm.WSTask(
                    name=f'{task_name}',
                    description=task_description,
                    project=project,
                    workspace=workspace,
                    creator=admin_user,
                    entrusted=admin_user,
                    executor=executor,
                    plan_deadline=datetime.date.today() + datetime.timedelta(days=7 * (task_idx + 1)),
                    plan_start_work_date=datetime.date.today() + datetime.timedelta(days=random.randint(1, 4)),
                    status_id=status_id
                )
                session.add(task)

        session.commit()

    with session_maker() as session, session.begin():
        pass


if __name__ == '__main__':
    from server.database.models.db_utils import init_db

    init_db('sqlite:///database')
    engine = create_engine('sqlite:///database')
    set_db_config_1(engine=engine)

    print('Test configuration applied successfully')
    print('Users: 51 (1 Admin, 10 Mentors, 10 Team Leads, 30 Students)')
    print('Projects: 7')
    print('Tasks per project: 3-5')
    print('Work stages per project: 6')



