import pytest
from pathlib import Path
import json
import os


@pytest.fixture(scope='session')  # ToDo: настроить вызов фикстуры за один прогон тестов
def set_authentication_config():
    with open(Path('utils/server_configs/auth_test_config.json'), 'rb') as file:
        config = json.load(file)

    with open(Path('../../server/config.json'), 'rb') as file:
        last_config = json.load(file)

    with open(Path('../../server/config.json'), 'w') as file:  # Установка нового конфига
        json.dump(config, file)

    os.chdir('../../server/api')
    import server.api.app as app

    app.launch()

    yield

    os.chdir('../../test/server_test')

    with open(Path('../../server/config.json'), 'w') as file:  # Возвращение старого конфига
        json.dump(last_config, file)
