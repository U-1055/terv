"""Тест обработки последовательности запросов (получения данных частями)."""
import pytest

import asyncio
import concurrent.futures

from client.src.requester.requester import Requester
from test.conftest import launch_test_server, client_requester, REQUEST_LIMIT, LEN_TEST_REPO_CONTENT


@pytest.mark.f_data({REQUEST_LIMIT: 10})
@pytest.mark.parametrize(
    ('limit', 'offset'),
    ((100, 50), (110, 0), (1000, 0), (900, 0), (1000, 0))
)
def test_data_receiving(client_requester, launch_test_server, limit: int, offset: int):

    future: concurrent.futures.Future = client_requester.get_wf_tasks([i for i in range(100)], 'access', limit, offset)
    loop = asyncio.get_event_loop()
    future = asyncio.wrap_future(future, loop=loop)
    loop.run_until_complete(future)

    result = future.result()

    assert len(result.content) == limit
    assert result.records_left == LEN_TEST_REPO_CONTENT - limit - offset


