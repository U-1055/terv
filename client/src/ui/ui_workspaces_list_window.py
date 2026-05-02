# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'workspaces_list_window.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView,
    QLineEdit, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_WorkspacesListWindow(object):
    def setupUi(self, WorkspacesListWindow):
        if not WorkspacesListWindow.objectName():
            WorkspacesListWindow.setObjectName(u"WorkspacesListWindow")
        WorkspacesListWindow.resize(1024, 768)

        self.vertical_layout = QVBoxLayout(WorkspacesListWindow)
        self.vertical_layout.setObjectName(u"vertical_layout")

        # Строка поиска с кнопками
        self.search_layout = QHBoxLayout()
        self.search_layout.setObjectName(u"search_layout")

        self.horizontal_spacer_left = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.search_layout.addItem(self.horizontal_spacer_left)

        self.line_edit_search = QLineEdit(WorkspacesListWindow)
        self.line_edit_search.setObjectName(u"line_edit_search")
        self.line_edit_search.setPlaceholderText(u"Поиск рабочих пространств...")
        size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        self.line_edit_search.setSizePolicy(size_policy)
        self.line_edit_search.setMaximumSize(QSize(400, 16777215))
        self.search_layout.addWidget(self.line_edit_search)

        self.btn_search = QPushButton(WorkspacesListWindow)
        self.btn_search.setObjectName(u"btn_search")
        self.btn_search.setMinimumSize(QSize(80, 0))
        self.search_layout.addWidget(self.btn_search)

        self.btn_reset = QPushButton(WorkspacesListWindow)
        self.btn_reset.setObjectName(u"btn_reset")
        self.btn_reset.setMinimumSize(QSize(80, 0))
        self.btn_reset.setEnabled(False)
        self.search_layout.addWidget(self.btn_reset)

        self.horizontal_spacer_right = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.search_layout.addItem(self.horizontal_spacer_right)

        self.vertical_layout.addLayout(self.search_layout)

        # Область прокрутки для виджетов рабочих пространств
        self.scroll_area = QScrollArea(WorkspacesListWindow)
        self.scroll_area.setObjectName(u"scroll_area")
        self.scroll_area.setWidgetResizable(True)
        
        self.scroll_area_widget_contents = QWidget()
        self.scroll_area_widget_contents.setObjectName(u"scroll_area_widget_contents")
        self.scroll_area_widget_contents.setGeometry(QRect(0, 0, 1006, 680))
        
        self.scroll_area_contents_layout = QVBoxLayout(self.scroll_area_widget_contents)
        self.scroll_area_contents_layout.setObjectName(u"scroll_area_contents_layout")
        self.scroll_area_contents_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.workspaces_container = QWidget()
        self.workspaces_container.setObjectName(u"workspaces_container")
        self.workspaces_layout = QVBoxLayout(self.workspaces_container)
        self.workspaces_layout.setObjectName(u"workspaces_layout")
        self.workspaces_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area_contents_layout.addWidget(self.workspaces_container)
        
        self.scroll_area.setWidget(self.scroll_area_widget_contents)
        self.vertical_layout.addWidget(self.scroll_area, 10)

        self.retranslateUi(WorkspacesListWindow)
        QMetaObject.connectSlotsByName(WorkspacesListWindow)

    def retranslateUi(self, WorkspacesListWindow):
        WorkspacesListWindow.setWindowTitle(QCoreApplication.translate("WorkspacesListWindow", u"Рабочие пространства", None))
        self.btn_search.setText(QCoreApplication.translate("WorkspacesListWindow", u"Найти", None))
        self.btn_reset.setText(QCoreApplication.translate("WorkspacesListWindow", u"Сброс", None))
