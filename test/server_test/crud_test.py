"""Тесты CRUD-ов."""
import asyncio
import concurrent.futures

import pytest

import typing as tp

from common.base import CommonStruct
from test.conftest import client_requester, set_config, SERVER_WORKING_DIR, access_token, LOGIN, PASSWORD, register, EMAIL
from client.src.requester.requester import Request, Requester


base_params = {
    SERVER_WORKING_DIR: '../../server/api',
    LOGIN: 'test_login1',
    PASSWORD: 'password_1',
    EMAIL: 'test_email'
              }


@pytest.fixture()
def request_get(request: pytest.FixtureRequest) -> Request:
    endpoint = request.node.callspec.params.get('endpoint')
    return Request(endpoint, 'GET')


def wait(future: concurrent.futures.Future) -> tp.Any:
    """
    Ждёт завершения объекта concurrent.futures.Future и возвращает результат его выполнения.
    Передаёт все исключения, вызванные при выполнении.
    """
    future = asyncio.wrap_future(future)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(future)
    try:
        return future.result()
    except Exception as e:
        raise e


@pytest.mark.f_data({
    SERVER_WORKING_DIR: '../../server/api',
    LOGIN: 'test_login1',
    PASSWORD: 'password_1',
    EMAIL: 'test_email'
})
@pytest.mark.parametrize(
    ['endpoint'],
    [['http://localhost:5000/wf_tasks', 'http://localhost:5000/personal_tasks', 'http://localhost:5000/wf_many_days_events',
      'http://localhost:5000/personal_many_days_events', 'http://localhost:5000/wf_daile_events',
      'http://localhost:5000/wf_many_days_events']]
)
def test_data_receiving(client_requester: Requester,
                        set_config,
                        request_get: Request,
                        register,
                        access_token: str,
                        endpoint: str):

    request = client_requester.make_custom_request(request_get)
    request.wait_until_complete()
    response = request.result()

    assert response.content is not None, (f'Request to endpoint: {endpoint} has not returned anything.'
                                          f'Request: {request_get}. Response: {response}.')


@pytest.mark.parametrize.f_data(base_params)
def test_get_wf_tasks(client_requester: Requester, set_config, access_token):
    request = Request('http://localhost:5000/wf_tasks', 'GET')

