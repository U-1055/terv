# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLayout, QPushButton,
    QSizePolicy, QStackedWidget, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1093, 749)
        self.horizontalLayout_3 = QHBoxLayout(Form)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.btn_userspace = QPushButton(Form)
        self.btn_userspace.setObjectName(u"btn_userspace")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_userspace.sizePolicy().hasHeightForWidth())
        self.btn_userspace.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.btn_userspace)

        self.btn_worspaces = QPushButton(Form)
        self.btn_worspaces.setObjectName(u"btn_worspaces")
        sizePolicy.setHeightForWidth(self.btn_worspaces.sizePolicy().hasHeightForWidth())
        self.btn_worspaces.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.btn_worspaces)

        self.btn_calendar = QPushButton(Form)
        self.btn_calendar.setObjectName(u"btn_calendar")
        sizePolicy.setHeightForWidth(self.btn_calendar.sizePolicy().hasHeightForWidth())
        self.btn_calendar.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.btn_calendar)

        self.btn_tasks = QPushButton(Form)
        self.btn_tasks.setObjectName(u"btn_tasks")
        sizePolicy.setHeightForWidth(self.btn_tasks.sizePolicy().hasHeightForWidth())
        self.btn_tasks.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.btn_tasks)

        self.btn_settings = QPushButton(Form)
        self.btn_settings.setObjectName(u"btn_settings")
        sizePolicy.setHeightForWidth(self.btn_settings.sizePolicy().hasHeightForWidth())
        self.btn_settings.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.btn_settings)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SetDefaultConstraint)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(2, 1)
        self.verticalLayout.setStretch(3, 1)
        self.verticalLayout.setStretch(4, 1)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.wdg_window = QStackedWidget(Form)
        self.wdg_window.setObjectName(u"wdg_window")
        self.wdg_windowPage1 = QWidget()
        self.wdg_windowPage1.setObjectName(u"wdg_windowPage1")
        self.wdg_window.addWidget(self.wdg_windowPage1)

        self.horizontalLayout.addWidget(self.wdg_window)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 24)

        self.horizontalLayout_3.addLayout(self.horizontalLayout)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.btn_userspace.setText(QCoreApplication.translate("Form", u"PushButton", None))
        self.btn_worspaces.setText(QCoreApplication.translate("Form", u"PushButton", None))
        self.btn_calendar.setText(QCoreApplication.translate("Form", u"PushButton", None))
        self.btn_tasks.setText(QCoreApplication.translate("Form", u"PushButton", None))
        self.btn_settings.setText(QCoreApplication.translate("Form", u"PushButton", None))
    # retranslateUi

