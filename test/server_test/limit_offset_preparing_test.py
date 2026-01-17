"""Тест обработки limit&offset."""
import pytest

from test.server_test.utils.requester import TestRequester
import test.conftest as cf
from common.base import CommonStruct, DBFields

set_config = cf.set_config
config_limit_offset_test_db = cf.config_limit_offset_test_db
access_token = cf.access_token
requester = cf.requester

base_params = {
    cf.TEST_DB_PATH: 'sqlite:///utils/test_database/database',
    cf.TEST_CONFIG_PATH: 'utils/server_configs/limit_offset_test_config.json',
    cf.SERVER_CONFIG_PATH: '../../server/config.json',
    cf.SERVER_WORKING_DIR: '../../server/api',
    cf.LOGIN: 'login',
    cf.PASSWORD: 'password_1',
    cf.EMAIL: 'email',
    cf.TASKS_NUM: 100
}


@pytest.mark.f_data(base_params)
@pytest.mark.parametrize(
    ('limit',),
    ((5, ), (15, ), (25, ), (50, ), (75, ), (100, ))
)
def test_normal_limit(config_limit_offset_test_db, set_config, requester: TestRequester, access_token, limit: int):
    get_ids_request = requester.get_user_info(access_token)
    ids = get_ids_request.json().get(CommonStruct.content)[0].get(DBFields.assigned_to_user_tasks)
    request = requester.get_workflow_tasks(access_token, ids, limit, 0)

    request_content = request.json().get(CommonStruct.content)

    length = len(request_content)

    assert length == limit, f'Num of returned records ({length}) not equal the limit ({request}).'


@pytest.mark.f_data(base_params)
@pytest.mark.parametrize(
    ('limit',),
    ((101, ), (215, ), (122, ), (1423, ), (750, ), (120, ))
)
def test_over_limit(config_limit_offset_test_db, set_config, requester: TestRequester, access_token: str, limit: int):
    get_ids_request = requester.get_user_info(access_token)
    ids = get_ids_request.json().get(CommonStruct.content)[0].get(DBFields.assigned_to_user_tasks)
    request = requester.get_workflow_tasks(access_token, ids, limit, 0)

    length = len(request.json().get(CommonStruct.content))

    assert length == base_params.get(cf.TASKS_NUM), f'Num of returned records ({length}) not equal the limit ({request}).'


@pytest.mark.f_data(base_params)
@pytest.mark.parametrize(
    ('limit',),
    ((-1, ), ('@$%', ), ('122_', ))
)
def test_not_normal_limit(config_limit_offset_test_db, set_config, requester: TestRequester, access_token: str, limit: int):
    get_ids_request = requester.get_user_info(access_token)
    ids = get_ids_request.json().get(CommonStruct.content)[0].get(DBFields.assigned_to_user_tasks)
    request = requester.get_workflow_tasks(access_token, ids, limit, 0)

    status_code = request.status_code
    content = request.json().get(CommonStruct.content)

    assert status_code == 400, f'Status code must be 400, but it is {status_code}. Response: {request.json()}'
    assert content is None, f'Content of this response must be None, but it is {content}. Response: {request.json()}'


@pytest.mark.f_data(base_params)
@pytest.mark.parametrize(
    ('offset',),
    ((0, ), (1,), (10, ), (20, ), (30, ), (40, ))
)
def test_normal_offset(config_limit_offset_test_db, set_config, requester: TestRequester, access_token: str, offset: int):
    get_ids_request = requester.get_user_info(access_token)
    ids = get_ids_request.json().get(CommonStruct.content)[0].get(DBFields.assigned_to_user_tasks)
    request = requester.get_workflow_tasks(access_token, ids, 1000, offset)

    content = request.json().get(CommonStruct.content)

    for rec in content:  # Предполагается, что нумерация id начинается с 0 (т.к. каждый раз делается новый конфиг)
        rec_id = rec.get(DBFields.id)
        assert rec_id in range(offset, base_params.get(cf.TASKS_NUM) + 1), \
            f'ID of the model not in allowed range ({offset} - {cf.TASKS_NUM}). ID: {rec_id}'

@pytest.mark.f_data(base_params)
@pytest.mark.parametrize(
    ('offset', ),
    ((-1, ), ('asdas', ), ('dfsa',))
)
def test_not_normal_offset(config_limit_offset_test_db, set_config, requester: TestRequester, access_token: str, offset: int):
    get_ids_request = requester.get_user_info(access_token)
    ids = get_ids_request.json().get(CommonStruct.content)[0].get(DBFields.assigned_to_user_tasks)
    request = requester.get_workflow_tasks(access_token, ids, None, offset)

    status_code = request.status_code
    content = request.json().get(CommonStruct.content)

    assert status_code == 400, f'Status code must be 400, but it is {status_code}. Response: {request.json()}'
    assert content is None, f'Content of this response must be None, but it is {content}. Response: {request.json()}'


@pytest.mark.f_data(base_params)
@pytest.mark.parametrize(
    ('offset', ),
    ((400, ), (500, ), (102, ))
)
def test_over_offset(config_limit_offset_test_db, set_config, requester: TestRequester, access_token: str, offset: int):
    get_ids_request = requester.get_user_info(access_token)
    ids = get_ids_request.json().get(CommonStruct.content)[0].get(DBFields.assigned_to_user_tasks)
    request = requester.get_workflow_tasks(access_token, ids, None, offset)

    content = request.json().get(CommonStruct.content)

    assert content is None, f'Content of the response must be None, but it is {content}'


@pytest.mark.f_data(base_params)
def test_no_limit_offset(config_limit_offset_test_db, set_config, requester: TestRequester, access_token: str):
    get_ids_request = requester.get_user_info(access_token)
    ids = get_ids_request.json().get(CommonStruct.content)[0].get(DBFields.assigned_to_user_tasks)
    request = requester.get_workflow_tasks(access_token, ids, None, None)

    length = len(request.json().get(CommonStruct.content))

    assert length == base_params.get(cf.TASKS_NUM), f'Num of returned records ({length}) must be {base_params.get(cf.TASKS_NUM)}.'

