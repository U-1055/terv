# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'task_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDateTimeEdit,
    QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget, QTextEdit, QLineEdit)

class Ui_TaskDialog(object):
    def setupUi(self, TaskDialog):
        if not TaskDialog.objectName():
            TaskDialog.setObjectName(u"TaskDialog")
        TaskDialog.resize(600, 700)

        self.vertical_layout = QVBoxLayout(TaskDialog)
        self.vertical_layout.setObjectName(u"vertical_layout")
        self.vertical_layout.setContentsMargins(20, 20, 20, 20)

        # Название задачи
        self.lbl_name = QLabel(TaskDialog)
        self.lbl_name.setObjectName(u"lbl_name")
        self.vertical_layout.addWidget(self.lbl_name)

        self.line_edit_name = QLineEdit(TaskDialog)
        self.line_edit_name.setObjectName(u"line_edit_name")
        self.vertical_layout.addWidget(self.line_edit_name)

        # Описание
        self.lbl_description = QLabel(TaskDialog)
        self.lbl_description.setObjectName(u"lbl_description")
        self.vertical_layout.addWidget(self.lbl_description)

        self.text_edit_description = QTextEdit(TaskDialog)
        self.text_edit_description.setObjectName(u"text_edit_description")
        self.text_edit_description.setMaximumSize(QSize(16777215, 150))
        self.vertical_layout.addWidget(self.text_edit_description)

        # Исполнитель
        self.lbl_executor = QLabel(TaskDialog)
        self.lbl_executor.setObjectName(u"lbl_executor")
        self.vertical_layout.addWidget(self.lbl_executor)

        self.combobox_executor = QComboBox(TaskDialog)
        self.combobox_executor.setObjectName(u"combobox_executor")
        self.vertical_layout.addWidget(self.combobox_executor)

        # Планируемая дата взятия в работу
        self.lbl_plan_start = QLabel(TaskDialog)
        self.lbl_plan_start.setObjectName(u"lbl_plan_start")
        self.vertical_layout.addWidget(self.lbl_plan_start)

        self.date_time_plan_start = QDateTimeEdit(TaskDialog)
        self.date_time_plan_start.setObjectName(u"date_time_plan_start")
        self.date_time_plan_start.setCalendarPopup(True)
        self.vertical_layout.addWidget(self.date_time_plan_start)

        # Планируемый дедлайн
        self.lbl_plan_deadline = QLabel(TaskDialog)
        self.lbl_plan_deadline.setObjectName(u"lbl_plan_deadline")
        self.vertical_layout.addWidget(self.lbl_plan_deadline)

        self.date_time_plan_deadline = QDateTimeEdit(TaskDialog)
        self.date_time_plan_deadline.setObjectName(u"date_time_plan_deadline")
        self.date_time_plan_deadline.setCalendarPopup(True)
        self.vertical_layout.addWidget(self.date_time_plan_deadline)

        # Кнопки
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setObjectName(u"buttons_layout")

        self.horizontal_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.buttons_layout.addItem(self.horizontal_spacer)

        self.btn_cancel = QPushButton(TaskDialog)
        self.btn_cancel.setObjectName(u"btn_cancel")
        self.btn_cancel.setMinimumSize(QSize(100, 35))
        self.buttons_layout.addWidget(self.btn_cancel)

        self.btn_save = QPushButton(TaskDialog)
        self.btn_save.setObjectName(u"btn_save")
        self.btn_save.setMinimumSize(QSize(100, 35))
        self.buttons_layout.addWidget(self.btn_save)

        self.vertical_layout.addLayout(self.buttons_layout)

        self.retranslateUi(TaskDialog)
        QMetaObject.connectSlotsByName(TaskDialog)

    def retranslateUi(self, TaskDialog):
        TaskDialog.setWindowTitle(QCoreApplication.translate("TaskDialog", u"Задача", None))
        self.lbl_name.setText(QCoreApplication.translate("TaskDialog", u"Название задачи:", None))
        self.lbl_description.setText(QCoreApplication.translate("TaskDialog", u"Описание:", None))
        self.lbl_executor.setText(QCoreApplication.translate("TaskDialog", u"Исполнитель:", None))
        self.lbl_plan_start.setText(QCoreApplication.translate("TaskDialog", u"Планируемая дата взятия в работу:", None))
        self.lbl_plan_deadline.setText(QCoreApplication.translate("TaskDialog", u"Планируемый дедлайн:", None))
        self.btn_cancel.setText(QCoreApplication.translate("TaskDialog", u"Отмена", None))
        self.btn_save.setText(QCoreApplication.translate("TaskDialog", u"Сохранить", None))
