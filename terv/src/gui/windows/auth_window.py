from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Signal

import logging

from terv.src.gui.widgets_view.userflow_view import TaskWidgetView
from terv.src.gui.windows.windows import BaseWindow


class AuthWindow(BaseWindow):
    def __init__(self):
        super().__init__()

    def password(self):
        pass
