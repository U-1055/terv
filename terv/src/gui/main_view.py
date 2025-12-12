from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget
from PySide6.QtCore import Signal

import logging

from terv.src.ui.ui_main_window import Ui_Form


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.DEBUG)
logging.debug(f'Module main_view.py is running')


class MainWindow(QMainWindow):

    btn_pressed = Signal()

    def __init__(self):
        super().__init__()
        self._main_widget = QStackedWidget()

        container = QWidget()
        self._view = Ui_Form()
        self._view.setupUi(container)
        self._main_widget.insertWidget(0, container)
        self.setCentralWidget(self._main_widget)
        self._view.pushButton_2.clicked.connect(self.press_btn)

    def press_btn(self):
        self.btn_pressed.emit()



class BaseWindow:
    # Сигналы закрытия самого окна или окна приложения
    pass


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
    logic = Logic(root, Requester(''), Requester(''))

    setup_gui(root, app)
