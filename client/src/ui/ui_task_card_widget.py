# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'task_card_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QDateTimeEdit, QFrame, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

class Ui_TaskCardWidget(object):
    def setupUi(self, TaskCardWidget):
        if not TaskCardWidget.objectName():
            TaskCardWidget.setObjectName(u"TaskCardWidget")
        TaskCardWidget.resize(400, 280)
        TaskCardWidget.setMinimumSize(QSize(0, 200))

        self.frame = QFrame(TaskCardWidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.frame.setGeometry(QRect(0, 0, 400, 280))

        self.main_layout = QVBoxLayout(self.frame)
        self.main_layout.setObjectName(u"main_layout")
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(6)

        # Верхняя строка: стрелка влево, троеточие, редактирование, стрелка вправо
        self.top_layout = QHBoxLayout()
        self.top_layout.setObjectName(u"top_layout")
        self.top_layout.setSpacing(4)

        self.btn_move_left = QPushButton(self.frame)
        self.btn_move_left.setObjectName(u"btn_move_left")
        self.btn_move_left.setMaximumSize(QSize(24, 24))
        self.btn_move_left.setMinimumSize(QSize(24, 24))
        self.top_layout.addWidget(self.btn_move_left)

        self.btn_view = QPushButton(self.frame)
        self.btn_view.setObjectName(u"btn_view")
        self.btn_view.setMaximumSize(QSize(24, 24))
        self.btn_view.setMinimumSize(QSize(24, 24))
        self.top_layout.addWidget(self.btn_view)

        self.btn_edit = QPushButton(self.frame)
        self.btn_edit.setObjectName(u"btn_edit")
        self.btn_edit.setMaximumSize(QSize(24, 24))
        self.btn_edit.setMinimumSize(QSize(24, 24))
        self.top_layout.addWidget(self.btn_edit)

        self.btn_move_right = QPushButton(self.frame)
        self.btn_move_right.setObjectName(u"btn_move_right")
        self.btn_move_right.setMaximumSize(QSize(24, 24))
        self.btn_move_right.setMinimumSize(QSize(24, 24))
        self.top_layout.addWidget(self.btn_move_right)

        self.top_layout.addStretch(1)

        self.main_layout.addLayout(self.top_layout)

        # Название задачи
        self.lbl_name = QLabel(self.frame)
        self.lbl_name.setObjectName(u"lbl_name")
        font = QFont("Calibri", 12, 75, False)
        self.lbl_name.setFont(font)
        self.lbl_name.setWordWrap(True)
        self.main_layout.addWidget(self.lbl_name)

        # Описание
        self.lbl_description = QLabel(self.frame)
        self.lbl_description.setObjectName(u"lbl_description")
        self.lbl_description.setWordWrap(True)
        self.main_layout.addWidget(self.lbl_description)

        # Поручил
        self.creator_layout = QHBoxLayout()
        self.creator_layout.setObjectName(u"creator_layout")

        self.lbl_creator_label = QLabel(self.frame)
        self.lbl_creator_label.setObjectName(u"lbl_creator_label")
        self.creator_layout.addWidget(self.lbl_creator_label)

        self.lbl_creator = QLabel(self.frame)
        self.lbl_creator.setObjectName(u"lbl_creator")
        self.creator_layout.addWidget(self.lbl_creator)

        self.creator_layout.addStretch(1)

        self.main_layout.addLayout(self.creator_layout)

        # Исполнитель
        self.executor_layout = QHBoxLayout()
        self.executor_layout.setObjectName(u"executor_layout")

        self.lbl_executor_label = QLabel(self.frame)
        self.lbl_executor_label.setObjectName(u"lbl_executor_label")
        self.executor_layout.addWidget(self.lbl_executor_label)

        self.lbl_executor = QLabel(self.frame)
        self.lbl_executor.setObjectName(u"lbl_executor")
        self.executor_layout.addWidget(self.lbl_executor)

        self.executor_layout.addStretch(1)

        self.main_layout.addLayout(self.executor_layout)

        # Взять в работу
        self.start_layout = QHBoxLayout()
        self.start_layout.setObjectName(u"start_layout")

        self.lbl_start_label = QLabel(self.frame)
        self.lbl_start_label.setObjectName(u"lbl_start_label")
        self.start_layout.addWidget(self.lbl_start_label)

        self.date_time_start = QDateTimeEdit(self.frame)
        self.date_time_start.setObjectName(u"date_time_start")
        self.date_time_start.setReadOnly(True)
        self.date_time_start.setButtonSymbols(QDateTimeEdit.ButtonSymbols.NoButtons)
        self.date_time_start.setCalendarPopup(False)
        self.start_layout.addWidget(self.date_time_start)

        self.start_layout.addStretch(1)

        self.main_layout.addLayout(self.start_layout)

        # Дедлайн
        self.deadline_layout = QHBoxLayout()
        self.deadline_layout.setObjectName(u"deadline_layout")

        self.lbl_deadline_label = QLabel(self.frame)
        self.lbl_deadline_label.setObjectName(u"lbl_deadline_label")
        self.deadline_layout.addWidget(self.lbl_deadline_label)

        self.date_time_deadline = QDateTimeEdit(self.frame)
        self.date_time_deadline.setObjectName(u"date_time_deadline")
        self.date_time_deadline.setReadOnly(True)
        self.date_time_deadline.setButtonSymbols(QDateTimeEdit.ButtonSymbols.NoButtons)
        self.date_time_deadline.setCalendarPopup(False)
        self.deadline_layout.addWidget(self.date_time_deadline)

        self.deadline_layout.addStretch(1)

        self.main_layout.addLayout(self.deadline_layout)

        self.retranslateUi(TaskCardWidget)
        QMetaObject.connectSlotsByName(TaskCardWidget)

    def retranslateUi(self, TaskCardWidget):
        TaskCardWidget.setWindowTitle(QCoreApplication.translate("TaskCardWidget", u"TaskCardWidget", None))
        self.btn_edit.setText(QCoreApplication.translate("TaskCardWidget", u"\u270E", None))
        self.btn_view.setText(QCoreApplication.translate("TaskCardWidget", u"\u22EE", None))
        self.btn_move_left.setText(QCoreApplication.translate("TaskCardWidget", u"\u2190", None))
        self.btn_move_right.setText(QCoreApplication.translate("TaskCardWidget", u"\u2192", None))
        self.lbl_creator_label.setText(QCoreApplication.translate("TaskCardWidget", u"Поручил:", None))
        self.lbl_executor_label.setText(QCoreApplication.translate("TaskCardWidget", u"Исполнитель:", None))
        self.lbl_start_label.setText(QCoreApplication.translate("TaskCardWidget", u"Взять в работу:", None))
        self.lbl_deadline_label.setText(QCoreApplication.translate("TaskCardWidget", u"Дедлайн:", None))
