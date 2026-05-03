"""Виджет карточки задачи."""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QFrame
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont

from client.src.ui.ui_task_card_widget import Ui_TaskCardWidget


class TaskCardWidget(QWidget):
    """
    Виджет карточки задачи.
    
    :param task_id: ID задачи.
    :param name: Название задачи.
    :param description: Описание задачи.
    :param executor_email: Email исполнителя.
    :param plan_deadline: Планируемый дедлайн.
    :param status_id: ID статуса задачи.
    """
    
    edit_pressed = Signal(int)  # Сигнал при нажатии кнопки редактирования
    move_left_pressed = Signal(int)  # Сигнал при нажатии кнопки перемещения влево
    move_right_pressed = Signal(int)  # Сигнал при нажатии кнопки перемещения вправо
    
    def __init__(self, task_id: int, name: str, description: str,
                 executor_email: str, plan_deadline: str, status_id: int):
        super().__init__()
        self._task_id = task_id
        self._name = name
        self._description = description
        self._executor_email = executor_email
        self._plan_deadline = plan_deadline
        self._status_id = status_id
        
        self._view = Ui_TaskCardWidget()
        self._view.setupUi(self)
        
        # Установка текста
        self._view.lbl_name.setText(name)
        self._view.lbl_description.setText(description if description else "Описание отсутствует")
        self._view.lbl_executor.setText(executor_email if executor_email else "Не назначен")
        self._view.lbl_deadline.setText(plan_deadline if plan_deadline else "Не указан")
        
        # Настройка видимости кнопок перемещения в зависимости от статуса
        # Статусы: 1 - Запланировано, 2 - В работе, 3 - Проверяется, 4 - Выполнено, 5 - Доработать
        self._view.btn_move_left.setVisible(status_id > 1)
        self._view.btn_move_right.setVisible(status_id < 5)
        
        # Подключение сигналов
        self._view.btn_edit.clicked.connect(self._on_btn_edit_pressed)
        self._view.btn_move_left.clicked.connect(self._on_btn_move_left_pressed)
        self._view.btn_move_right.clicked.connect(self._on_btn_move_right_pressed)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def _on_btn_edit_pressed(self):
        """Обработка нажатия кнопки редактирования."""
        self.edit_pressed.emit(self._task_id)
    
    def _on_btn_move_left_pressed(self):
        """Обработка нажатия кнопки перемещения влево."""
        self.move_left_pressed.emit(self._task_id)
    
    def _on_btn_move_right_pressed(self):
        """Обработка нажатия кнопки перемещения вправо."""
        self.move_right_pressed.emit(self._task_id)
    
    def task_id(self) -> int:
        """Возвращает ID задачи."""
        return self._task_id
    
    def name(self) -> str:
        """Возвращает название задачи."""
        return self._view.lbl_name.text()
    
    def set_name(self, name: str):
        """Устанавливает название задачи."""
        self._name = name
        self._view.lbl_name.setText(name)
    
    def description(self) -> str:
        """Возвращает описание задачи."""
        return self._view.lbl_description.text()
    
    def set_description(self, description: str):
        """Устанавливает описание задачи."""
        self._description = description
        self._view.lbl_description.setText(description if description else "Описание отсутствует")
    
    def executor_email(self) -> str:
        """Возвращает email исполнителя."""
        return self._view.lbl_executor.text()
    
    def set_executor_email(self, executor_email: str):
        """Устанавливает email исполнителя."""
        self._executor_email = executor_email
        self._view.lbl_executor.setText(executor_email if executor_email else "Не назначен")
    
    def plan_deadline(self) -> str:
        """Возвращает планируемый дедлайн."""
        return self._view.lbl_deadline.text()
    
    def set_plan_deadline(self, plan_deadline: str):
        """Устанавливает планируемый дедлайн."""
        self._plan_deadline = plan_deadline
        self._view.lbl_deadline.setText(plan_deadline if plan_deadline else "Не указан")
    
    def status_id(self) -> int:
        """Возвращает ID статуса задачи."""
        return self._status_id
    
    def set_status_id(self, status_id: int):
        """Устанавливает ID статуса задачи."""
        self._status_id = status_id
        # Обновляем видимость кнопок перемещения
        self._view.btn_move_left.setVisible(status_id > 1)
        self._view.btn_move_right.setVisible(status_id < 5)
