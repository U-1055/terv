from PySide6.QtCore import Signal, QObject

from client.src.gui.windows.windows import UserFlowWindow, PersonalTasksWindow
from test.client_test.utils.mocked_objects.views import TestBaseView, TestTaskWidgetView


class TestBaseWindow(QObject):
    pass


class TestPopUpAuthWindow:
    pass


class TestUserFlowWindow(TestBaseWindow):

    def place_task_widget(self) -> TestTaskWidgetView:
        return TestTaskWidgetView()

    def close(self):
        pass


class TestPersonalTasksWindow(TestBaseWindow):
    pass
