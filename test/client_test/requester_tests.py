import asyncio
import os

import pytest
from client.src.requester.requester import err, Requester
from test.conftest import set_config, server_config_path, server_working_dir, test_config_path

os.chdir('../../test/server_test')


@pytest.fixture()
def requester() -> Requester:
    return Requester('http://localhost:5000')


@pytest.mark.f_data({server_working_dir: '../../server/api'})
def test_unauthorized(requester: Requester, set_config):
    def prepare_request(future: asyncio.Future):
        set_config
        with pytest.raises(err.ExpiredAccessToken):
            future.result()

    future: asyncio.Future = requester.get_user_info('')
    future.add_done_callback(lambda future: prepare_request(future))


@pytest.mark.f_data({server_working_dir: '../../server/api'})
def test_retry_request(requester: Requester):
    """Проверяет повторение запроса."""
    pass




