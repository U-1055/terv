# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'workspace_settings_window.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget, QTextEdit)

class Ui_WorkspaceSettingsWindow(object):
    def setupUi(self, WorkspaceSettingsWindow):
        if not WorkspaceSettingsWindow.objectName():
            WorkspaceSettingsWindow.setObjectName(u"WorkspaceSettingsWindow")
        WorkspaceSettingsWindow.resize(600, 500)

        self.vertical_layout = QVBoxLayout(WorkspaceSettingsWindow)
        self.vertical_layout.setObjectName(u"vertical_layout")
        self.vertical_layout.setContentsMargins(20, 20, 20, 20)

        # Верхняя панель с кнопкой возврата
        self.top_panel_layout = QHBoxLayout()
        self.top_panel_layout.setObjectName(u"top_panel_layout")

        self.btn_back = QPushButton(WorkspaceSettingsWindow)
        self.btn_back.setObjectName(u"btn_back")
        self.btn_back.setMinimumSize(QSize(30, 30))
        self.btn_back.setMaximumSize(QSize(30, 30))
        self.top_panel_layout.addWidget(self.btn_back)

        self.lbl_title = QLabel(WorkspaceSettingsWindow)
        self.lbl_title.setObjectName(u"lbl_title")
        font = QFont("Calibri", 16, 75, False)
        self.lbl_title.setFont(font)
        self.top_panel_layout.addWidget(self.lbl_title)

        self.horizontal_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.top_panel_layout.addItem(self.horizontal_spacer)

        self.vertical_layout.addLayout(self.top_panel_layout)

        # Поля для редактирования
        self.form_layout = QVBoxLayout()
        self.form_layout.setObjectName(u"form_layout")

        # Название
        self.lbl_name_label = QLabel(WorkspaceSettingsWindow)
        self.lbl_name_label.setObjectName(u"lbl_name_label")
        self.form_layout.addWidget(self.lbl_name_label)

        self.text_edit_name = QTextEdit(WorkspaceSettingsWindow)
        self.text_edit_name.setObjectName(u"text_edit_name")
        self.text_edit_name.setMaximumSize(QSize(16777215, 80))
        self.form_layout.addWidget(self.text_edit_name)

        # Описание
        self.lbl_description_label = QLabel(WorkspaceSettingsWindow)
        self.lbl_description_label.setObjectName(u"lbl_description_label")
        self.form_layout.addWidget(self.lbl_description_label)

        self.text_edit_description = QTextEdit(WorkspaceSettingsWindow)
        self.text_edit_description.setObjectName(u"text_edit_description")
        self.form_layout.addWidget(self.text_edit_description)

        self.vertical_layout.addLayout(self.form_layout)

        # Кнопки подтверждения и отмены
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setObjectName(u"buttons_layout")

        self.horizontal_spacer_left = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.buttons_layout.addItem(self.horizontal_spacer_left)

        self.btn_cancel = QPushButton(WorkspaceSettingsWindow)
        self.btn_cancel.setObjectName(u"btn_cancel")
        self.btn_cancel.setMinimumSize(QSize(100, 35))
        self.buttons_layout.addWidget(self.btn_cancel)

        self.btn_confirm = QPushButton(WorkspaceSettingsWindow)
        self.btn_confirm.setObjectName(u"btn_confirm")
        self.btn_confirm.setMinimumSize(QSize(100, 35))
        self.btn_confirm.setEnabled(False)
        self.buttons_layout.addWidget(self.btn_confirm)

        self.horizontal_spacer_right = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.buttons_layout.addItem(self.horizontal_spacer_right)

        self.vertical_layout.addLayout(self.buttons_layout)

        self.retranslateUi(WorkspaceSettingsWindow)
        QMetaObject.connectSlotsByName(WorkspaceSettingsWindow)

    def retranslateUi(self, WorkspaceSettingsWindow):
        WorkspaceSettingsWindow.setWindowTitle(QCoreApplication.translate("WorkspaceSettingsWindow", u"Настройки рабочего пространства", None))
        self.btn_back.setText(QCoreApplication.translate("WorkspaceSettingsWindow", u"\u2190", None))
        self.lbl_title.setText(QCoreApplication.translate("WorkspaceSettingsWindow", u"Настройки", None))
        self.lbl_name_label.setText(QCoreApplication.translate("WorkspaceSettingsWindow", u"Название:", None))
        self.lbl_description_label.setText(QCoreApplication.translate("WorkspaceSettingsWindow", u"Описание:", None))
        self.btn_cancel.setText(QCoreApplication.translate("WorkspaceSettingsWindow", u"Отмена", None))
        self.btn_confirm.setText(QCoreApplication.translate("WorkspaceSettingsWindow", u"Сохранить", None))
