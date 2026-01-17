"""Тест аутентификации"""
import datetime

import pytest
import jwt
import os
import time
import typing as tp

from pathlib import Path
import json

from test.server_test.utils.requester import TestRequester
from test.server_test.utils.model import Model
from common.base import CommonStruct as DataStruct
from test.conftest import set_config, TEST_CONFIG_PATH, SERVER_CONFIG_PATH, SERVER_WORKING_DIR

access_token_lifetime = 2  # Время жизни токенов (из auth_test_config.json)
refresh_token_life_time = 10
ds_const = DataStruct()


def create_token(key: str, sub: str, exp: datetime.datetime, iat: datetime.datetime):
    return jwt.encode(
               algorithm='HS256',
               key=key,
               payload={
                   'sub': sub,
                   'exp': exp,
                   'iat': iat
               }
           )


@pytest.fixture()
def requester() -> TestRequester:
    return TestRequester('http://localhost:5000')


@pytest.fixture()
def invalid_token() -> tp.Callable:
    yield create_token


@pytest.mark.f_data({
    TEST_CONFIG_PATH: 'utils/server_configs/auth_test_config.json',
    SERVER_CONFIG_PATH: '../../server/config.json',
    SERVER_WORKING_DIR: '../../server/api'
})
def test_no_register(requester, set_config):

    response = requester.authorize('___', '_')
    status_code = response.status_code
    content = response.json().get(DataStruct.content)

    set_config

    assert status_code == 400, f'Unknown status code when authorizing unknown user. Received status code: {status_code} must be 400'
    assert content is None, f'Content of the response is not None: {content}'


@pytest.mark.f_data({
    TEST_CONFIG_PATH: 'utils/server_configs/auth_test_config.json',
    SERVER_CONFIG_PATH: '../../server/config.json',
    SERVER_WORKING_DIR: '../../server/api'
})
@pytest.mark.parametrize(
    ['login', 'password', 'email'],
    [['sth_login', 'sth_password1', 'sth_email']]
)
def test_expired_access_token(requester, set_config, login: str, password: str, email: str):
    response = requester.register(login, password, email)  # Регистрируем
    status_code = response.status_code

    response = requester.authorize(login, password)  # Получаем access-токен
    auth_status_code = response.status_code
    auth_data = response.json().get(ds_const.content)

    if auth_data:
        access_token = auth_data.get(ds_const.access_token)
    else:
        assert False, f'No access token in response to request to endpoint /auth/login. Response: {response.json()}'

    time.sleep(access_token_lifetime + 1)  # Ждём пока истечёт токен
    response = requester.get_user_info(access_token)  # Запрашиваем данные по невалидному токену
    get_request_status_code = response.status_code
    get_content = response.json().get(DataStruct.content)

    set_config
    assert status_code == 200, f'Status code {status_code} must be 200'
    assert auth_status_code == 200, f'Status code {auth_status_code} must be 200'
    assert access_token, 'No access token in response to request to endpoint /auth/login'
    assert get_request_status_code == 401, f'Status code {get_request_status_code} must be 401. Response: {response}'
    assert get_content is None, f'Content of the response is not None: {get_content}'


@pytest.mark.f_data({
    TEST_CONFIG_PATH: 'utils/server_configs/auth_test_config.json',
    SERVER_CONFIG_PATH: '../../server/config.json',
    SERVER_WORKING_DIR: '../../server/api'
})
@pytest.mark.parametrize(
    ['login', 'password', 'email'],
    [['sth_login1', 'sth_password1', 'sth_email1']]
)
def test_expired_refresh_token(requester, set_config, login: str, password: str, email: str):
    requester.register(login, password, email)
    response = requester.authorize(login, password)
    refresh_token = response.json().get(DataStruct.content).get(DataStruct.refresh_token)

    time.sleep(refresh_token_life_time + 1)  # Ждём истечения refresh-токена

    response = requester.update_tokens(refresh_token)
    status_code = response.status_code
    content = response.json().get(DataStruct.content)

    set_config
    assert status_code == 400, f'Status code {status_code} must be 400'
    assert content is None, f'Content of the response is not None: {content}'


@pytest.mark.f_data({
    TEST_CONFIG_PATH: 'utils/server_configs/auth_test_config.json',
    SERVER_CONFIG_PATH: '../../server/config.json',
    SERVER_WORKING_DIR: '../../server/api'
})
@pytest.mark.parametrize(
    ['login', 'password', 'email', 'exp', 'iat'],
    [[
        'sth_login3',
        'sth_password3',
        'sth_email3',
        datetime.datetime.now(),
        datetime.datetime.now() + datetime.timedelta(seconds=access_token_lifetime)]]
)
def test_invalid_access(
        requester,
        set_config,
        invalid_token,
        login: str,
        password: str,
        email: str,
        exp: datetime.datetime,  # Параметры JWT.payload
        iat: datetime.datetime
        ):
    requester.register(login, password, email)
    response = requester.authorize(login, password)
    refresh_token = response.json().get(DataStruct.content).get(DataStruct.refresh_token)

    invalid_access = invalid_token('143143124', login, exp, iat)
    invalid_response = requester.get_user_info(invalid_access)
    invalid_status_code = invalid_response.status_code
    invalid_content = invalid_response.json().get(DataStruct.content)

    refresh_response = requester.get_user_info(refresh_token)
    refresh_status_code = refresh_response.status_code
    refresh_content = refresh_response.json().get(DataStruct.content)

    set_config

    assert invalid_status_code == 401, f'Status code {invalid_status_code} must be 401. Response: {invalid_response}'
    assert refresh_status_code == 401, f'Status code {refresh_status_code} must be 401. Response: {refresh_status_code}'

    assert invalid_content is None, f'Content of the response is not None: {invalid_content}'
    assert refresh_content is None, f'Content of the response is not None: {refresh_content}'


