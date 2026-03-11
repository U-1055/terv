"""
Тесты CRUD-ов.
Во всех конфигах все личные объекты принадлежат пользователю (User) с id=1.
"""
import datetime

import jsonschema as js
import flask
from flask.testing import FlaskClient
import pytest
import jwt

import os
import typing as tp

from common.base import CommonStruct
from test.server_test.utils.test_database.base import DatabaseManager
from test.conftest import SERVER_CONFIG_PATH, SERVER_WORKING_DIR, TEST_CONFIG_PATH, TEST_DB_PATH
from server.storage.server_model import Model

IGNORE = f'IGNORE_VALUE_{datetime.datetime.now()}'  # Константа, помечающая параметр теста как игнорируемый
base_params = {
    SERVER_WORKING_DIR: '../../server/api',
    SERVER_CONFIG_PATH: '../../server/config.json',
    TEST_CONFIG_PATH: '../../test/server_test/utils/server_configs/limit_offset_test_config.json',
    TEST_DB_PATH: 'sqlite:///../../test/server_test/utils/test_database/database'
              }


class BaseSchema:
    """Базовый класс для работы со схемой."""

    number = 'number'
    object = 'object'
    string = 'string'

    def __init__(self, schema: dict[str, str]):
        super().__init__()
        self._schema = schema

    def add_fields(self, fields: dict) -> 'BaseSchema':
        """
        Обновляет схему и возвращает обновленную.

        :param fields: Данные для обновления схемы.

        """
        self._schema.update(fields)
        return BaseSchema(self._schema)

    @property
    def schema(self) -> dict:
        return self._schema


common_response_schema = BaseSchema({
    "type": "object",
    "status_code":
        {"type": BaseSchema.number},
})

common_error_schema = common_response_schema.add_fields(
    {
        "message":
            {"type": "string"},
        "error_id":
            {"type": "number"}
    })
valid_response_schema = common_error_schema.add_fields({"status_code": {"type": 200}})


@pytest.fixture(scope='session')
def controller_access_token() -> str:
    if os.getcwd().split('\\')[-1] != 'api':
        os.chdir('../../server/api')
    model = Model('../storage/storage')
    secret_ = model.get_secret()
    token_ = jwt.encode(
        key=secret_,
        algorithm='HS256',
        payload={
            'sub': '1',
            'exp': datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=15),  # Время истечения токена
            'iat': datetime.datetime.now(tz=datetime.timezone.utc)  # Время создания токена
        }
    )
    return token_


@pytest.fixture(scope='session')
def client(app: flask.Flask) -> FlaskClient:
    test_client = app.test_client()
    test_client.post('/register', json={CommonStruct.login: 'NEW NAME', CommonStruct.email: 'NEW EMAIL',
                     CommonStruct.password: 'PASSWORD'})
    test_client.post('/auth/login', json={CommonStruct.login: 'NEW NAME', CommonStruct.password: 'PASSWORD'})

    return test_client


@pytest.fixture(scope='session')
def app() -> flask.Flask:
    if os.getcwd().split('\\')[-1] != 'api':
        os.chdir('../../server/api')
    import server.api.routes as routes

    app_ = routes.app
    return app_


@pytest.fixture(scope='function')
def set_db_get_config(request: pytest.FixtureRequest):
    """
    Добавляет пользователя в БД.
    """
    db_manager = DatabaseManager('sqlite:///../../test/server_test/utils/test_database/database')
    db_manager.add_new_user()
    params = request.node.callspec.params
    config_num = params.get('config_num')
    if config_num:
        db_manager.choose_db_config(config_num)


@pytest.mark.f_data(base_params)
@pytest.mark.parametrize(
    ['uri', 'expected_schema', 'query_params', 'exp_status_code', 'config_num', 'exp_content', 'exp_content_ids'],
    [
        ['/users', valid_response_schema, {}, 200, None, IGNORE, IGNORE],
        ['/ws_tasks', valid_response_schema, {}, 200, None, IGNORE, IGNORE],
        [
            '/personal_tasks', valid_response_schema, {}, 200,
            DatabaseManager.getting_config_personal_tasks, IGNORE, [i for i in range(10) if i % 2 == 0]
        ],
        # Тесты поиска
        # ID указан согласно порядку создания объектов в конфиге. + 1, т.к. каждый раз создаётся ещё один пользователь
        [
            '/users/search', valid_response_schema, {CommonStruct.username: '#90'},
             200, DatabaseManager.searching_config, IGNORE, [92]
        ],
        [
            '/users/search', valid_response_schema, {CommonStruct.username: 'User'}, 200,
            DatabaseManager.searching_config, IGNORE, [i for i in range(2, 102)]
        ],
        [
            '/users/search', valid_response_schema, {CommonStruct.email: '9'}, 200,
            DatabaseManager.searching_config, IGNORE, [11, 21, 31, 41, 51, 61, 71, 81, 91, 92, 93, 94, 95, 96, 97, 98, 99,
                                                       100, 101]
        ]
    ],
)
def test_get_model(set_config, client: FlaskClient, uri: str, expected_schema: BaseSchema, query_params: tp.Sequence,
                   exp_status_code: int, set_db_get_config, controller_access_token: str, config_num: int | None,
                   exp_content: tp.Sequence[dict], exp_content_ids: tp.Sequence[int]):
    response = client.get(uri, query_string=query_params, headers={'Authorization': controller_access_token})
    js.validate(response.json, schema=expected_schema.schema)

    assert response.status_code == exp_status_code
    if exp_content != IGNORE:
        assert response.json.get(CommonStruct.content) == exp_content
    if exp_content_ids != IGNORE:
        ids = [dict_.get("id") for dict_ in response.json.get(CommonStruct.content)]
        assert tuple(ids) == tuple(exp_content_ids), f'Response: {response.json}'
