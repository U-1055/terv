import pathlib

import pytest
from pathlib import Path
import json
import os
import contextlib

from test.client_test.utils.test_server import launch
from test.server_test.utils.test_database.base import DatabaseManager
from common.base import CommonStruct
from test.server_test.utils.requester import TestRequester

TEST_CONFIG_PATH = 'TEST_CONFIG_PATH'  # Параметры фикстур
SERVER_CONFIG_PATH = 'SERVER_CONFIG_PATH'
SERVER_WORKING_DIR = 'SERVER_WORKING_DIR'
TEST_DB_PATH = 'test_db_path'
LOGIN = 'login'
PASSWORD = 'password'
EMAIL = 'email'
TASKS_NUM = 'tasks_num'


@pytest.fixture(scope='function')
def set_config(request: pytest.FixtureRequest):
    """
    Устанавливает тестовый конфиг на сервер, после теста устанавливает исходный конфиг. Аргументы передаются через
    pytest.mark.f_data: словарь вида
    {
    TEST_CONFIG_PATH: путь к тестовому конфигу. Если нет - конфиги не перезаписываются
    SERVER_CONFIG_PATH: путь к серверному конфигу.
    SERVER_WORKING_DIR: рабочая директория сервера. (В нашем случае: server/api)
    }
    """

    params = request.node.get_closest_marker('f_data').args[0]
    test_config = params.get(TEST_CONFIG_PATH)

    if test_config:
        with open(Path(params.get(TEST_CONFIG_PATH)), 'rb') as file:
            config = json.load(file)

        with open(Path(params.get(SERVER_CONFIG_PATH)), 'rb') as file:
            last_config = json.load(file)

        with open(Path(params.get(SERVER_CONFIG_PATH)), 'w') as file:  # Установка нового конфига
            json.dump(config, file)

    with contextlib.chdir(params.get(SERVER_WORKING_DIR)):
        import server.api.app as app
        app.launch()

        yield

    if test_config:
        with open(Path(params.get(SERVER_CONFIG_PATH)), 'w') as file:  # Возвращение старого конфига
            json.dump(last_config, file)


@pytest.fixture(scope='function')
def config_limit_offset_test_db(request: pytest.FixtureRequest):
    """
    Устанавливает конфиг для теста limit&offset в тестовую БД.
    Принимает параметры (через f_data):
    
    test_db_path: путь к тестовой БД.
    login: логин добавляемого пользователя.
    password: пароль добавляемого пользователя.
    email: email добавляемого пользователя.
    tasks_num: число создаваемых задач.
    """

    params = request.node.get_closest_marker('f_data').args[0]
    test_db_path = params.get(TEST_DB_PATH)
    login = params.get(LOGIN)
    password = params.get(PASSWORD)
    tasks_num = params.get(TASKS_NUM)
    email = params.get(EMAIL)
    
    db_manager = DatabaseManager(test_db_path)
    db_manager.set_limit_offset_test_config(login, password, email, tasks_num)


@pytest.fixture(scope='session')
def launch_test_server():
    launch()


@pytest.fixture()
def access_token(request: pytest.FixtureRequest, requester) -> str:
    """
    Авторизует пользователя и возвращает access-токен. Принимает параметры (через f_data):
    login: логин пользователя.
    password: пароль пользователя.
    """
    params = request.node.get_closest_marker('f_data').args[0]
    login = params.get(LOGIN)
    password = params.get(PASSWORD)

    result = requester.authorize(login, password)
    return result.json().get(CommonStruct.content).get(CommonStruct.access_token)


@pytest.fixture()
def refresh_token(request: pytest.FixtureRequest, requester) -> str:
    """
    Авторизует пользователя и возвращает access-токен. Принимает параметры (через f_data):
    login: логин пользователя.
    password: пароль пользователя.
    """
    params = request.node.get_closest_marker('f_data').args[0]
    login = params.get(LOGIN)
    password = params.get(PASSWORD)

    result = requester.authorize(login, password)
    return result.json().get(CommonStruct.content).get(CommonStruct.refresh_token)


@pytest.fixture()
def requester() -> TestRequester:
    return TestRequester('http://localhost:5000')
