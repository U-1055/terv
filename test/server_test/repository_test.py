import pytest
import sqlalchemy.orm.session
from sqlalchemy.sql import select

import datetime
import typing as tp

from server.database.repository import DataRepository, RepoInsertResponse, RepoSelectResponse
from common.base import CommonStruct, DBFields, get_datetime_now
from server.database.models.common_models import Workspace
from test.server_test.utils.test_database.base import DatabaseManager
from server.database.schemes.common_schemes import UserSchema
from test.server_test.utils.test_data.repository_test_data import test_updating_objects_data
from server.database.exceptions import BaseRepoException, DataIntegrityError, IncorrectLinkError, NotUniqueValue
from test.conftest import TEST_DB_PATH

test_database_path = 'sqlite:///utils/test_database/database'

TEST_LOGIN = 'username'
TEST_WS_NAME = 'workspace'
REPOSITORY = 'repository'
CREATING_METHOD = 'creating_method'
OBJ_DATA = 'obj_data'

params = {TEST_DB_PATH: test_database_path}


@pytest.fixture(scope='function')
def config_db(set_db_config: DatabaseManager) -> sqlalchemy.orm.session.sessionmaker:  # Устанавливает конфиг БД для теста, возвращает sessionmaker
    db_manager = set_db_config
    db_manager.set_repository_test_config(TEST_LOGIN, TEST_WS_NAME, 30)
    return db_manager.session_maker


@pytest.fixture(scope='function')
def repository(config_db) -> DataRepository:
    return DataRepository(config_db)


@pytest.fixture(scope='function')
def clear_db():
    DatabaseManager(test_database_path)  # DataBaseManager при инициализации пересоздаёт базу


@pytest.fixture(scope='function')
def user(repository) -> dict:
    return repository.get_users_by_username().content[0]


@pytest.fixture(scope='function')
def obj_id(request: pytest.FixtureRequest, repository) -> int:
    """
    Создаёт объект в БД. В тестовой функции должны быть параметры:
    creating_method - метод создания объекта, принимающий объект репозитория и коллекцию словарей с данными объектов;
    obj_data - словарь с данными объекта. Возвращает ID созданного объекта.

    """
    params = request.node.callspec.params

    creating_method: tp.Callable[[DataRepository, tp.Collection[dict]], RepoInsertResponse] = params.get(CREATING_METHOD)
    obj_data: dict = params.get(OBJ_DATA)

    response = creating_method(repository, [obj_data])
    return response.ids[0]


@pytest.mark.f_data(params)
@pytest.mark.parametrize(
    ['exp_len'],
    [[1]]
)
def test_get_workspace(repository: DataRepository, exp_len: int):
    result = repository.get_workspaces([1])

    assert len(result.content) == exp_len
    assert type(result.content[0]) is dict


@pytest.mark.f_data(params)
def test_date_format(repository: DataRepository):
    ws_tasks = repository.get_ws_tasks([])
    for task in ws_tasks.content:
        try:
            datetime.datetime.strptime(str(task.get(DBFields.created_at)), CommonStruct.datetime_format)
        except ValueError:
            assert False, (f'Datetime format of {DBFields.created_at} field of WSTask (id: {task.get(DBFields.id)})'
                           f'must be {CommonStruct.datetime_format}.')
        try:
            datetime.datetime.strptime(str(task.get(DBFields.updated_at)), CommonStruct.datetime_format)
        except ValueError:
            assert False, (f'Datetime format of {DBFields.updated_at} field of WSTask (id: {task.get(DBFields.id)})'
                           f'must be {CommonStruct.datetime_format}.')


@pytest.mark.f_data(params)
def test_serializing_links(repository: DataRepository):
    """Проверяет сериализацию связей между моделями."""
    workspace = repository.get_workspaces([1])
    users = repository.get_users_by_username()
    workspace_users = workspace.content[0].get(DBFields.users)

    assert workspace_users == [user.get(DBFields.id) for user in users.content], \
        f'All of users must be the users of workspace. Workspace: {workspace.content[0]}'


@pytest.mark.f_data(params)
def test_deserializing_links(repository: DataRepository):  
    """Проверяет десериализацию связей между моделями."""
    workspace = repository.get_workspaces([1]).content[0]
    serialized_users = workspace.get(DBFields.users)
    schema = UserSchema()

    with repository._session_maker() as session, session.begin():  # Получаем модели
        result = session.execute(select(Workspace)).scalars()
        workspaces = [ws for ws in result]
        deserialized_users_before = [schema.dump(user) for user in workspaces[0].users]  # До перезаписи

    repository.update_workspaces([workspace])  # Перезаписываем

    workspace = repository.get_workspaces([1]).content[0]
    rewritten_users = workspace.get(DBFields.users)

    with repository._session_maker() as session, session.begin():
        result = session.execute(select(Workspace)).scalars()
        workspaces = [ws for ws in result]
        deserialized_users_after = [schema.dump(user) for user in workspaces[0].users]  # После перезаписи

        assert deserialized_users_after == deserialized_users_before, (f'Deserialized users before: {deserialized_users_before}.'
                                                                       f'After: {deserialized_users_after}. Workspace: {workspace}')
    assert serialized_users == rewritten_users


