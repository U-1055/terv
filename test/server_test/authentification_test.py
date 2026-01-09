"""Тест аутентификации."""
import time

import pytest
from pathlib import Path
import json

from test.server_test.utils.requester import TestRequester
from test.server_test.utils.model import Model
from common.base import DataStruct

access_token_lifetime = 2  # Время жизни токенов (из auth_test_config.json)
refresh_token_life_time = 10
ds_const = DataStruct()

@pytest.fixture()
def requester() -> TestRequester:
    return TestRequester('http://localhost:5000')


@pytest.fixture()
def set_config():
    with open(Path('utils/server_configs/auth_test_config.json'), 'rb') as file:
        config = json.load(file)

    with open(Path('../../server/config.json'), 'rb') as file:
        last_config = json.load(file)

    with open(Path('../../server/config.json'), 'w') as file:  # Установка нового конфига
        json.dump(config, file)

    import server.api.app as app
    app.launch()

    yield

    with open(Path('../../server/config.json'), 'w') as file:  # Возвращение старого конфига
        json.dump(last_config, file)


def test_no_register(requester, set_config):

    response = requester.authorize('___', '_')
    status_code = response.status_code
    set_config
    assert status_code == 400, f'Unknown status code when authorizing unknown user. Received status code: {status_code} must be 400'


@pytest.mark.parametrize(
    ['login', 'password', 'email'],
    [['sth_login', 'sth_password', 'sth_email']]
)
def test_expired_access_token(requester, set_config, login: str, password: str, email: str):
    response = requester.register(login, password, email)
    status_code = response.status_code
    data = response.json()
    access_token = data[ds_const.content][ds_const.access_token]

    time.sleep(access_token_lifetime + 1)

    response = requester.get_user_info(access_token)
    status_code_2 = response.status_code

    assert status_code == 200, f'Status code {status_code} must be 200'
    assert access_token, f'No access token in response to request to endpoint /register'
    assert status_code_2 == 401, f'Status code {status_code_2} must be 401'

