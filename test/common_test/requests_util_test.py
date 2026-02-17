import datetime

import pytest

from common_utils.log_utils.request_time_logger import RequestsTimeHandler


@pytest.fixture()
def requests_time_handler() -> RequestsTimeHandler:
    return RequestsTimeHandler('../../log/requests_time.txt')


@pytest.mark.parametrize(
    ['values', 'expected_percentile', 'percentile_value'],
    [
        [[
            [*[0 for i in range(900)], *[1000 for j in range(100)]]
        ], 90, 999],
        [[
            [*[0 for t in range(75000)], *[1000 for y in range(25000)]]
        ], 75, 999],
        [[
            [*[0 for x in range(5000)], *[1000 for z in range(5000)]]
        ], 50, 999]
    ]
)
def test_percentile(values: list[int], expected_percentile: int, percentile_value: int, requests_time_handler):

    percentile = round(requests_time_handler._get_percentile(percentile_value, *values), 2)

    assert percentile == expected_percentile


