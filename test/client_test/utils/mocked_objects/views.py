from PySide6.QtCore import QObject, Signal


class TestBaseView(QObject):
    pass


class TestTaskWidgetView(TestBaseView):
    task_completed = Signal(str)

    def __init__(self):
        super().__init__()

    def complete_task(self, name: str):
        self.task_completed.emit()

    def add_task(self, name):
        pass

    @property
    def tasks(self) -> tuple[str, ...]:
        return '', ''
