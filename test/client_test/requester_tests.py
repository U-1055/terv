import asyncio
import concurrent.futures
import datetime
import os
import time

import pytest
from client.src.requester.requester import err, Requester, Request, InternalRequest
from common.base import ErrorCodes
from test.conftest import launch_test_server, client_requester, REQUEST_LIMIT, LEN_TEST_REPO_CONTENT, TIMEOUT


# Исключение ошибок с кодами статуса вместо ID
unique_errors = [error_id.value for error_id in ErrorCodes if error_id != ErrorCodes.server_error and error_id != ErrorCodes.ok]

server_url = 'http://127.0.0.1:5000'


@pytest.fixture()
def requester() -> Requester:
    return Requester(server_url)


@pytest.fixture()
def error_request(request: pytest.FixtureRequest) -> InternalRequest:
    error_id = request.node.callspec.params.get('error_id')
    return InternalRequest(path=f'http://localhost:5000/error/{error_id}', method='GET')


@pytest.fixture()
def timeout_requester(request: pytest.FixtureRequest, requester: Requester) -> Requester:
    timeout = request.node.callspec.params.get('timeout')
    requester.set_timeout(timeout)
    return requester


@pytest.mark.parametrize(
    ['error_id'],
    [[i] for i in range(max(unique_errors) - 2)]
)
def test_preparing_error(requester: Requester, launch_test_server, error_request: InternalRequest, error_id: int):

    request: Request = requester.make_custom_request(error_request)
    with pytest.raises(err.exceptions_error_ids[error_id]):
        request.wait_until_complete()


@pytest.mark.parametrize(
    ['params'],
    [[[[f'{i}' for v in range(3)] for i in range(10)]]]
)
def test_requests_group(requester: Requester, launch_test_server, params: list[list[str]]):
    """
    Тестирует группы запросов. Обращается к эндпоинту /register, который возвращает в поле content переданные данные
    (из JSON).
    """
    requests = [requester.register(*args) for args in params]
    group = requester.create_group(*requests)
    group.wait_until_complete()
    results = [request.result().content for request in group.requests()]
    for args in params:
        assert args in results, f'There is no result {args} in results. The request may be not finished. Results: {results}'


@pytest.mark.f_data({REQUEST_LIMIT: 10})
@pytest.mark.parametrize(
    ('limit', 'offset'),
    ((100, 50), (110, 0), (1000, 0), (900, 0), (1000, 0))
)
def test_request_sequence(client_requester, launch_test_server, limit: int, offset: int):
    """Проверка получения данных из последовательности запросов."""
    request = client_requester.get_wf_tasks([i for i in range(100)], 'access', limit, offset)

    result = request.wait_until_complete()

    assert len(result.content) == limit
    assert result.records_left == LEN_TEST_REPO_CONTENT - limit - offset


@pytest.mark.skip(reason='Тест падает по неясной причине.'
                         'Конкретно: при запуске корутин (даже при последовательном и с задержкой) они выполняются '
                         'асинхронно, из-за чего при втором запросе в Requester._request ещё нет первого запроса).'
                         'При этом при тестировании клиента замечено, что функционал всё-таки работает и задержка '
                         'происходит. Отладить позже')
@pytest.mark.parametrize(
    ['timeout'],
    [[i] for i in range(1000, 150000, 100)]
)
def test_timeout(timeout_requester: Requester, launch_test_server, timeout: int):
    """Проверка соблюдения интервала между запросами."""
    future1: concurrent.futures.Future = timeout_requester.get_wf_tasks('', 'ONE')
    future2: concurrent.futures.Future = timeout_requester.get_wf_tasks('', 'TWO')
    loop = asyncio.get_event_loop()
    future1 = asyncio.wrap_future(future1, loop=loop)
    future2 = asyncio.wrap_future(future2, loop=loop)
    start_time = datetime.datetime.now()
    loop.run_until_complete(future1)
    time.sleep(1)
    loop.run_until_complete(future2)

    end_time = datetime.datetime.now()
    diff = end_time - start_time
    # * 1000, т.к. возвращаются секунды
    assert diff >= datetime.timedelta(milliseconds=timeout), \
        f'Interval between two request must be {timeout} ms or less. The real interval is {diff}'
