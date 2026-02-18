"""Тест на переключение окон"""
import pytest

from pathlib import Path
import time

from client.main import launch, Model, MainWindow, Logic, DataStructConst, Requester
from test.client_test.utils.mocked_objects.test_main_window import TestMainWindow
from test.client_test.utils.mocked_objects.test_model import TestModel
from test.client_test.utils.mocked_objects.test_requester import TestRequester
from client.src.src.handlers.window_handlers.userspace_handler import UserSpaceWindowHandler
from client.src.src.handlers.window_handlers.personal_tasks_handler import PersonalTasksWindowHandler
from test.client_test.utils.mocked_objects.test_links_handler import TestLinksHandler, TestCashManager


@pytest.mark.parametrize(
    ['timeout'],
    [[i] for i in range(1, 3)]
)
def test_windows_switching(timeout: int):
    is_closed = False

    def closed():
        nonlocal is_closed
        is_closed = True

    view = TestMainWindow()
    requester = Requester('')
    model = TestModel('', '')
    logic = Logic(view, model, TestLinksHandler('', TestCashManager), requester, timeout)

    view.press_btn_open_userspace()
    opened_handler = logic._opened_now
    handlers = logic._win_handlers
    opened_handler.closed.connect(closed)

    assert isinstance(opened_handler, UserSpaceWindowHandler), f'Window was not opened. Logic._opened_now = {opened_handler}'  # Проверка открытия окна
    assert len(handlers) == 1, f'Handler was not added to win_handlers. Logic._win_handlers = {handlers}'

    time.sleep(timeout + 1)  # timeout + задержка, т.к. удаление происходит чуть позднее таймаута
    view.press_btn_open_personal_tasks_window()
    view.press_btn_open_userspace()

    assert is_closed, f'Window was not closed after timeout'   # Проверка закрытия окна

    view.press_btn_open_userspace()  # Открыли ПП
    first_handler = logic._opened_now
    view.press_btn_open_personal_tasks_window()  # Переключили на другое окно

    win_handlers = logic._win_handlers  # В списке окон должно быть два окна
    opened_handler = logic._opened_now
    assert len(win_handlers) == 2, f'Handler was not added to win_handlers. Logic._win_handlers = {handlers}'
    assert isinstance(opened_handler, PersonalTasksWindowHandler), f'Window was not switched'

    view.press_btn_open_userspace()  # Переключили обратно на ПП
    second_handler = logic._opened_now  # Должен использоваться тот же обработчик
    assert first_handler == second_handler, f'New handler created when timeout does not gone. Handler_type:{type(first_handler)}'


if __name__ == '__main__':
    test_windows_switching(1)
