"""
Точка входа
"""

from PySide6.QtWidgets import QApplication

from pathlib import Path

from client.src.src.main_logic import Logic
from client.src.requester.requester import Requester
from client.src.gui.main_view import MainWindow, setup_gui
from client.src.client_model.model import Model
from client.src.base import DataStructConst
from common.base import CommonStruct


def launch(model_class, model_params: tuple, view_class, view_params: tuple, presenter_class, presenter_params: tuple):
    app = QApplication()
    root = view_class(*view_params)
    model = model_class(*model_params)
    model.set_access_token(None)
    model.set_refresh_token(None)
    logic = presenter_class(root, model, *presenter_params)

    setup_gui(root, app)


def run_main_config():
    launch(
        Model, (Path('data\\config_data\\storage'), Path('..\\..\\data'), DataStructConst()),
        MainWindow, (),
        Logic, (Requester('http://localhost:5000'), 0.1)
    )


if __name__ == '__main__':
    run_main_config()

