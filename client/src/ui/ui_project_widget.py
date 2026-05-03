# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'project_widget.ui'
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
    QSizePolicy, QVBoxLayout, QWidget, QPushButton)

class Ui_ProjectWidget(object):
    def setupUi(self, ProjectWidget):
        if not ProjectWidget.objectName():
            ProjectWidget.setObjectName(u"ProjectWidget")
        ProjectWidget.resize(800, 120)
        ProjectWidget.setMinimumSize(QSize(0, 100))

        self.frame = QFrame(ProjectWidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.frame.setGeometry(QRect(0, 0, 800, 120))

        self.main_layout = QVBoxLayout(self.frame)
        self.main_layout.setObjectName(u"main_layout")
        self.main_layout.setContentsMargins(15, 10, 15, 10)

        # Верхняя строка с названием
        self.top_layout = QHBoxLayout()
        self.top_layout.setObjectName(u"top_layout")

        self.lbl_name = QLabel(self.frame)
        self.lbl_name.setObjectName(u"lbl_name")
        font = QFont("Calibri", 14, 75, False)
        self.lbl_name.setFont(font)
        self.top_layout.addWidget(self.lbl_name)

        self.lbl_stage = QLabel(self.frame)
        self.lbl_stage.setObjectName(u"lbl_stage")
        self.lbl_stage.setFont(QFont("Calibri", 11, 50, False))
        self.top_layout.addWidget(self.lbl_stage)

        self.top_layout.addStretch(1)

        self.btn_open = QPushButton(self.frame)
        self.btn_open.setObjectName(u"btn_open")
        self.btn_open.setMinimumSize(QSize(80, 30))
        self.btn_open.setMaximumSize(QSize(80, 30))
        self.top_layout.addWidget(self.btn_open)

        self.main_layout.addLayout(self.top_layout)

        # Средняя строка с наставником
        self.mentor_layout = QHBoxLayout()
        self.mentor_layout.setObjectName(u"mentor_layout")

        self.lbl_mentor_label = QLabel(self.frame)
        self.lbl_mentor_label.setObjectName(u"lbl_mentor_label")
        self.mentor_layout.addWidget(self.lbl_mentor_label)

        self.lbl_mentor = QLabel(self.frame)
        self.lbl_mentor.setObjectName(u"lbl_mentor")
        self.mentor_layout.addWidget(self.lbl_mentor)

        self.mentor_layout.addStretch(1)

        self.main_layout.addLayout(self.mentor_layout)

        # Нижняя строка со студентами
        self.students_layout = QHBoxLayout()
        self.students_layout.setObjectName(u"students_layout")

        self.lbl_students_label = QLabel(self.frame)
        self.lbl_students_label.setObjectName(u"lbl_students_label")
        self.students_layout.addWidget(self.lbl_students_label)

        self.lbl_students = QLabel(self.frame)
        self.lbl_students.setObjectName(u"lbl_students")
        self.lbl_students.setWordWrap(True)
        self.students_layout.addWidget(self.lbl_students)

        self.students_layout.addStretch(1)

        self.main_layout.addLayout(self.students_layout)

        self.retranslateUi(ProjectWidget)
        QMetaObject.connectSlotsByName(ProjectWidget)

    def retranslateUi(self, ProjectWidget):
        ProjectWidget.setWindowTitle(QCoreApplication.translate("ProjectWidget", u"ProjectWidget", None))
        self.btn_open.setText(QCoreApplication.translate("ProjectWidget", u"Открыть", None))
        self.lbl_stage.setText(u"Этап: ...")
        self.lbl_mentor_label.setText(u"Наставник:")
        self.lbl_mentor.setText(u"")
        self.lbl_students_label.setText(u"Студенты:")
        self.lbl_students.setText(u"")
