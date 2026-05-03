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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

class Ui_TaskCardWidget(object):
    def setupUi(self, TaskCardWidget):
        if not TaskCardWidget.objectName():
            TaskCardWidget.setObjectName(u"TaskCardWidget")
        TaskCardWidget.resize(400, 200)
        TaskCardWidget.setMinimumSize(QSize(0, 150))

        self.frame = QFrame(TaskCardWidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.frame.setGeometry(QRect(0, 0, 400, 200))

        self.main_layout = QVBoxLayout(self.frame)
        self.main_layout.setObjectName(u"main_layout")
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Верхняя строка с названием и кнопками
        self.top_layout = QHBoxLayout()
        self.top_layout.setObjectName(u"top_layout")

        self.lbl_name = QLabel(self.frame)
        self.lbl_name.setObjectName(u"lbl_name")
        font = QFont("Calibri", 12, 75, False)
        self.lbl_name.setFont(font)
        self.lbl_name.setWordWrap(True)
        self.top_layout.addWidget(self.lbl_name)

        self.btn_move_left = QPushButton(self.frame)
        self.btn_move_left.setObjectName(u"btn_move_left")
        self.btn_move_left.setMaximumSize(QSize(30, 30))
        self.top_layout.addWidget(self.btn_move_left)

        self.btn_edit = QPushButton(self.frame)
        self.btn_edit.setObjectName(u"btn_edit")
        self.btn_edit.setMinimumSize(QSize(80, 25))
        self.btn_edit.setMaximumSize(QSize(80, 25))
        self.top_layout.addWidget(self.btn_edit)

        self.btn_move_right = QPushButton(self.frame)
        self.btn_move_right.setObjectName(u"btn_move_right")
        self.btn_move_right.setMaximumSize(QSize(30, 30))
        self.top_layout.addWidget(self.btn_move_right)

        self.main_layout.addLayout(self.top_layout)

        # Описание
        self.lbl_description = QLabel(self.frame)
        self.lbl_description.setObjectName(u"lbl_description")
        self.lbl_description.setWordWrap(True)
        self.main_layout.addWidget(self.lbl_description)

        # Исполнитель
        self.lbl_executor_layout = QHBoxLayout()
        self.lbl_executor_layout.setObjectName(u"lbl_executor_layout")

        self.lbl_executor_label = QLabel(self.frame)
        self.lbl_executor_label.setObjectName(u"lbl_executor_label")
        self.lbl_executor_layout.addWidget(self.lbl_executor_label)

        self.lbl_executor = QLabel(self.frame)
        self.lbl_executor.setObjectName(u"lbl_executor")
        self.lbl_executor_layout.addWidget(self.lbl_executor)

        self.lbl_executor_layout.addStretch(1)

        self.main_layout.addLayout(self.lbl_executor_layout)

        # Дедлайн
        self.lbl_deadline_layout = QHBoxLayout()
        self.lbl_deadline_layout.setObjectName(u"lbl_deadline_layout")

        self.lbl_deadline_label = QLabel(self.frame)
        self.lbl_deadline_label.setObjectName(u"lbl_deadline_label")
        self.lbl_deadline_layout.addWidget(self.lbl_deadline_label)

        self.lbl_deadline = QLabel(self.frame)
        self.lbl_deadline.setObjectName(u"lbl_deadline")
        self.lbl_deadline_layout.addWidget(self.lbl_deadline)

        self.lbl_deadline_layout.addStretch(1)

        self.main_layout.addLayout(self.lbl_deadline_layout)

        self.retranslateUi(TaskCardWidget)
        QMetaObject.connectSlotsByName(TaskCardWidget)

    def retranslateUi(self, TaskCardWidget):
        TaskCardWidget.setWindowTitle(QCoreApplication.translate("TaskCardWidget", u"TaskCardWidget", None))
        self.btn_move_left.setText(QCoreApplication.translate("TaskCardWidget", u"\u2190", None))
        self.btn_edit.setText(QCoreApplication.translate("TaskCardWidget", u"Edit", None))
        self.btn_move_right.setText(QCoreApplication.translate("TaskCardWidget", u"\u2192", None))
        self.lbl_executor_label.setText(QCoreApplication.translate("TaskCardWidget", u"Исполнитель:", None))
        self.lbl_deadline_label.setText(QCoreApplication.translate("TaskCardWidget", u"Дедлайн:", None))
