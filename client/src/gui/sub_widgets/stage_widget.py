"""Виджет этапа проекта."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QToolButton, QFrame, QTextEdit)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class StageWidget(QWidget):
    """
    Виджет для отображения информации об этапе проекта.
    
    :param name: Название этапа.
    :param description: Полное описание этапа.
    :param date_start: Дата начала.
    :param date_end: Дата окончания.
    :param result: Планируемый результат.
    :param status: Статус этапа ('завершён', 'сейчас', 'планируется').
    :param stage_id: ID этапа.
    """
    
    def __init__(self, name: str, description: str, date_start: str, 
                 date_end: str, result: str, status: str, stage_id: int = 0):
        super().__init__()
        self._name = name
        self._full_description = description
        self._date_start = date_start
        self._date_end = date_end
        self._result = result
        self._status = status
        self._stage_id = stage_id
        self._is_expanded = False

        self._setup_ui()
        self._update_description_display()

    def _setup_ui(self):
        """Настройка интерфейса виджета."""
        self.setObjectName(f'stage_widget_{self._stage_id}')

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # Верхняя строка: название и статус
        top_layout = QHBoxLayout()
        
        self.lbl_name = QLabel(self._name)
        self.lbl_name.setFont(QFont("Calibri", 12, QFont.Weight.Bold))
        top_layout.addWidget(self.lbl_name)

        top_layout.addStretch()

        self.lbl_status = QLabel(self._status)
        self._set_status_style()
        top_layout.addWidget(self.lbl_status)

        main_layout.addLayout(top_layout)

        # Даты
        dates_layout = QHBoxLayout()
        self.lbl_dates = QLabel(f"С: {self._date_start}  по  {self._date_end}")
        self.lbl_dates.setFont(QFont("Calibri", 10))
        self.lbl_dates.setStyleSheet("color: #666666;")
        dates_layout.addWidget(self.lbl_dates)
        main_layout.addLayout(dates_layout)

        # Описание с кнопкой разворачивания
        desc_layout = QHBoxLayout()
        
        self.lbl_description = QLabel()
        self.lbl_description.setWordWrap(True)
        self.lbl_description.setFont(QFont("Calibri", 10))
        self.lbl_description.setTextInteractionFlags(Qt.TextSelectableByMouse)
        desc_layout.addWidget(self.lbl_description, stretch=1)

        self.btn_toggle_desc = QToolButton()
        self.btn_toggle_desc.setText("...")
        self.btn_toggle_desc.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.btn_toggle_desc.clicked.connect(self._toggle_description)
        desc_layout.addWidget(self.btn_toggle_desc)

        main_layout.addLayout(desc_layout)

        # Полное описание (скрыто по умолчанию)
        self.txt_full_description = QTextEdit()
        self.txt_full_description.setReadOnly(True)
        self.txt_full_description.setVisible(False)
        self.txt_full_description.setMaximumHeight(150)
        self.txt_full_description.setFont(QFont("Calibri", 10))
        main_layout.addWidget(self.txt_full_description)

        # Планируемый результат
        if self._result:
            result_layout = QVBoxLayout()
            self.lbl_result_title = QLabel("Планируемый результат:")
            self.lbl_result_title.setFont(QFont("Calibri", 10, QFont.Weight.Bold))
            result_layout.addWidget(self.lbl_result_title)
            
            self.lbl_result = QLabel(self._result)
            self.lbl_result.setWordWrap(True)
            self.lbl_result.setFont(QFont("Calibri", 10))
            self.lbl_result.setStyleSheet("color: #333333;")
            result_layout.addWidget(self.lbl_result)
            
            main_layout.addLayout(result_layout)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def _set_status_style(self):
        """Устанавливает стиль для статуса."""
        if self._status == 'завершён':
            self.lbl_status.setStyleSheet("color: green; font-weight: bold;")
        elif self._status == 'сейчас':
            self.lbl_status.setStyleSheet("color: blue; font-weight: bold;")
        else:  # планируется
            self.lbl_status.setStyleSheet("color: gray; font-weight: bold;")

    def _update_description_display(self):
        """Обновляет отображение описания."""
        if len(self._full_description) <= 150:
            self.lbl_description.setText(self._full_description)
            self.btn_toggle_desc.setVisible(False)
        else:
            truncated = self._full_description[:150]
            self.lbl_description.setText(truncated + "...")
            self.btn_toggle_desc.setVisible(True)

    def _toggle_description(self):
        """Переключает отображение полного описания."""
        self._is_expanded = not self._is_expanded
        if self._is_expanded:
            self.txt_full_description.setText(self._full_description)
            self.txt_full_description.setVisible(True)
            self.btn_toggle_desc.setText("▲")
        else:
            self.txt_full_description.setVisible(False)
            self.btn_toggle_desc.setText("...")

    @property
    def stage_id(self) -> int:
        """Возвращает ID этапа."""
        return self._stage_id

    @property
    def is_expanded(self) -> bool:
        """Возвращает состояние развернутого описания."""
        return self._is_expanded

    def set_status(self, status: str):
        """Устанавливает статус этапа."""
        self._status = status
        self.lbl_status.setText(status)
        self._set_status_style()
