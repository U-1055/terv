from PySide6.QtCore import Signal, QObject


from test.client_test.utils.mocked_objects.views import TestBaseView, TestTaskWidgetView
from test.client_test.utils.mocked_objects.test_auth import TestRegisterView, TestAuthView


class TestBaseWindow(QObject):
    pass


class TestUserSpaceWindow(TestBaseWindow):

    def place_task_widget(self) -> TestTaskWidgetView:
        return TestTaskWidgetView()

    def close(self):
        pass


class TestPersonalTasksWindow(TestBaseWindow):
    pass
