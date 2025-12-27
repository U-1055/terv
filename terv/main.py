"""
Точка входа
"""

from PySide6.QtWidgets import QApplication

from terv.src.src.main_logic import Logic
from terv.src.requester.requester import Requester
from terv.src.gui.main_view import MainWindow, setup_gui
from terv.src.client_model.model import Model


def launch(model_class, model_params: tuple, view_class, view_params: tuple, presenter_class, presenter_params: tuple):
    app = QApplication()
    root = view_class(*view_params)
    model = model_class(*model_params)
    logic = presenter_class(root, model, *presenter_params)

    setup_gui(root, app)


if __name__ == '__main__':
    from pathlib import Path
    from terv.src.base import DataStructConst

    launch(
        Model, (Path('data\\config_data\\storage'), Path('..\\..\\data'), DataStructConst()),
        MainWindow, (),
        Logic, (Requester('http://localhost:5000'), 10)
    )