@pytest.mark.parametrize(
    ['login', 'password', 'email', 'exp', 'iat'],
    [[
        'sth_login4',
        'sth_password4',
        'sth_email4',
        datetime.datetime.now(),
        datetime.datetime.now() + datetime.timedelta(seconds=access_token_lifetime)]]
)
@pytest.mark.f_data({
    TEST_CONFIG_PATH: 'utils/server_configs/auth_test_config.json',
    SERVER_CONFIG_PATH: '../../server/config.json',
    SERVER_WORKING_DIR: '../../server/api'
})
def test_invalid_refresh(
        requester,
        set_config,
        invalid_token,
        login: str,
        password: str,
        email: str,
        exp: datetime.datetime,  # Параметры JWT.payload
        iat: datetime.datetime
        ):
    requester.register(login, password, email)
    response = requester.authorize(login, password)
    access_token = response.json().get(DataStruct.content).get(DataStruct.access_token)

    invalid_refresh = invalid_token('143143124', login, exp, iat)
    invalid_response = requester.update_tokens(invalid_refresh)
    invalid_status_code = invalid_response.status_code
    invalid_content = invalid_response.json().get(DataStruct.content)

    access_response = requester.update_tokens(access_token)
    access_status_code = access_response.status_code
    access_content = access_response.json().get(DataStruct.content)

    set_config

    assert invalid_content is None, f'Content of the response is not None: {invalid_content}'
    assert access_content is None, f'Content of the response is not None: {access_content}'
    assert invalid_status_code == 400, f'Status code {invalid_status_code} must be 401. Response: {invalid_response}'
    assert access_status_code == 400, f'Status code {access_status_code} muse be 401. Response: {access_status_code}'


@pytest.mark.f_data({
    TEST_CONFIG_PATH: 'utils/server_configs/auth_test_config.json',
    SERVER_CONFIG_PATH: '../../server/config.json',
    SERVER_WORKING_DIR: '../../server/api'
})
@pytest.mark.skip(reason='Токен с временем жизни в 2 сек. успевает истечь. Запускать отдельно от других тестов и '
                         'менять access_token_lifetime в auth_test_config')
@pytest.mark.parametrize(
    ['login', 'password', 'email'],
    [['sth_login2', 'sth_password2', 'sth_email2']]
)
def test_recall_tokens(requester, login: str, password: str, email: str, set_config):
    requester.register(login, password, email)
    response = requester.authorize(login, password)
    refresh_token = response.json().get(DataStruct.content).get(DataStruct.refresh_token)
    access_token = response.json().get(DataStruct.content).get(DataStruct.access_token)

    recall_response = requester.recall_tokens((refresh_token, access_token), access_token)
    status_code = recall_response.status_code

    get_response = requester.get_user_info(access_token)  # Пытаемся использовать отозванные токены
    get_status_code = get_response.status_code
    get_content = get_response.json().get(DataStruct.content)

    update_response = requester.update_tokens(refresh_token)
    update_status_code = update_response.status_code

    set_config

    assert status_code == 200, f'Status code {status_code} must be 200. Response: {response}. Message: {response.json().get('message')}'
    assert get_status_code == 401, f'Status code {status_code} must be 401. Response: {get_response}'
    assert get_content is None, f'Content of the response is not None: {get_content}'
    assert update_status_code == 400, f'Status code {status_code} must be 400. Response: {update_response}'


@pytest.mark.f_data({
    TEST_CONFIG_PATH: 'utils/server_configs/auth_test_config.json',
    SERVER_CONFIG_PATH: '../../server/config.json',
    SERVER_WORKING_DIR: '../../server/api'
})
@pytest.mark.parametrize(
    ['login', 'password', 'email'],
    [['sth_login2', 'sth_password2', 'sth_email2']]
)
def test_not_unique_credentials(requester, set_config, login: str, password: str, email: str):
    requester.register(login, password, email)

    existing_login_response = requester.register(login, password, '@')
    existing_login_status_code = existing_login_response.status_code

    existing_email_response = requester.register('sth', password, email)
    existing_email_status_code = existing_email_response.status_code

    set_config

    assert existing_login_status_code == 400, f'Status code {existing_login_status_code} must be 400. Response: {existing_login_response.json()}'
    assert existing_email_status_code == 400, f'Status code {existing_email_status_code} must be 400. Response: {existing_email_response.json()}'


@pytest.mark.f_data({
    TEST_CONFIG_PATH: 'utils/server_configs/auth_test_config.json',
    SERVER_CONFIG_PATH: '../../server/config.json',
    SERVER_WORKING_DIR: '../../server/api'
})
@pytest.mark.parametrize(
    ['login', 'password', 'email'],
    [['sth_login5', 'sth_password5', 'sth_email5']]
)
def test_incorrect_credentials(requester, set_config, login: str, password: str, email: str):
    requester.register(login, password, email)

    incorrect_login_response = requester.authorize('11', password)
    incorrect_login_status_code = incorrect_login_response.status_code

    incorrect_password_response = requester.authorize(login, 'p')
    incorrect_password_status_code = incorrect_password_response.status_code

    incorrect_credentials_response = requester.authorize('11', 'p')
    incorrect_credentials_status_code = incorrect_credentials_response.status_code

    assert incorrect_login_status_code == 400, f'Status code {incorrect_login_status_code} must be 400. Response: {incorrect_login_response}'
    assert incorrect_password_status_code == 400, f'Status code {incorrect_password_status_code} must be 400. Response: {incorrect_password_response}'
    assert incorrect_credentials_status_code == 400, f'Status code {incorrect_credentials_status_code} must be 400. Response: {incorrect_credentials_response}'
