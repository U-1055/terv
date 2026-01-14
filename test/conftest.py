import pathlib

import pytest
from pathlib import Path
import json
import os
import contextlib

from test.client_test.utils.test_server import launch

test_config_path = 'test_config_path'
server_config_path = 'server_config_path'
server_working_dir = 'server_working_dir'


@pytest.fixture(scope='function')
def set_config(request: pytest.FixtureRequest):
    """
    Устанавливает тестовый конфиг на сервер, после теста устанавливает исходный конфиг. Аргументы передаются через
    pytest.mark.f_data: словарь вида
    {
    test_config_path: путь к тестовому конфигу. Если нет - конфиги не перезаписываются
    server_config_path: путь к серверному конфигу.
    server_working_dir: рабочая директория сервера. (В нашем случае: server/api)
    }
    """

    params = request.node.get_closest_marker('f_data').args[0]
    test_config = params.get(test_config_path)

    if test_config:
        with open(Path(params.get(test_config_path)), 'rb') as file:
            config = json.load(file)

        with open(Path(params.get(server_config_path)), 'rb') as file:
            last_config = json.load(file)

        with open(Path(params.get(server_config_path)), 'w') as file:  # Установка нового конфига
            json.dump(config, file)

    with contextlib.chdir(params.get(server_working_dir)):
        import server.api.app as app
        app.launch()

        yield

    if test_config:
        with open(Path(params.get(server_config_path)), 'w') as file:  # Возвращение старого конфига
            json.dump(last_config, file)


@pytest.fixture(scope='session')
def launch_test_server():
    launch()
