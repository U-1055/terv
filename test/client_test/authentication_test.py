"""Тест логики аутентификации на клиенте."""
import time

import pytest

from client.main import run_main_config, Logic
from test.client_test.utils.mocked_objects.test_model import TestModel
from test.client_test.utils.mocked_objects.test_main_window import TestMainWindow
from client.src.requester.requester import Requester
from test.client_test.utils.mocked_objects.test_auth import TestPopUpAuthWindow, TestAuthView, TestRegisterView

MODEL = 'model'
AUTH_VIEW = 'auth_view'
REGISTER_VIEW = 'register_view'


@pytest.fixture(scope='function')
def client_config():

    root = TestMainWindow()
    model = TestModel('', '')
    requester = Requester('http://localhost:5000')
    logic = Logic(root, model, requester, 10, )

    root.press_btn_open_userspace()  # Переходим на ПП, чтобы логика отправила запрос
    time.sleep(1)  # Ждём, чтобы запрос точно успел пройти
    auth_view = root.auth_window.auth_window()   # Получаем окна
    register_view = root.auth_window.register_window()

    return {MODEL: model, AUTH_VIEW: auth_view, REGISTER_VIEW: register_view}


@pytest.mark.parametrize(
    ['login', 'password', 'email'],
    [['login1', 'password1_', 'email1'], ['login2', 'password1_', 'email2']]
)
def test_correct_insert(client_config: dict, login: str, password: str, email: str):
    model: TestModel = client_config.get(MODEL)
    auth_view: TestAuthView = client_config.get(AUTH_VIEW)
    register_view: TestRegisterView = client_config.get(REGISTER_VIEW)

    register_view.set_login(login)
    register_view.set_email(email)
    register_view.set_password(password)

    auth_view.set_login(login)
    auth_view.set_password(password)
    auth_view.press_btn_auth()

    assert not auth_view.is_error, f'Auth view set to error with correct input: login: {login}; password: {password}'


