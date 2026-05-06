# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'workspace_window.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QTabWidget,
    QVBoxLayout, QWidget, QComboBox)

class Ui_WorkspaceWindow(object):
    def setupUi(self, WorkspaceWindow):
        if not WorkspaceWindow.objectName():
            WorkspaceWindow.setObjectName(u"WorkspaceWindow")
        WorkspaceWindow.resize(1024, 768)

        self.vertical_layout = QVBoxLayout(WorkspaceWindow)
        self.vertical_layout.setObjectName(u"vertical_layout")
        self.vertical_layout.setContentsMargins(10, 10, 10, 10)

        # Верхняя панель с кнопкой возврата
        self.top_panel_layout = QHBoxLayout()
        self.top_panel_layout.setObjectName(u"top_panel_layout")

        self.btn_back = QPushButton(WorkspaceWindow)
        self.btn_back.setObjectName(u"btn_back")
        self.btn_back.setMinimumSize(QSize(30, 30))
        self.btn_back.setMaximumSize(QSize(30, 30))
        self.top_panel_layout.addWidget(self.btn_back)

        self.horizontal_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.top_panel_layout.addItem(self.horizontal_spacer)

        self.vertical_layout.addLayout(self.top_panel_layout)

        # Вкладки
        self.tab_widget = QTabWidget(WorkspaceWindow)
        self.tab_widget.setObjectName(u"tab_widget")

        # Вкладка "Проекты"
        self.tab_projects = QWidget()
        self.tab_projects.setObjectName(u"tab_projects")
        self.projects_layout = QVBoxLayout(self.tab_projects)
        self.projects_layout.setObjectName(u"projects_layout")

        self.scroll_area_projects = QScrollArea(self.tab_projects)
        self.scroll_area_projects.setObjectName(u"scroll_area_projects")
        self.scroll_area_projects.setWidgetResizable(True)

        self.scroll_area_projects_contents = QWidget()
        self.scroll_area_projects_contents.setObjectName(u"scroll_area_projects_contents")
        self.scroll_area_projects_contents.setGeometry(QRect(0, 0, 1000, 700))

        self.projects_container_layout = QVBoxLayout(self.scroll_area_projects_contents)
        self.projects_container_layout.setObjectName(u"projects_container_layout")
        self.projects_container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area_projects.setWidget(self.scroll_area_projects_contents)
        self.projects_layout.addWidget(self.scroll_area_projects)

        self.tab_widget.addTab(self.tab_projects, u"Проекты")

        # Вкладка "Аналитика"
        self.tab_analytics = QWidget()
        self.tab_analytics.setObjectName(u"tab_analytics")
        self.analytics_layout = QVBoxLayout(self.tab_analytics)
        self.analytics_layout.setObjectName(u"analytics_layout")

        self.analytics_combobox_layout = QHBoxLayout()
        self.analytics_combobox_layout.setObjectName(u"analytics_combobox_layout")

        self.lbl_analytics_project = QLabel(self.tab_analytics)
        self.lbl_analytics_project.setObjectName(u"lbl_analytics_project")
        self.analytics_combobox_layout.addWidget(self.lbl_analytics_project)

        self.combobox_analytics_project = QComboBox(self.tab_analytics)
        self.combobox_analytics_project.setObjectName(u"combobox_analytics_project")
        self.analytics_combobox_layout.addWidget(self.combobox_analytics_project)

        self.analytics_combobox_layout.addStretch(1)

        self.analytics_layout.addLayout(self.analytics_combobox_layout)

        self.analytics_widgets_layout = QHBoxLayout()
        self.analytics_widgets_layout.setObjectName(u"analytics_widgets_layout")

        self.widget_avg_tasks = QFrame(self.tab_analytics)
        self.widget_avg_tasks.setObjectName(u"widget_avg_tasks")
        self.widget_avg_tasks.setFrameShape(QFrame.Shape.StyledPanel)
        self.avg_tasks_layout = QVBoxLayout(self.widget_avg_tasks)
        self.avg_tasks_lbl = QLabel(self.widget_avg_tasks)
        self.avg_tasks_lbl.setObjectName(u"avg_tasks_lbl")
        self.avg_tasks_value_lbl = QLabel(self.widget_avg_tasks)
        self.avg_tasks_value_lbl.setObjectName(u"avg_tasks_value_lbl")
        self.avg_tasks_value_lbl.setFont(QFont("Calibri", 24, 75, False))
        self.avg_tasks_layout.addWidget(self.avg_tasks_lbl)
        self.avg_tasks_layout.addWidget(self.avg_tasks_value_lbl)
        self.analytics_widgets_layout.addWidget(self.widget_avg_tasks, 1)

        self.widget_tasks_distribution = QFrame(self.tab_analytics)
        self.widget_tasks_distribution.setObjectName(u"widget_tasks_distribution")
        self.widget_tasks_distribution.setFrameShape(QFrame.Shape.StyledPanel)
        self.tasks_distribution_layout = QVBoxLayout(self.widget_tasks_distribution)
        self.tasks_distribution_lbl = QLabel(self.widget_tasks_distribution)
        self.tasks_distribution_lbl.setObjectName(u"tasks_distribution_lbl")
        self.tasks_distribution_chart_lbl = QLabel(self.widget_tasks_distribution)
        self.tasks_distribution_chart_lbl.setObjectName(u"tasks_distribution_chart_lbl")
        self.tasks_distribution_chart_lbl.setText(u"[График будет здесь]")
        self.tasks_distribution_chart_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tasks_distribution_layout.addWidget(self.tasks_distribution_lbl)
        self.tasks_distribution_layout.addWidget(self.tasks_distribution_chart_lbl)
        self.analytics_widgets_layout.addWidget(self.widget_tasks_distribution, 1)

        self.analytics_layout.addLayout(self.analytics_widgets_layout)

        self.tab_widget.addTab(self.tab_analytics, u"Аналитика")

        # Вкладка "Инфо"
        self.tab_info = QWidget()
        self.tab_info.setObjectName(u"tab_info")
        self.info_layout = QVBoxLayout(self.tab_info)
        self.info_layout.setObjectName(u"info_layout")

        self.info_content_layout = QVBoxLayout()
        self.info_content_layout.setObjectName(u"info_content_layout")

        self.lbl_workspace_name_info = QLabel(self.tab_info)
        self.lbl_workspace_name_info.setObjectName(u"lbl_workspace_name_info")
        font = QFont("Calibri", 18, 75, False)
        self.lbl_workspace_name_info.setFont(font)
        self.info_content_layout.addWidget(self.lbl_workspace_name_info)

        self.lbl_workspace_description_info = QLabel(self.tab_info)
        self.lbl_workspace_description_info.setObjectName(u"lbl_workspace_description_info")
        self.lbl_workspace_description_info.setWordWrap(True)
        self.info_content_layout.addWidget(self.lbl_workspace_description_info)

        self.info_content_layout.addStretch(1)

        self.btn_settings_info = QPushButton(self.tab_info)
        self.btn_settings_info.setObjectName(u"btn_settings_info")
        self.btn_settings_info.setMinimumSize(QSize(150, 40))

        self.info_layout.addLayout(self.info_content_layout)
        self.info_layout.addWidget(self.btn_settings_info, 0, Qt.AlignmentFlag.AlignHCenter)

        self.tab_widget.addTab(self.tab_info, u"Инфо")
        self.tab_widget.setTabEnabled(2, False)

        # Вкладка "Участники"
        self.tab_participants = QWidget()
        self.tab_participants.setObjectName(u"tab_participants")
        self.participants_layout = QVBoxLayout(self.tab_participants)
        self.participants_layout.setObjectName(u"participants_layout")

        self.scroll_area_participants = QScrollArea(self.tab_participants)
        self.scroll_area_participants.setObjectName(u"scroll_area_participants")
        self.scroll_area_participants.setWidgetResizable(True)

        self.scroll_area_participants_contents = QWidget()
        self.scroll_area_participants_contents.setObjectName(u"scroll_area_participants_contents")
        self.scroll_area_participants_contents.setGeometry(QRect(0, 0, 1000, 700))

        self.participants_container_layout = QVBoxLayout(self.scroll_area_participants_contents)
        self.participants_container_layout.setObjectName(u"participants_container_layout")
        self.participants_container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area_participants.setWidget(self.scroll_area_participants_contents)
        self.participants_layout.addWidget(self.scroll_area_participants)

        self.tab_widget.addTab(self.tab_participants, u"Участники")

        self.vertical_layout.addWidget(self.tab_widget, 10)

        self.retranslateUi(WorkspaceWindow)
        QMetaObject.connectSlotsByName(WorkspaceWindow)

    def retranslateUi(self, WorkspaceWindow):
        WorkspaceWindow.setWindowTitle(QCoreApplication.translate("WorkspaceWindow", u"Рабочее пространство", None))
        self.btn_back.setText(QCoreApplication.translate("WorkspaceWindow", u"\u2190", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_projects), QCoreApplication.translate("WorkspaceWindow", u"Проекты", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_analytics), QCoreApplication.translate("WorkspaceWindow", u"Аналитика", None))
        self.lbl_analytics_project.setText(QCoreApplication.translate("WorkspaceWindow", u"Проект:", None))
        self.avg_tasks_lbl.setText(QCoreApplication.translate("WorkspaceWindow", u"Задач на участника в среднем:", None))
        self.avg_tasks_value_lbl.setText(QCoreApplication.translate("WorkspaceWindow", u"0", None))
        self.tasks_distribution_lbl.setText(QCoreApplication.translate("WorkspaceWindow", u"Распределение задач по участникам:", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_info), QCoreApplication.translate("WorkspaceWindow", u"Инфо", None))
        self.lbl_workspace_name_info.setText(QCoreApplication.translate("WorkspaceWindow", u"Название рабочего пространства", None))
        self.lbl_workspace_description_info.setText(QCoreApplication.translate("WorkspaceWindow", u"Описание рабочего пространства", None))
        self.btn_settings_info.setText(QCoreApplication.translate("WorkspaceWindow", u"Настройки", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_participants), QCoreApplication.translate("WorkspaceWindow", u"Участники", None))
