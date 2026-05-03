"""Модальное окно создания/редактирования задачи."""
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Signal, QDateTime

from client.src.ui.ui_task_dialog import Ui_TaskDialog


class TaskDialogWindow(QDialog):
    """
    Модальное окно для создания или редактирования задачи.
    
    :param task_id: ID задачи (None для создания новой).
    :param name: Название задачи.
    :param description: Описание задачи.
    :param executor_email: Email исполнителя.
    :param plan_start: Планируемая дата взятия в работу.
    :param plan_deadline: Планируемый дедлайн.
    :param executors: Список доступных исполнителей (email, user_id).
    """
    
    try_save_pressed = Signal()  # Сигнал при попытке сохранения. Обработчик валидирует поля.

    def __init__(self, task_id: int | None = None, name: str = "", 
                 description: str = "", executor_email: str = "",
                 plan_start: QDateTime | None = None,
                 plan_deadline: QDateTime | None = None,
                 executors: list[tuple[str, int]] | None = None,
                 parent=None):
        super().__init__(parent)
        
        self._task_id = task_id
        self._executors = executors or []
        
        self._view = Ui_TaskDialog()
        self._view.setupUi(self)
        
        # Установка начальных значений
        self._view.line_edit_name.setText(name)
        self._view.text_edit_description.setText(description)
        
        # Заполнение комбобокса исполнителей
        if executors:
            for email, user_id in executors:
                self._view.combobox_executor.addItem(email, user_id)
            
            # Установка выбранного исполнителя
            if executor_email:
                for i in range(self._view.combobox_executor.count()):
                    if self._view.combobox_executor.itemText(i) == executor_email:
                        self._view.combobox_executor.setCurrentIndex(i)
                        break
        
        # Установка дат
        if plan_start:
            self._view.date_time_plan_start.setDateTime(plan_start)
        else:
            self._view.date_time_plan_start.setDateTime(QDateTime.currentDateTime())
        
        if plan_deadline:
            self._view.date_time_plan_deadline.setDateTime(plan_deadline)
        else:
            self._view.date_time_plan_deadline.setDateTime(QDateTime.currentDateTime().addSecs(24 * 3600))

        # Подключение сигналов
        self._view.btn_save.clicked.connect(self._on_btn_save_pressed)
        self._view.btn_cancel.clicked.connect(self._on_btn_cancel_pressed)
    
    def _on_btn_save_pressed(self):
        """Обработка нажатия кнопки сохранения. Испускает try_save_pressed для валидации в обработчике."""
        self.try_save_pressed.emit()

    def get_task_data(self) -> dict:
        """
        Собирает и возвращает данные задачи из полей формы.

        :return: Словарь с данными задачи.
        """
        name = self._view.line_edit_name.text().strip()
        description = self._view.text_edit_description.toPlainText().strip()
        executor_email = self._view.combobox_executor.currentText()
        executor_id = self._view.combobox_executor.currentData()
        plan_start = self._view.date_time_plan_start.dateTime()
        plan_deadline = self._view.date_time_plan_deadline.dateTime()
        
        return {
            'name': name,
            'description': description,
            'executor_email': executor_email,
            'executor_id': executor_id,
            'plan_start': plan_start.toString('yyyy-MM-dd HH:mm:ss'),
            'plan_deadline': plan_deadline.toString('yyyy-MM-dd HH:mm:ss')
        }

    def _on_btn_cancel_pressed(self):
        """Обработка нажатия кнопки отмены."""
        self.reject()
    
    def set_readonly(self, readonly: bool):
        """
        Устанавливает режим только для чтения.
        
        :param readonly: Режим только для чтения.
        """
        self._view.line_edit_name.setReadOnly(readonly)
        self._view.text_edit_description.setReadOnly(readonly)
        self._view.combobox_executor.setEnabled(not readonly)
        self._view.date_time_plan_start.setReadOnly(readonly)
        self._view.date_time_plan_deadline.setReadOnly(readonly)
        self._view.btn_save.setVisible(not readonly)
