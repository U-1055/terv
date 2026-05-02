# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'workspace_widget.ui'
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

class Ui_WorkspaceWidget(object):
    def setupUi(self, WorkspaceWidget):
        if not WorkspaceWidget.objectName():
            WorkspaceWidget.setObjectName(u"WorkspaceWidget")
        WorkspaceWidget.resize(800, 100)
        WorkspaceWidget.setMinimumSize(QSize(0, 80))
        
        # Основной фрейм с границей
        self.frame = QFrame(WorkspaceWidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.frame.setGeometry(QRect(0, 0, 800, 100))
        
        self.main_layout = QVBoxLayout(self.frame)
        self.main_layout.setObjectName(u"main_layout")
        self.main_layout.setContentsMargins(15, 10, 15, 10)
        
        # Верхняя строка с названием и описанием
        self.top_layout = QHBoxLayout()
        self.top_layout.setObjectName(u"top_layout")
        
        self.lbl_name = QLabel(self.frame)
        self.lbl_name.setObjectName(u"lbl_name")
        font = QFont("Calibri", 14, 75, False)
        self.lbl_name.setFont(font)
        self.top_layout.addWidget(self.lbl_name)

        self.top_layout.addStretch(1)

        self.btn_open = QPushButton(self.frame)
        self.btn_open.setObjectName(u"btn_open")
        self.btn_open.setMinimumSize(QSize(80, 30))
        self.btn_open.setMaximumSize(QSize(80, 30))
        self.top_layout.addWidget(self.btn_open)

        self.main_layout.addLayout(self.top_layout)
        
        # Нижняя строка с описанием
        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.setObjectName(u"bottom_layout")
        
        self.lbl_description = QLabel(self.frame)
        self.lbl_description.setObjectName(u"lbl_description")
        self.lbl_description.setWordWrap(True)
        self.bottom_layout.addWidget(self.lbl_description)
        
        self.bottom_layout.addStretch(1)
        
        self.main_layout.addLayout(self.bottom_layout)
        
        self.retranslateUi(WorkspaceWidget)
        QMetaObject.connectSlotsByName(WorkspaceWidget)

    def retranslateUi(self, WorkspaceWidget):
        WorkspaceWidget.setWindowTitle(QCoreApplication.translate("WorkspaceWidget", u"WorkspaceWidget", None))
        self.btn_open.setText(QCoreApplication.translate("WorkspaceWidget", u"Открыть", None))
