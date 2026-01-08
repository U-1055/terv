"""Замена MainView для тестов"""

from PySide6.QtCore import QObject, Signal

from test.client_test.utils.mocked_objects.windows import TestBaseWindow, TestPopUpAuthWindow, TestUserFlowWindow, TestPersonalTasksWindow
from client.src.gui.main_view import MainWindow


class TestMainWindow(QObject):

    showed = Signal()  # Окно отрисовано
    btn_pressed = Signal()

    btn_open_personal_tasks_window_pressed = Signal()
    btn_open_userflow_pressed = Signal()
    btn_update_pressed = Signal()

    def __init__(self):
        super().__init__()

    def _destroy_window(self, idx: int):
        pass

    def _open_window(self, type_) -> TestBaseWindow:
        """Открытие окна"""
    def _show_auth_window(self, window: TestBaseWindow):
        pass

    def press_btn_open_personal_tasks_window(self):
        self.btn_open_personal_tasks_window_pressed.emit()

    def press_btn_open_userflow(self):
        self.btn_open_userflow_pressed.emit()

    def press_btn(self):
        self.btn_pressed.emit()

    def show_error(self, title: str, message: str):
        pass

    def show_modal_window(self, window):
        pass

    def open_auth_window(self) -> TestPopUpAuthWindow:
        pass

    def open_personal_tasks_window(self) -> TestPersonalTasksWindow:
        return TestPersonalTasksWindow()

    def open_userflow_window(self) -> TestUserFlowWindow:
        return TestUserFlowWindow()

    def open_calendar_window(self) -> TestBaseWindow:
        pass

    def open_window(self, window: TestBaseWindow):
        """Переключает окно в стековом виджете на указанное."""
        pass
