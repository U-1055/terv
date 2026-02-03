from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QDialog, QMessageBox
from PySide6.QtCore import Signal, Qt

import logging

from client.src.ui.ui_main_window import Ui_Form
from client.src.gui.windows.windows import PersonalTasksWindow, CalendarWindow
from client.src.gui.windows.userflow_window import UserFlowWindow
from client.src.gui.windows.windows import BaseWindow
from client.src.gui.windows.auth_window import PopUpAuthWindow
from client.src.base import GUIStyles, GuiLabels
import client.src.gui.view_utils as utils

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.DEBUG)
logging.debug(f'Module main_view.py is running')


class MainWindow(QMainWindow):

    DialogShowingType = utils.DialogShowingType

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

        self._opened_dialog_windows: list[QDialog] = []
        self._opened_message_windows: list[QMessageBox] = []

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
        window.show()
        window.setWindowModality(Qt.WindowModality.ApplicationModal)
        window.raise_()

    def _remove_dialog_window(self, window: QDialog):
        logging.debug(f'Dialog window {window} closed.')
        if window in self._opened_dialog_windows:
            self._opened_dialog_windows.remove(window)

    def _remove_message_window(self, window: QMessageBox):
        logging.debug(f'Message window {window} closed.')
        if window in self._opened_message_windows:
            self._opened_message_windows.remove(window)

    def press_btn_open_personal_tasks_window(self):
        self.btn_open_personal_tasks_window_pressed.emit()

    def press_btn_open_userflow(self):
        self.btn_open_userflow_pressed.emit()

    def press_btn(self):
        self.btn_pressed.emit()

    def set_style(self, style: str):
        self.setStyleSheet(style)

    def show_error(self, title: str, message: str):
        pass

    def show_dialog_window(self, window: QDialog, title: str = GuiLabels.default_dialog_window_title,
                           showing_type: int = utils.DialogShowingType.unique, modality: bool = True,
                           frameless: bool = False):
        """
        Показывает диалоговое окно.
        С параметром unique_type = True не выведет ничего, если уже выведено окно этого типа.
        Предупреждение: не следует создавать сразу несколько модальных окон (лучше вообще избегать одновременного
        вывода нескольких окон), т.к. это может привести к сложностям в работе пользователя с ними.

        :param window: Выводимое окно (QDialog). Обязательно должно иметь возможность закрыться (иметь для этого кнопку
                       или что-то другое) каким-либо другим способом, кроме как средствами системы, т.к. шапка окна
                       удаляется.
        :param title: Заголовок окна. Не будет отображаться, если frameless = True.
        :param showing_type: Тип показа окна (MainWindow.DialogShowingType). Если DialogShowingType.unique - то окно не будет выведено,
                            если уже выведены другие окна этого типа. Если DialogShowingType.add - выводится в любом случае.
                            Если DialogShowingType.replace - выводится с заменой всех остальных окон.
                            (По умолчанию - DataShowingType.unique).
        :param modality: Является ли окно модальным?
        :param frameless: Является ли окно безрамочным?
        """

        if showing_type == self.DialogShowingType.unique:  # Проверка уникальности
            for opened_window in self._opened_dialog_windows:
                if type(window) is type(opened_window):
                    return
        elif showing_type == self.DialogShowingType.replace:
            for opened_window in self._opened_dialog_windows:  # Закрытие всех окон того же типа
                if type(window) is type(opened_window):
                    opened_window.close()
                else:
                    print(type(window), type(opened_window))

        self._opened_dialog_windows.append(window)
        window.finished.connect(lambda: self._remove_dialog_window(window))
        if modality:
            window.setWindowModality(Qt.WindowModality.ApplicationModal)
        window.setParent(self)
        window.setWindowTitle(title)
        flags = Qt.WindowType.Dialog | Qt.WindowType.Dialog.WindowStaysOnTopHint
        if frameless:
            flags |= Qt.WindowType.Dialog.CustomizeWindowHint
        window.setWindowFlags(flags)

        window.show()

    def show_message(self, title: str, message: str):
        """
        Выводит на экран окно сообщения.
        Если уже есть выведенные окна с такими же названием и сообщением - не выводит ничего.
        """

        for message_box in self._opened_message_windows:  # Проверка уникальности
            if message_box.text() == message_box and message_box.windowTitle() == title:
                return

        message_box = QMessageBox(parent=self)
        message_box.setText(message)
        message_box.setWindowTitle(title)
        message_box.finished.connect(lambda: self._remove_dialog_window(message_box))
        self._opened_message_windows.append(message_box)
        message_box.setWindowFlags(Qt.WindowType.Window.WindowStaysOnTopHint | Qt.WindowType.Window)
        message_box.exec()

    def open_auth_window(self) -> PopUpAuthWindow:
        if self._auth_window:
            return self._auth_window

        window = PopUpAuthWindow(GUIStyles.normal_style, GUIStyles.error_style, GuiLabels())
        self._auth_window = window
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

    def close(self):
        super().close()

    def showEvent(self, event, /):
        self.showed.emit()


def setup_gui(root: MainWindow, app: QApplication):
    screen = root.screen()

    screen_width = screen.geometry().width()
    screen_height = screen.geometry().height()

    root_width = int(screen_width * 0.65)
    root_height = int(screen_height * 0.7)
    padx = (screen_width - root_width) // 2
    pady = (screen_height - root_height) // 2

    root.setGeometry(padx, pady, root_width, root_height)
    root.setMinimumSize(root_width, root_height)
    root.setWindowTitle('terv')
    root.show()

    app.exec()


if __name__ == '__main__':
    def open_all_dialog_windows():  # Вывод диалоговых окон одного и того же типа
        menu = WidgetSettingsMenu(['1', '2', '3'], ['1'])
        auth_window = PopUpAuthWindow('', '', title='TITLE')
        auth_window_1 = PopUpAuthWindow('', '', title='TITLE_1')
        window.show_dialog_window(auth_window)
        window.show_dialog_window(auth_window_1, showing_type=MainWindow.DialogShowingType.unique)

    from PySide6.QtCore import QTimer

    from test.client_test.utils.window import setup_gui
    from client.src.gui.widgets_view.userflow_view import WidgetSettingsMenu
    from client.src.gui.windows.auth_window import PopUpAuthWindow

    window = MainWindow()
    QTimer.singleShot(100, open_all_dialog_windows)

    setup_gui(window)

