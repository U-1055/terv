import pytest
import sqlalchemy.orm.session
from sqlalchemy.sql import select

import datetime

from server.database.repository import DataRepository
from common.base import CommonStruct, DBFields, get_datetime_now
from server.database.models.common_models import Workflow, User
from test.server_test.utils.test_database.base import DatabaseManager
from server.database.schemes.common_schemes import UserSchema

test_database_path = 'sqlite:///utils/test_database/database'

TEST_LOGIN = 'username'
TEST_WF_NAME = 'workflow'


@pytest.fixture(scope='session')
def config_db() -> sqlalchemy.orm.session.sessionmaker:  # Устанавливает конфиг БД для теста, возвращает sessionmaker
    db_manager = DatabaseManager(test_database_path)
    db_manager.set_repository_test_config(TEST_LOGIN, TEST_WF_NAME, 15)
    return db_manager.session_maker


@pytest.fixture(scope='function')
def repository(config_db) -> DataRepository:
    return DataRepository(config_db)


@pytest.fixture(scope='function')
def user(repository) -> dict:
    return repository.get_users_by_username().content[0]


@pytest.mark.parametrize(
    ['exp_len'],
    [[1]]
)
def test_get_workflow(repository: DataRepository, exp_len: int):
    result = repository.get_workflows([1])

    assert len(result.content) == exp_len
    assert type(result.content[0]) == dict


def test_date_format(repository: DataRepository):
    wf_tasks = repository.get_wf_tasks_by_id()
    for task in wf_tasks.content:
        try:
            datetime.datetime.strptime(str(task.get(DBFields.created_at)), CommonStruct.datetime_format)
        except ValueError:
            assert False, (f'Datetime format of {DBFields.created_at} field of WFTask (id: {task.get(DBFields.id)})'
                           f'must be {CommonStruct.datetime_format}.')
        try:
            datetime.datetime.strptime(str(task.get(DBFields.updated_at)), CommonStruct.datetime_format)
        except ValueError:
            assert False, (f'Datetime format of {DBFields.updated_at} field of WFTask (id: {task.get(DBFields.id)})'
                           f'must be {CommonStruct.datetime_format}.')


def test_serializing_links(repository: DataRepository):
    """Проверяет сериализацию связей между моделями."""
    workflow = repository.get_workflows([1])
    users = repository.get_users_by_username()
    workflow_users = workflow.content[0].get(DBFields.users)

    assert workflow_users == [user.get(DBFields.id) for user in users.content], \
        f'All of users must be the users of workflow. Workflow: {workflow.content[0]}'


def test_deserializing_links(repository: DataRepository):
    """Проверяет десериализацию связей между моделями."""
    workflow = repository.get_workflows([1]).content[0]
    serialized_users = workflow.get(DBFields.users)
    schema = UserSchema()

    with repository._session_maker() as session, session.begin():  # Получаем модели
        result = session.execute(select(Workflow)).scalars()
        workflows = [wf for wf in result]
        deserialized_users_before = [schema.dump(user) for user in workflows[0].users]  # До перезаписи

    repository.update_workflows([workflow])  # Перезаписываем

    workflow = repository.get_workflows([1]).content[0]
    rewritten_users = workflow.get(DBFields.users)

    with repository._session_maker() as session, session.begin():
        result = session.execute(select(Workflow)).scalars()
        workflows = [wf for wf in result]
        deserialized_users_after = [schema.dump(user) for user in workflows[0].users]  # После перезаписи

        assert deserialized_users_after == deserialized_users_before, (f'Deserialized users before: {deserialized_users_before}.'
                                                                       f'After: {deserialized_users_after}. Workflow: {workflow}')
    assert serialized_users == rewritten_users


@pytest.mark.parametrize(
    ['name', 'description'],
    [['task', 'some_description']]
)
def test_creating_personal_tasks(repository: DataRepository, name: str, description: str, user: dict):
    """Проверяет создание моделей. (Конкретно: PersonalTask)."""
    task = {DBFields.name: name, DBFields.description: description, DBFields.plan_deadline: get_datetime_now(), DBFields.owner: user}
    request = repository.add_personal_tasks([task])
    task_id = request.ids[0]
    request = repository.get_personal_tasks_by_id([task_id])
    task = request.content[0]
    task_name, task_desc = task.get(DBFields.name), task.get(DBFields.description)
    assert isinstance(task_id, int)
    assert task_name == name
    assert task_desc == description


