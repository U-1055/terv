from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget
from PySide6.QtCore import Signal, Qt

import logging

from terv.src.ui.ui_main_window import Ui_Form
from terv.src.gui.windows.windows import PersonalTasksWindow, CalendarWindow, UserFlowWindow
from terv.src.gui.windows.windows import BaseWindow
from terv.src.gui.windows.auth_window import PopUpAuthWindow, AuthView, RegisterView
from terv.src.base import GUIStyles, GuiLabels


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.DEBUG)
logging.debug(f'Module main_view.py is running')


class MainWindow(QMainWindow):

    showed = Signal()  # Окно отрисовано
    btn_pressed = Signal()

    btn_open_personal_tasks_window_pressed = Signal()
    btn_open_userflow_pressed = Signal()
    btn_update_pressed = Signal()

    def __init__(self):
        super().__init__()

        container = QWidget()

        self._auth_window: PopUpAuthWindow = None

        self._view = Ui_Form()
        self._view.setupUi(container)
        self.setCentralWidget(container)
        self._view.pushButton.setText('Task')
        self._view.pushButton_2.setText('UserFlow')
        self._view.pushButton.clicked.connect(self.press_btn_open_personal_tasks_window)
        self._view.pushButton_2.clicked.connect(self.press_btn_open_userflow)

    def _destroy_window(self, idx: int):
        self._view.wdg_window.removeWidget(idx)
        logging.debug(f'Window idx {idx} destroyed')

    def _open_window(self, type_) -> BaseWindow:
        """Открытие окна"""
        window = type_()
        self._view.wdg_window.insertWidget(-1, window)
        current_idx = self._view.wdg_window.count()
        window.destroyed.connect(lambda: self._destroy_window(current_idx))
        self._view.wdg_window.setCurrentWidget(window)

        return window

    def _show_auth_window(self, window: BaseWindow):
        window.setWindowModality(Qt.WindowModality.ApplicationModal)
        window.show()

    def press_btn_open_personal_tasks_window(self):
        self.btn_open_personal_tasks_window_pressed.emit()

    def press_btn_open_userflow(self):
        self.btn_open_userflow_pressed.emit()

    def press_btn(self):
        self.btn_pressed.emit()

    def show_error(self, title: str, message: str):
        pass

    def open_auth_window(self) -> PopUpAuthWindow:
        window = PopUpAuthWindow(GUIStyles.normal_style, GUIStyles.error_style, GuiLabels())
        self.showed.connect(lambda: self._show_auth_window(window))

        return window

    def open_personal_tasks_window(self) -> BaseWindow:
        return self._open_window(PersonalTasksWindow)

    def open_userflow_window(self) -> BaseWindow:
        return self._open_window(UserFlowWindow)

    def open_calendar_window(self) -> BaseWindow:
        return self._open_window(CalendarWindow)

    def open_window(self, window: BaseWindow):
        """Переключает окно в стековом виджете на указанное."""
        self._view.wdg_window.setCurrentWidget(window)
        logging.debug(f'{window} opened')

    def showEvent(self, event, /):
        self.showed.emit()


def setup_gui(root: MainWindow, app: QApplication):
    screen = root.screen()

    screen_width = screen.geometry().width()
    screen_height = screen.geometry().height()

    root_width = int(screen_width * 0.5)
    root_height = int(screen_height * 0.6)
    padx = (screen_width - root_width) // 2
    pady = (screen_height - root_height) // 2

    root.setGeometry(padx, pady, root_width, root_height)
    root.setMinimumSize(root_width, root_height)
    root.show()

    app.exec()


if __name__ == '__main__':
    from terv.src.src.main_logic import Logic
    from terv.src.requester.requester import Requester
    from threading import Thread

    app = QApplication()
    root = MainWindow()
    logic = Logic(root, Requester(''), Requester(''), 4)

    setup_gui(root, app)
