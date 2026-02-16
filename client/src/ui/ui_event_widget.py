# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'event_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLayout,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(244, 47)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.lbl_title = QLabel(Form)
        self.lbl_title.setObjectName(u"lbl_title")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lbl_title.sizePolicy().hasHeightForWidth())
        self.lbl_title.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.lbl_title, 0, Qt.AlignHCenter)

        self.lbl_start_end = QLabel(Form)
        self.lbl_start_end.setObjectName(u"lbl_start_end")
        sizePolicy1.setHeightForWidth(self.lbl_start_end.sizePolicy().hasHeightForWidth())
        self.lbl_start_end.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.lbl_start_end)

        self.btn_show_details = QPushButton(Form)
        self.btn_show_details.setObjectName(u"btn_show_details")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.btn_show_details.sizePolicy().hasHeightForWidth())
        self.btn_show_details.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.btn_show_details)

        self.horizontalLayout.setStretch(0, 5)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalLayout.setStretch(0, 2)

        self.verticalLayout_2.addLayout(self.verticalLayout)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.lbl_title.setText(QCoreApplication.translate("Form", u"TextLabel", None))
        self.lbl_start_end.setText(QCoreApplication.translate("Form", u"TextLabel", None))
        self.btn_show_details.setText(QCoreApplication.translate("Form", u"PushButton", None))
    # retranslateUi

