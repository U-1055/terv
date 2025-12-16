"""
Точка входа
"""
from PySide6.QtWidgets import QApplication

from terv.src.src.main_logic import Logic
from terv.src.requester.requester import Requester
from terv.src.gui.main_view import MainWindow, setup_gui


if __name__ == '__main__':

    app = QApplication()
    root = MainWindow()
    logic = Logic(root, Requester(''), Requester(''), 5)

    setup_gui(root, app)
