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

test_database_path = 'sqlite:///utils/test_database/database'

TEST_LOGIN = 'username'
TEST_ws_NAME = 'workspace'
REPOSITORY = 'repository'
CREATING_METHOD = 'creating_method'
OBJ_DATA = 'obj_data'


@pytest.fixture(scope='session')
def config_db() -> sqlalchemy.orm.session.sessionmaker:  # Устанавливает конфиг БД для теста, возвращает sessionmaker
    db_manager = DatabaseManager(test_database_path)
    db_manager.set_repository_test_config(TEST_LOGIN, TEST_ws_NAME, 30)
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


@pytest.mark.parametrize(
    ['exp_len'],
    [[1]]
)
def test_get_workspace(repository: DataRepository, exp_len: int):
    result = repository.get_workspaces([1])

    assert len(result.content) == exp_len
    assert type(result.content[0]) == dict


def test_date_format(repository: DataRepository):
    ws_tasks = repository.get_ws_tasks_by_id()
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


def test_serializing_links(repository: DataRepository):
    """Проверяет сериализацию связей между моделями."""
    workspace = repository.get_workspaces([1])
    users = repository.get_users_by_username()
    workspace_users = workspace.content[0].get(DBFields.users)

    assert workspace_users == [user.get(DBFields.id) for user in users.content], \
        f'All of users must be the users of workspace. Workspace: {workspace.content[0]}'


def test_deserializing_links(repository: DataRepository):  # ToDo: расширить тесты сериализации
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


@pytest.mark.parametrize(
    ['name', 'description'],
    [['task', 'some_description']]
)
def test_creating_models(repository: DataRepository, name: str, description: str):
    """Проверяет создание моделей. (Конкретно: PersonalTask)."""
    user_id = 1
    task = {DBFields.name: name, DBFields.description: description, DBFields.plan_deadline: get_datetime_now(),
            DBFields.owner_id: user_id, DBFields.status_id: 0}
    request = repository.add_personal_tasks([task])
    task_id = request.ids[0]
    request = repository.get_personal_tasks_by_id([task_id])
    task = request.content[0]
    task_name, task_desc = task.get(DBFields.name), task.get(DBFields.description)
    assert isinstance(task_id, int)
    assert task_name == name
    assert task_desc == description


@pytest.mark.parametrize(
    ['name', 'description'],
    [[f'task_{i}', f'description_{i}'] for i in range(10)]
)
def test_serializing_foreign_keys(repository: DataRepository, name: str, description: str):
    """Проверяет сериализацию полей с внешним ключом и соответствующих им relationship-полей."""
    user_id = 1
    task = {DBFields.name: name, DBFields.description: description, DBFields.plan_deadline: get_datetime_now(),
            DBFields.owner_id: user_id, DBFields.status_id: 0}
    request = repository.add_personal_tasks([task])
    task_id = request.ids[0]
    request = repository.get_personal_tasks_by_id([task_id])
    task = request.content[0]
    owner_id = task.get(DBFields.owner_id)
    owner = task.get(DBFields.owner)

    assert owner_id is None
    assert owner == 1


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