@pytest.mark.f_data(params)
@pytest.mark.parametrize(
    ['name', 'description'],
    [['task', 'some_description']]
)
def test_creating_models(repository: DataRepository, name: str, description: str):
    """Проверяет создание моделей. (Конкретно: PersonalTask)."""
    user_id = 1
    task = {DBFields.name: name, DBFields.description: description, DBFields.plan_deadline: get_datetime_now(),
            DBFields.owner_id: user_id, DBFields.status_id: 1}
    request = repository.add_personal_tasks([task])
    task_id = request.ids[0]
    request = repository.get_personal_tasks_by_id([task_id])
    task = request.content[0]
    task_name, task_desc = task.get(DBFields.name), task.get(DBFields.description)
    assert isinstance(task_id, int)
    assert task_name == name
    assert task_desc == description


@pytest.mark.f_data(params)
@pytest.mark.parametrize(
    ['name', 'description'],
    [[f'task_{i}', f'description_{i}'] for i in range(10)]
)
def test_serializing_foreign_keys(repository: DataRepository, name: str, description: str):
    """Проверяет сериализацию полей с внешним ключом и соответствующих им relationship-полей."""
    user_id = 1
    task = {DBFields.name: name, DBFields.description: description, DBFields.plan_deadline: get_datetime_now(),
            DBFields.owner_id: user_id, DBFields.status_id: 1}
    request = repository.add_personal_tasks([task])
    task_id = request.ids[0]
    request = repository.get_personal_tasks_by_id([task_id])
    task = request.content[0]
    owner_id = task.get(DBFields.owner_id)
    owner = task.get(DBFields.owner)

    assert owner_id is None
    assert owner == 1


@pytest.mark.f_data(params)
@pytest.mark.parametrize(
    ['creating_method', 'updating_method', 'obj_data', 'updating_data', 'get_by_id_method', 'expected'],
    test_updating_objects_data
)
def test_updating_objects(creating_method: tp.Callable[[DataRepository, tp.Collection[dict]], RepoInsertResponse],
                          updating_method: tp.Callable[[DataRepository, tp.Collection[dict]], None], obj_id: int,
                          obj_data: dict, updating_data: dict, repository: DataRepository, expected: dict,
                          get_by_id_method: tp.Callable[[DataRepository, tp.Collection[int]], RepoSelectResponse]):
    """
    Проверка частичного обновления объектов.

    :param creating_method: Метод создания объекта (Принимает список словарей с данными объектов).
    :param updating_method: Метод обновления объекта (Принимает список словарей с обновляемыми данными).
    :param obj_data: Данные создаваемого объекта.
    :param updating_data: Обновляемые данные.
    :param repository: Репозиторий (фикстура).
    :param obj_id: Фикстура для создания объекта в базе.
    :param expected: Ожидаемый результат (обновлённый объект).
    :param get_by_id_method: Метод получения объектов по ID (Принимает список ID).

    """
    updating_data[DBFields.id] = obj_id  # Устанавливаем ID объектам
    expected[DBFields.id] = obj_id

    updating_method(repository, [updating_data])  # Обновили объект

    for field in obj_data:
        if field in updating_data:  # Обновляем данные об объекте
            obj_data[field] = updating_data[field]

    response = get_by_id_method(repository, [obj_id])  # Получаем объект
    updated_obj = response.content[0]

    for field in expected:
        assert field in updated_obj, (f'Field {field} must be in updated object, but it is not. Updated object: {updated_obj},'
                                      f'Expected: {expected}.')

    for field in updated_obj:
        if field == DBFields.updated_at or field == DBFields.created_at:  # Dump-only поля пропускаем
            continue

        assert field in expected, f'Unknown field {field} in updated object. Object: {updated_obj}. Expected: {expected}.'
        updated_field = updated_obj[field]
        expected_field = expected[field]

        if updated_field or expected_field:  # В обоих полях значение может быть None, [], () - это эквивалентно
            assert updated_obj[field] == expected[field], (f'Field {field} has different content in updated and expected objects.'
                                                           f'Updated content: {updated_obj[field]}. Expected content: {expected[field]}.'
                                                           f'Updated object: {updated_obj}. Expected object: {expected}.')
    print(updated_obj, expected)


