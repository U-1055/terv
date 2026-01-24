import pytest
import sqlalchemy.orm.session

from pathlib import Path

from server.services.services import WorkflowService
from server.database.repository import DataRepository
from test.server_test.utils.test_database.base import DatabaseManager
from common.base import DBFields
import server.services.errors as err


def string(len_: int = 30) -> str:
    return ''.join(['.' for i in range(len_)])


@pytest.fixture(scope='session')
def config_db() -> sqlalchemy.orm.session.sessionmaker:
    db_manager = DatabaseManager('sqlite:///utils/test_database/database')
    db_manager.set_workflow_service_test_config(20)
    return db_manager.session_maker


@pytest.fixture(scope='function')
def repository(config_db):
    return DataRepository(config_db)


@pytest.fixture(scope='function')
def workflow_id(repository) -> int:
    return WorkflowService.create({DBFields.name: 'wf_2'}, 2, repository)


@pytest.fixture(scope='function')
def workflow_with_users_id(repository, workflow_id: int) -> tuple[int, tuple[int, ...]]:
    WorkflowService.add_users((1, 2, 3, 4, 5), workflow_id, repository)
    return workflow_id, (1, 2, 3, 4, 5)


@pytest.mark.parametrize(
    ['name', 'description', 'creator_id'],
    [['wf_2', 'desc', 1], ['wf_3', 'desc', 2], ['wf_4', 'desc', 3], ['wf_3', 'desc', 4], ['wf_5', 'desc', 6]]
)
def test_creating_normal_workflow(repository: DataRepository, name: str, description: str, creator_id: int):
    workflow = {DBFields.name: name, DBFields.description: description}
    wf_id = WorkflowService.create(workflow, creator_id, repository)
    db_workflow = repository.get_workflows([wf_id]).content[0]  # Проверка установки связей
    db_wf_name = db_workflow.get(DBFields.name)
    db_wf_description = db_workflow.get(DBFields.description)
    db_users = db_workflow.get(DBFields.users)

    assert name == db_wf_name
    assert description == db_wf_description
    assert db_users == [creator_id]


@pytest.mark.parametrize(
    ['name', 'description', 'creator_id'],
    [[string(31), string(25), 2], [string(30), string(1002), 2], [string(31), string(1002), 5]]
)
def test_creating_not_normal_workflow(repository: DataRepository, name: str, description: str, creator_id: int):
    workflow = {DBFields.name: name, DBFields.description: description}
    with pytest.raises(err.IncorrectParamError) as e:
        WorkflowService.create(workflow, creator_id, repository)
        assert e.param == 'workflow'


@pytest.mark.parametrize(
    ['user_ids'],
    [[(2, 3, 4, 5, 6, 7, 8)]]
)
def test_normal_adding_users(repository: DataRepository, workflow_id: int, user_ids: tuple[int, ...]):
    WorkflowService.add_users(user_ids, workflow_id, repository)
    response = repository.get_workflows([workflow_id]).content
    workflow = response[0]
    workflow_users = workflow.get(DBFields.users)
    users = repository.get_users_by_id(user_ids).content

    assert list(workflow_users) == list(user_ids), workflow.get(DBFields.users)
    for user in users:
        linked_workflows = user.get(DBFields.linked_workflows)
        assert workflow_id in linked_workflows


def test_normal_deleting_users(workflow_with_users_id: tuple[int, tuple[int, ...]],  # ToDo: проверка удаления пользователя из роли
                               repository: DataRepository):
    workflow_id = workflow_with_users_id[0]
    user_ids = workflow_with_users_id[1]
    WorkflowService.delete_users(workflow_id, user_ids, repository)

    workflow = repository.get_workflows([workflow_id]).content[0]
    workflow_users = workflow.get(DBFields.users)
    users = repository.get_users_by_id(user_ids).content
    linked_workflow = [user.get(DBFields.linked_workflows) for user in users]
    assert all([user not in users for user in workflow_users])
    assert workflow_id not in linked_workflow


