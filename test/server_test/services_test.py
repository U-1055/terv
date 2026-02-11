import pytest
import sqlalchemy.orm.session

from pathlib import Path

from server.services.services import WorkspaceService
from server.database.repository import DataRepository
from test.server_test.utils.test_database.base import DatabaseManager
from common.base import DBFields
import server.services.errors as err


def string(len_: int = 30) -> str:
    return ''.join(['.' for i in range(len_)])


@pytest.fixture(scope='session')
def config_db() -> sqlalchemy.orm.session.sessionmaker:
    db_manager = DatabaseManager('sqlite:///utils/test_database/database')
    db_manager.set_workspace_service_test_config(20)
    return db_manager.session_maker


@pytest.fixture(scope='function')
def repository(config_db):
    return DataRepository(config_db)


@pytest.fixture(scope='function')
def workspace_id(repository) -> int:
    return WorkspaceService.create({DBFields.name: 'wf_2'}, 2, repository)


@pytest.fixture(scope='function')
def workspace_with_users_id(repository, workspace_id: int) -> tuple[int, tuple[int, ...]]:
    WorkspaceService.add_users((1, 2, 3, 4, 5), workspace_id, repository)
    return workspace_id, (1, 2, 3, 4, 5)


@pytest.mark.parametrize(
    ['name', 'description', 'creator_id'],
    [['wf_2', 'desc', 1], ['wf_3', 'desc', 2], ['wf_4', 'desc', 3], ['wf_3', 'desc', 4], ['wf_5', 'desc', 6]]
)
def test_creating_normal_workspace(repository: DataRepository, name: str, description: str, creator_id: int):
    workspace = {DBFields.name: name, DBFields.description: description}
    wf_id = WorkspaceService.create(workspace, creator_id, repository)
    db_workspace = repository.get_workspaces([wf_id]).content[0]  # Проверка установки связей
    db_wf_name = db_workspace.get(DBFields.name)
    db_wf_description = db_workspace.get(DBFields.description)
    db_users = db_workspace.get(DBFields.users)

    assert name == db_wf_name
    assert description == db_wf_description
    assert db_users == [creator_id]


@pytest.mark.parametrize(
    ['name', 'description', 'creator_id'],
    [[string(31), string(25), 2], [string(30), string(1002), 2], [string(31), string(1002), 5]]
)
def test_creating_not_normal_workspace(repository: DataRepository, name: str, description: str, creator_id: int):
    workspace = {DBFields.name: name, DBFields.description: description}
    with pytest.raises(err.IncorrectParamError) as e:
        WorkspaceService.create(workspace, creator_id, repository)
        assert e.param == 'workspace'


@pytest.mark.parametrize(
    ['user_ids'],
    [[(2, 3, 4, 5, 6, 7, 8)]]
)
def test_normal_adding_users(repository: DataRepository, workspace_id: int, user_ids: tuple[int, ...]):
    WorkspaceService.add_users(user_ids, workspace_id, repository)
    response = repository.get_workspaces([workspace_id]).content
    workspace = response[0]
    workspace_users = workspace.get(DBFields.users)
    users = repository.get_users_by_id(user_ids).content

    assert list(workspace_users) == list(user_ids), workspace.get(DBFields.users)
    for user in users:
        linked_workspaces = user.get(DBFields.linked_workspaces)
        assert workspace_id in linked_workspaces


def test_normal_deleting_users(workspace_with_users_id: tuple[int, tuple[int, ...]],  # ToDo: проверка удаления пользователя из роли
                               repository: DataRepository):
    workspace_id = workspace_with_users_id[0]
    user_ids = workspace_with_users_id[1]
    WorkspaceService.delete_users(workspace_id, user_ids, repository)

    workspace = repository.get_workspaces([workspace_id]).content[0]
    workspace_users = workspace.get(DBFields.users)
    users = repository.get_users_by_id(user_ids).content
    linked_workspace = [user.get(DBFields.linked_workspaces) for user in users]
    assert all([user not in users for user in workspace_users])
    assert workspace_id not in linked_workspace


