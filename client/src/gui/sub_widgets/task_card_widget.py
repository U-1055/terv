"""Виджет карточки задачи."""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QFrame, QDateTimeEdit
from PySide6.QtCore import Signal, Qt, QDateTime
from PySide6.QtGui import QFont

from client.src.ui.ui_task_card_widget import Ui_TaskCardWidget


class TaskCardWidget(QWidget):
    """
    Виджет карточки задачи.

    :param task_id: ID задачи.
    :param name: Название задачи.
    :param description: Описание задачи.
    :param creator_email: Email пользователя, поручившего задачу.
    :param executor_email: Email исполнителя.
    :param plan_start: Плановая дата взятия в работу.
    :param plan_deadline: Планируемый дедлайн.
    :param status_id: ID текущего статуса задачи.
    """

    edit_pressed = Signal(int)
    view_pressed = Signal(int)
    move_left_pressed = Signal(int)
    move_right_pressed = Signal(int)

    def __init__(self, task_id: int, name: str, description: str,
                 creator_email: str, executor_email: str,
                 plan_start: str, plan_deadline: str, status_id: int,
                 parent=None):
        super().__init__(parent)

        self._task_id = task_id
        self._status_id = status_id

        self._view = Ui_TaskCardWidget()
        self._view.setupUi(self)

        # Установка текста
        self._view.lbl_name.setText(name)
        self._view.lbl_description.setText(description)
        self._view.lbl_creator.setText(creator_email)
        self._view.lbl_executor.setText(executor_email)

        # Настройка дат
        self._setup_date(self._view.date_time_start, plan_start)
        self._setup_date(self._view.date_time_deadline, plan_deadline)

        # Шрифты и стили
        self._setup_fonts()

        # Подключение сигналов
        self._view.btn_edit.clicked.connect(lambda: self.edit_pressed.emit(self._task_id))
        self._view.btn_view.clicked.connect(lambda: self.view_pressed.emit(self._task_id))
        self._view.btn_move_left.clicked.connect(lambda: self.move_left_pressed.emit(self._task_id))
        self._view.btn_move_right.clicked.connect(lambda: self.move_right_pressed.emit(self._task_id))

        # Скрытие кнопок перемещения для крайних статусов
        self._update_move_buttons()

    def _setup_date(self, widget: QDateTimeEdit, date_str: str):
        """Устанавливает дату в QDateTimeEdit."""
        print(f'DATE: {date_str}')
        if date_str and date_str != 'Не указан':
            dt = self._parse_date_string(date_str)
            if dt.isValid():
                widget.setDateTime(dt)
                widget.setDisplayFormat('dd.MM.yyyy HH:mm')
            else:
                widget.setSpecialValueText('Не указан')
                widget.setEnabled(False)

        else:
            widget.setSpecialValueText('Не указан')
            widget.setEnabled(False)

    def _parse_date_string(self, date_str: str) -> QDateTime:
        """
        Парсит строку даты в QDateTime с поддержкой нескольких форматов.

        :param date_str: Строка даты для парсинга.
        :return: QDateTime объект или невалидный QDateTime если парсинг не удался.
        """
        if not date_str:
            return QDateTime()

        # Список форматов для попытки парсинга
        date_formats = [
            Qt.ISODate,                        # 2024-01-15T10:30:00
            'yyyy-MM-dd HH:mm:ss',             # 2024-01-15 10:30:00
            'yyyy-MM-dd HH:mm:ss.zzz',         # 2024-01-15 10:30:00.123
            'yyyy-MM-dd',                       # 2024-01-15
            'dd.MM.yyyy HH:mm:ss',              # 15.01.2024 10:30:00
            'dd.MM.yyyy HH:mm',                 # 15.01.2024 10:30
            'dd.MM.yyyy',                       # 15.01.2024
        ]

        for date_format in date_formats:
            dt = QDateTime.fromString(date_str, date_format)
            if dt.isValid():
                return dt

        # Если ни один формат не подошел, возвращаем невалидный
        return QDateTime()

    def _setup_fonts(self):
        """Настраивает шрифты элементов карточки."""
        from client.src.base import GUIStyles

        # Названия полей — жирным
        label_widgets = [
            self._view.lbl_creator_label,
            self._view.lbl_executor_label,
            self._view.lbl_start_label,
            self._view.lbl_deadline_label,
        ]
        for lbl in label_widgets:
            lbl.setFont(GUIStyles.bold_font)

        # Описание — мелким шрифтом
        small_font = QFont('Calibri', 10)
        self._view.lbl_description.setFont(small_font)

        # Остальные поля — базовый шрифт
        self._view.lbl_name.setFont(GUIStyles.base_font)
        self._view.lbl_creator.setFont(GUIStyles.base_font)
        self._view.lbl_executor.setFont(GUIStyles.base_font)

    def _update_move_buttons(self):
        """Обновляет состояние кнопок перемещения в зависимости от статуса."""
        # Стрелка влево неактивна для статуса "Запланировано" (1)
        self._view.btn_move_left.setEnabled(self._status_id > 1)
        # Стрелка вправо всегда активна (циклическое переключение 5 -> 1)
        self._view.btn_move_right.setEnabled(True)

    def set_status(self, status_id: int):
        """
        Устанавливает новый статус задачи.

        :param status_id: Новый ID статуса.
        """
        self._status_id = status_id
        self._update_move_buttons()

    def task_id(self) -> int:
        """Возвращает ID задачи."""
        return self._task_id

    def status_id(self) -> int:
        """Возвращает текущий статус задачи."""
        return self._status_id

    def set_status_id(self, status_id: int):
        """Устанавливает ID статуса задачи."""
        self._status_id = status_id
        self._update_move_buttons()
