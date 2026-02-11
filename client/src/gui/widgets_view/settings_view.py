"""Виджеты окна настроек."""
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QSizePolicy, QVBoxLayout, QLabel

from client.src.base import GuiLabels
from client.src.gui.sub_widgets.base import BaseWidget


class QThemeSwitcher(BaseWidget):
    """
    Виджет для переключения тем.

    :param themes: Темы, кнопки для выбора которых будут размещены в виджете.
                   Словарь в формате: {<название темы>: <цвет> (объект QColor)}.

    :var theme_changed: Сигнал, испускаемый при изменении темы. Передаёт название темы.

    """

    theme_changed = Signal(str)

    def __init__(self, title: str = '', themes: dict[str, QColor] | None = None):
        super().__init__()
        if themes:
            self._themes = themes
        else:
            self._themes: dict[str, QColor] = {}

        main_layout = QVBoxLayout()

        self._widgets_layout = QHBoxLayout()
        self._widgets_layout.setSizeConstraint(QHBoxLayout.SizeConstraint.SetMinimumSize)
        self._lbl_title = QLabel(title, alignment=Qt.AlignmentFlag.AlignCenter)
        self._lbl_title.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)

        main_layout.addWidget(self._lbl_title, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
        main_layout.addLayout(self._widgets_layout)
        self.setLayout(main_layout)

    def _clear_gui(self):
        for i in range(self._widgets_layout.count()):
            widget = self._widgets_layout.itemAt(i).widget()
            widget.hide()

    def change_theme(self, theme: str):
        self.theme_changed.emit(theme)

    def put_theme(self, theme: str, color: str | QColor):
        if isinstance(color, QColor):
            self._themes[theme] = color
        else:
            self._themes[theme] = QColor(color)
        btn_theme = QPushButton()
        btn_theme.setStyleSheet(''.join(['QPushButton {background-color:',
                                         f'{self._themes[theme].name(QColor.NameFormat.HexRgb)}', '}']))
        btn_theme.clicked.connect(lambda: self.change_theme(theme))
        btn_theme.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self._widgets_layout.addWidget(btn_theme, alignment=Qt.AlignmentFlag.AlignLeft)

    def delete_theme(self, theme: str):
        if theme in self._themes:
            self._themes.pop(theme)

    def theme_color(self, theme: str) -> str:
        return self._themes.get(theme)

    def clear(self):
        self._themes = dict()
        self._clear_gui()

    def title(self) -> str:
        return self._lbl_title.text()

    def set_title(self, title: str):
        self._lbl_title.setText(title)


if __name__ == '__main__':
    wdg = QThemeSwitcher('Theme Switcher')
    wdg.put_theme('Theme#1', 'black')
    wdg.put_theme('Theme#2', 'white')
    wdg.put_theme('Theme#3', 'yellow')
    wdg.put_theme('Theme#4', 'orange')
    wdg.put_theme('Theme#5', 'blue')

    wdg.theme_changed.connect(print)

