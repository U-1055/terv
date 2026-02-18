"""Замена MainView для тестов"""

from PySide6.QtCore import QObject, Signal

from test.client_test.utils.mocked_objects.windows import TestBaseWindow, TestUserSpaceWindow, TestPersonalTasksWindow
from client.src.gui.main_view import MainWindow
from test.client_test.utils.mocked_objects.test_auth import TestPopUpAuthWindow


class TestMainWindow(QObject):

    showed = Signal()  # Окно отрисовано
    btn_pressed = Signal()

    btn_open_personal_tasks_window_pressed = Signal()
    btn_open_userspace_pressed = Signal()
    btn_open_settings_pressed = Signal()
    btn_update_pressed = Signal()

    def __init__(self):
        super().__init__()
        self.auth_window = TestPopUpAuthWindow()

    def _destroy_window(self, idx: int):
        pass

    def _open_window(self, type_) -> TestBaseWindow:
        """Открытие окна"""
    def _show_auth_window(self, window: TestBaseWindow):
        pass

    def show_message(self, title: str, text: str):
        pass

    def press_btn_open_personal_tasks_window(self):
        self.btn_open_personal_tasks_window_pressed.emit()

    def press_btn_open_userspace(self):
        self.btn_open_userspace_pressed.emit()

    def press_btn(self):
        self.btn_pressed.emit()

    def show_error(self, title: str, message: str):
        pass

    def show_modal_window(self, window):
        pass

    def open_auth_window(self) -> TestPopUpAuthWindow:
        auth_window = TestPopUpAuthWindow()
        self.auth_window_sent.emit(auth_window)
        return auth_window

    def open_personal_tasks_window(self, _) -> TestPersonalTasksWindow:
        return TestPersonalTasksWindow()

    def open_userspace_window(self, _) -> TestUserSpaceWindow:
        return TestUserSpaceWindow()

    def open_calendar_window(self, _) -> TestBaseWindow:
        pass

    def open_window(self, window: TestBaseWindow):
        """Переключает окно в стековом виджете на указанное."""
        pass

    def set_style(self, style: str):
        pass