@pytest.mark.f_data(params)
@pytest.mark.parametrize(
    ['creating_method', 'obj_data', 'expected_exc', 'expected_params'],
    [
        [
            DataRepository.add_personal_tasks,
            {
                DBFields.name: 'Name', DBFields.description: 1, DBFields.status_id: 1, DBFields.owner_id: 1,
                DBFields.plan_deadline: datetime.datetime.now()
            },
            DataIntegrityError, {'data': {DBFields.description: 'Not a valid string.'}}
        ],
        [
            DataRepository.add_personal_tasks,
            {
                DBFields.name: 'Name', DBFields.description: 'Desc', DBFields.status_id: 15, DBFields.owner_id: 91,
                DBFields.plan_deadline: datetime.datetime.now()
            },
            IncorrectLinkError, None
        ],
        [
            DataRepository.add_users,
            {
                DBFields.username: 'lo', DBFields.hashed_password: '1', DBFields.email: 'another_email'
            },
            NotUniqueValue, {'entity': 'User', 'param': DBFields.username}
        ],
        [
            DataRepository.add_users,
            {
                DBFields.username: 'lox', DBFields.hashed_password: '1', DBFields.email: 'M'
            },
            NotUniqueValue, {'entity': 'User', 'param': DBFields.email}
        ]
    ]
                         )
def test_incorrect_adding_objects(creating_method: tp.Callable[[DataRepository, tp.Sequence[dict]], int],
                                  repository: DataRepository, obj_data: dict, expected_exc: tp.Type[BaseRepoException],
                                  expected_params: dict):
    """
    Тест исключений репозитория при добавлении объектов.

    :param creating_method: Метод создания объекта, принимающий аргументы: (<объект DataRepository>,
                            <Список словарей с данными об объектах>).
    :param repository: Репозиторий (фикстура).
    :param obj_data: Данные добавляемого объекта.
    :param expected_exc: Ожидаемое исключение.
    :param expected_params: Ожидаемые значения атрибутов исключения. Словарь вида: {<название атрибута>: <значение>}.

    """

    with pytest.raises(expected_exc) as e:
        creating_method(repository, [obj_data])
    if expected_params:
        for attribute in expected_params:
            param = getattr(e.value, attribute)
            expected_param = expected_params[attribute]
            assert param == expected_param, (f'The error attribute must be equal to expected. '
                                             f'Expected value: {expected_param}. Fact value: {param}. '
                                             f'Attribute name: {attribute}')


@pytest.mark.f_data(params)
@pytest.mark.parametrize(
    ['creating_method', 'obj_data', 'expected_exc', 'expected_params', 'updating_method', 'updating_data'],
    [
        [
            DataRepository.add_personal_tasks,
            {
                DBFields.name: 'Name', DBFields.description: 'desc', DBFields.status_id: 1, DBFields.owner_id: 1,
                DBFields.plan_deadline: datetime.datetime.now()
            },
            DataIntegrityError, {'data': {DBFields.description: 'Not a valid string.'}},
            DataRepository.update_personal_tasks,
            {
                DBFields.description: 1,
            }
        ],
        [
            DataRepository.add_personal_tasks,
            {
                DBFields.name: 'Name', DBFields.description: 'Desc', DBFields.status_id: 1, DBFields.owner_id: 1,
                DBFields.plan_deadline: datetime.datetime.now()
            },
            IncorrectLinkError, None,
            DataRepository.update_personal_tasks,
            {
                DBFields.status_id: 2,
            }
        ],
        [
            DataRepository.add_users,
            {
                DBFields.username: 'user', DBFields.hashed_password: '1', DBFields.email: 'another_email'
            },
            NotUniqueValue, {'entity': 'User', 'param': DBFields.username},
            DataRepository.update_users,
            {
                DBFields.username: 'lo',
            }
        ],
        [
            DataRepository.add_users,
            {
                DBFields.username: 'lox', DBFields.hashed_password: '1', DBFields.email: 'T'
            },
            NotUniqueValue, {'entity': 'User', 'param': DBFields.email},
            DataRepository.update_users,
            {
                DBFields.email: 'M',
            }
        ]
    ]
                         )
def test_incorrect_updating_objects(obj_id: int, obj_data: dict, repository: DataRepository,
                                    creating_method: tp.Callable[[DataRepository, tp.Collection[dict]], RepoInsertResponse],
                                    updating_method: tp.Callable[[DataRepository, tp.Collection[dict]], None],
                                    updating_data: dict, expected_params: tp.Sequence[tp.Any],
                                    expected_exc: tp.Type[Exception]):
    """
    Тест исключений репозитория при обновлении объектов.

    :param obj_id: Фикстура, создающая объект по obj_data в базе и возвращающая его ID.
    :param obj_data: Данные объекта.
    :param repository: Репозиторий.
    :param updating_method: Метод обновления объекта.
    :param updating_data: Обновляемые данные. Словарь вида {<поле в таблице БД>: <значение>}.
    :param expected_params: Ожидаемые атрибуты исключения. Словарь вида {<название атрибута>: <значение>}.
    :param expected_exc: Ожидаемое исключение.

    """
    updating_data.update({DBFields.id: obj_id})

    with pytest.raises(expected_exc) as e:
        updating_method(repository, [updating_data])
    if expected_params:
        for attribute in expected_params:
            param = getattr(e.value, attribute)
            expected_param = expected_params[attribute]
            assert param == expected_param, (f'The error attribute must be equal to expected. '
                                             f'Expected value: {expected_param}. Fact value: {param}. '
                                             f'Attribute name: {attribute}')
