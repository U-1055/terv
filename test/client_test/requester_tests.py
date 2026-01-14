import asyncio
import os
import time

import pytest
from client.src.requester.requester import err, Requester, Request
from test.conftest import set_config, server_config_path, server_working_dir, test_config_path, launch_test_server
from common.base import ErrorCodes

# Исключение ошибок с кодами статуса вместо ID
unique_errors = [error_id.value for error_id in ErrorCodes if error_id != ErrorCodes.server_error and error_id != ErrorCodes.ok]

server_url = 'http://127.0.0.1:5000'

@pytest.fixture()
def requester() -> Requester:
    return Requester(server_url)


def test_unauthorized(requester: Requester, launch_test_server):

    future: asyncio.Future = requester.get_user_info('')
    with pytest.raises(err.ExpiredAccessToken, match='.'):
        future.add_done_callback(lambda future: future.result())


@pytest.mark.parametrize(
    ['error_id'], [[id_] for id_ in range(max(unique_errors) + 1)])  # ToDo: не вызываются коллбэки, передаваемые в add_done_callback
def test_preparing_error(requester: Requester, launch_test_server, error_id: int):

    def prepare(future: asyncio.Future):
        assert False
        with pytest.raises(err.exceptions_error_ids.get(error_id), match='.') as exc:
            future.result()

    response = requester.get_user_info('a')
    response.add_done_callback(prepare)
    time.sleep(5)
