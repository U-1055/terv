from PySide6.QtWidgets import QHBoxLayout, QGridLayout, QVBoxLayout, QPushButton, QGraphicsScene
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor, QImage, QPixmap

import logging

from client.src.base import GuiLabels, ObjectNames, GUIStyles
from client.src.gui.windows.windows import BaseWindow
from client.src.ui.ui_settings_window import Ui_Form
from client.src.gui.widgets_view.settings_view import QThemeSwitcher
import client.src.client_model.resources_rc

logging.basicConfig(level=logging.DEBUG)


class SettingsWindow(BaseWindow):

    btn_log_out_pressed = Signal()
    btn_log_in_pressed = Signal()

    def __init__(self):
        super().__init__()
        self._view = Ui_Form()
        self._view.setupUi(self)
        self._view.label.setFont(GUIStyles.title_font)
        self._theme_switcher = QThemeSwitcher()

        self._is_connections = False

    def _place_image(self, image: QImage):
        scene = self._view.graphicsView.scene()
        if not scene:
            scene = QGraphicsScene()
            scene.addPixmap(image)

    def place_theme_widget(self, title: str = GuiLabels.change_theme) -> QThemeSwitcher:
        self._theme_switcher.set_title(title)
        self._view.widgets_layout.addWidget(self._theme_switcher, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        return self._theme_switcher

    def press_btn_log_out(self):
        self.btn_log_out_pressed.emit()

    def press_btn_log_in(self):
        self.btn_log_in_pressed.emit()

    def set_mode_log_in(self):
        self._view.label.setText(GuiLabels.enter_account)
        self._view.btn_account_ops.setText(GuiLabels.authorize)
        self._view.btn_account_ops.setObjectName(ObjectNames.btn_log_in)
        if self._is_connections:
            self._view.btn_account_ops.clicked.disconnect(self.press_btn_log_out)
        self._view.btn_account_ops.clicked.connect(self.press_btn_log_in)
        self._is_connections = True

    def set_mode_log_out(self):
        self._view.btn_account_ops.setText(GuiLabels.exit)
        self._view.btn_account_ops.setObjectName(ObjectNames.btn_exit)
        if self._is_connections:
            self._view.btn_account_ops.clicked.disconnect(self.press_btn_log_in)
        self._view.btn_account_ops.clicked.connect(self.press_btn_log_out)
        self._is_connections = True

    def set_username(self, username: str):
        self._view.label.setText(username)

    def set_image(self, image: QImage):
        self._place_image(image)



if __name__ == '__main__':
    wdg = SettingsWindow()
    wdg_themes = wdg.place_theme_widget()
    wdg_themes.put_theme('1', 'yellow')
    wdg_themes.put_theme('1', 'yellow')
    wdg_themes.put_theme('1', 'yellow')
    wdg_themes.put_theme('1', 'yellow')

