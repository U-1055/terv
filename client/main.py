"""
Точка входа
"""
from PySide6.QtWidgets import QApplication

from pathlib import Path
import threading
import logging
import locale

from common_utils.log_utils.memory_logger import check_memory
from client.src.src.main_logic import Logic
from client.src.requester.requester import Requester
from client.src.gui.main_view import MainWindow, setup_gui
from client.src.client_model.model import Model
from client.src.base import DataStructConst
from client.src.client_model.links_handler import LinksHandler
from client.src.requester.cash_manager import CashManager

logging.basicConfig(level=logging.INFO)
locale.setlocale(locale.LC_TIME, 'Russian')


def launch(model_class, model_params: tuple, view_class, view_params: tuple, presenter_class, presenter_params: tuple):
    app = QApplication()
    root = view_class(*view_params)
    model = model_class(*model_params)
    logic = presenter_class(root, model, *presenter_params)
    setup_gui(root, app)


# ToDo: переделать параметры в точке входа, чтобы можно было отметить cash_manager обязательным


def run_main_config(check_ram: bool = False):
    if check_ram:
        thread = threading.Thread(target=check_memory, args=[Path('../log/memory_client.txt')], daemon=True)
        thread.start()
    requester = Requester('http://localhost:5000')

    launch(
        Model, (Path('data\\config_data\\storage'), Path('..\\..\\data'), DataStructConst()),
        MainWindow, (),
        Logic, (LinksHandler(Path('data/config_data/records_storage')), requester, 0.1)
    )


if __name__ == '__main__':
    run_main_config(True)
