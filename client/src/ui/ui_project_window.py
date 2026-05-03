# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'project_window.ui'
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
    QLabel, QPushButton, QScrollArea, QTextEdit,
    QSizePolicy, QSpacerItem, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_ProjectWindow(object):
    def setupUi(self, ProjectWindow):
        if not ProjectWindow.objectName():
            ProjectWindow.setObjectName(u"ProjectWindow")
        ProjectWindow.resize(1200, 800)

        self.vertical_layout = QVBoxLayout(ProjectWindow)
        self.vertical_layout.setObjectName(u"vertical_layout")
        self.vertical_layout.setContentsMargins(10, 10, 10, 10)

        # Верхняя панель с кнопкой возврата
        self.top_panel_layout = QHBoxLayout()
        self.top_panel_layout.setObjectName(u"top_panel_layout")

        self.btn_back = QPushButton(ProjectWindow)
        self.btn_back.setObjectName(u"btn_back")
        self.btn_back.setMinimumSize(QSize(30, 30))
        self.btn_back.setMaximumSize(QSize(30, 30))
        self.top_panel_layout.addWidget(self.btn_back)

        self.horizontal_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.top_panel_layout.addItem(self.horizontal_spacer)

        self.vertical_layout.addLayout(self.top_panel_layout)

        # Вкладки
        self.tab_widget = QTabWidget(ProjectWindow)
        self.tab_widget.setObjectName(u"tab_widget")

        # Вкладка "Инфо"
        self.tab_info = QWidget()
        self.tab_info.setObjectName(u"tab_info")
        self.info_layout = QVBoxLayout(self.tab_info)
        self.info_layout.setObjectName(u"info_layout")

        # Поля для редактирования информации о проекте
        self.info_form_layout = QVBoxLayout()
        self.info_form_layout.setObjectName(u"info_form_layout")

        # Кнопка "Сохранить все"
        self.save_all_layout = QHBoxLayout()
        self.save_all_layout.setObjectName(u"save_all_layout")
        self.btn_save_all = QPushButton(self.tab_info)
        self.btn_save_all.setObjectName(u"btn_save_all")
        self.btn_save_all.setMinimumSize(QSize(120, 35))
        self.save_all_layout.addWidget(self.btn_save_all)
        self.save_all_layout.addStretch(1)
        self.info_form_layout.addLayout(self.save_all_layout)

        self.lbl_goal = QLabel(self.tab_info)
        self.lbl_goal.setObjectName(u"lbl_goal")
        self.info_form_layout.addWidget(self.lbl_goal)

        self.text_edit_goal = QTextEdit(self.tab_info)
        self.text_edit_goal.setObjectName(u"text_edit_goal")
        self.info_form_layout.addWidget(self.text_edit_goal)

        # Кнопки Цель
        self.goal_btn_layout = QHBoxLayout()
        self.goal_btn_layout.setObjectName(u"goal_btn_layout")
        self.btn_goal_save = QPushButton(self.tab_info)
        self.btn_goal_save.setObjectName(u"btn_goal_save")
        self.goal_btn_layout.addWidget(self.btn_goal_save)
        self.btn_goal_cancel = QPushButton(self.tab_info)
        self.btn_goal_cancel.setObjectName(u"btn_goal_cancel")
        self.goal_btn_layout.addWidget(self.btn_goal_cancel)
        self.goal_btn_layout.addStretch(1)
        self.info_form_layout.addLayout(self.goal_btn_layout)

        self.lbl_tasks = QLabel(self.tab_info)
        self.lbl_tasks.setObjectName(u"lbl_tasks")
        self.info_form_layout.addWidget(self.lbl_tasks)

        self.text_edit_tasks = QTextEdit(self.tab_info)
        self.text_edit_tasks.setObjectName(u"text_edit_tasks")
        self.info_form_layout.addWidget(self.text_edit_tasks)

        # Кнопки Задачи
        self.tasks_btn_layout = QHBoxLayout()
        self.tasks_btn_layout.setObjectName(u"tasks_btn_layout")
        self.btn_tasks_save = QPushButton(self.tab_info)
        self.btn_tasks_save.setObjectName(u"btn_tasks_save")
        self.tasks_btn_layout.addWidget(self.btn_tasks_save)
        self.btn_tasks_cancel = QPushButton(self.tab_info)
        self.btn_tasks_cancel.setObjectName(u"btn_tasks_cancel")
        self.tasks_btn_layout.addWidget(self.btn_tasks_cancel)
        self.tasks_btn_layout.addStretch(1)
        self.info_form_layout.addLayout(self.tasks_btn_layout)

        self.lbl_relevance = QLabel(self.tab_info)
        self.lbl_relevance.setObjectName(u"lbl_relevance")
        self.info_form_layout.addWidget(self.lbl_relevance)

        self.text_edit_relevance = QTextEdit(self.tab_info)
        self.text_edit_relevance.setObjectName(u"text_edit_relevance")
        self.info_form_layout.addWidget(self.text_edit_relevance)

        # Кнопки Актуальность
        self.relevance_btn_layout = QHBoxLayout()
        self.relevance_btn_layout.setObjectName(u"relevance_btn_layout")
        self.btn_relevance_save = QPushButton(self.tab_info)
        self.btn_relevance_save.setObjectName(u"btn_relevance_save")
        self.relevance_btn_layout.addWidget(self.btn_relevance_save)
        self.btn_relevance_cancel = QPushButton(self.tab_info)
        self.btn_relevance_cancel.setObjectName(u"btn_relevance_cancel")
        self.relevance_btn_layout.addWidget(self.btn_relevance_cancel)
        self.relevance_btn_layout.addStretch(1)
        self.info_form_layout.addLayout(self.relevance_btn_layout)

        self.lbl_problem = QLabel(self.tab_info)
        self.lbl_problem.setObjectName(u"lbl_problem")
        self.info_form_layout.addWidget(self.lbl_problem)

        self.text_edit_problem = QTextEdit(self.tab_info)
        self.text_edit_problem.setObjectName(u"text_edit_problem")
        self.info_form_layout.addWidget(self.text_edit_problem)

        # Кнопки Проблема
        self.problem_btn_layout = QHBoxLayout()
        self.problem_btn_layout.setObjectName(u"problem_btn_layout")
        self.btn_problem_save = QPushButton(self.tab_info)
        self.btn_problem_save.setObjectName(u"btn_problem_save")
        self.problem_btn_layout.addWidget(self.btn_problem_save)
        self.btn_problem_cancel = QPushButton(self.tab_info)
        self.btn_problem_cancel.setObjectName(u"btn_problem_cancel")
        self.problem_btn_layout.addWidget(self.btn_problem_cancel)
        self.problem_btn_layout.addStretch(1)
        self.info_form_layout.addLayout(self.problem_btn_layout)

        self.lbl_theses = QLabel(self.tab_info)
        self.lbl_theses.setObjectName(u"lbl_theses")
        self.info_form_layout.addWidget(self.lbl_theses)

        self.text_edit_theses = QTextEdit(self.tab_info)
        self.text_edit_theses.setObjectName(u"text_edit_theses")
        self.info_form_layout.addWidget(self.text_edit_theses)

        # Кнопки Тезисы
        self.thesis_btn_layout = QHBoxLayout()
        self.thesis_btn_layout.setObjectName(u"thesis_btn_layout")
        self.btn_thesis_save = QPushButton(self.tab_info)
        self.btn_thesis_save.setObjectName(u"btn_thesis_save")
        self.thesis_btn_layout.addWidget(self.btn_thesis_save)
        self.btn_thesis_cancel = QPushButton(self.tab_info)
        self.btn_thesis_cancel.setObjectName(u"btn_thesis_cancel")
        self.thesis_btn_layout.addWidget(self.btn_thesis_cancel)
        self.thesis_btn_layout.addStretch(1)
        self.info_form_layout.addLayout(self.thesis_btn_layout)

        self.info_form_layout.addStretch(1)

        self.info_layout.addLayout(self.info_form_layout)

        self.tab_widget.addTab(self.tab_info, u"Инфо")

        # Вкладка "План"
        self.tab_plan = QWidget()
        self.tab_plan.setObjectName(u"tab_plan")
        self.plan_layout = QVBoxLayout(self.tab_plan)
        self.plan_layout.setObjectName(u"plan_layout")

        self.lbl_plan_placeholder = QLabel(self.tab_plan)
        self.lbl_plan_placeholder.setObjectName(u"lbl_plan_placeholder")
        self.lbl_plan_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.plan_layout.addWidget(self.lbl_plan_placeholder)

        self.tab_widget.addTab(self.tab_plan, u"План")

        # Вкладка "Задачи"
        self.tab_tasks = QWidget()
        self.tab_tasks.setObjectName(u"tab_tasks")
        self.tasks_layout = QVBoxLayout(self.tab_tasks)
        self.tasks_layout.setObjectName(u"tasks_layout")

        # Кнопка создания задачи
        self.btn_create_task = QPushButton(self.tab_tasks)
        self.btn_create_task.setObjectName(u"btn_create_task")
        self.btn_create_task.setMinimumSize(QSize(150, 35))
        self.tasks_layout.addWidget(self.btn_create_task, 0, Qt.AlignmentFlag.AlignRight)

        # Колонки задач
        self.columns_layout = QHBoxLayout()
        self.columns_layout.setObjectName(u"columns_layout")

        # Колонка "Запланировано"
        self.column_planned = QWidget()
        self.column_planned_layout = QVBoxLayout(self.column_planned)
        self.column_planned_layout.setObjectName(u"column_planned_layout")
        self.lbl_column_planned = QLabel(self.column_planned)
        self.lbl_column_planned.setObjectName(u"lbl_column_planned")
        self.lbl_column_planned.setFont(QFont("Calibri", 12, 75, False))
        self.column_planned_layout.addWidget(self.lbl_column_planned)
        self.scroll_planned = QScrollArea(self.column_planned)
        self.scroll_planned.setWidgetResizable(True)
        self.scroll_planned_contents = QWidget()
        self.scroll_planned_contents_layout = QVBoxLayout(self.scroll_planned_contents)
        self.scroll_planned.setWidget(self.scroll_planned_contents)
        self.column_planned_layout.addWidget(self.scroll_planned)
        self.columns_layout.addWidget(self.column_planned, 1)

        # Колонка "В работе"
        self.column_in_progress = QWidget()
        self.column_in_progress_layout = QVBoxLayout(self.column_in_progress)
        self.column_in_progress_layout.setObjectName(u"column_in_progress_layout")
        self.lbl_column_in_progress = QLabel(self.column_in_progress)
        self.lbl_column_in_progress.setObjectName(u"lbl_column_in_progress")
        self.lbl_column_in_progress.setFont(QFont("Calibri", 12, 75, False))
        self.column_in_progress_layout.addWidget(self.lbl_column_in_progress)
        self.scroll_in_progress = QScrollArea(self.column_in_progress)
        self.scroll_in_progress.setWidgetResizable(True)
        self.scroll_in_progress_contents = QWidget()
        self.scroll_in_progress_contents_layout = QVBoxLayout(self.scroll_in_progress_contents)
        self.scroll_in_progress.setWidget(self.scroll_in_progress_contents)
        self.column_in_progress_layout.addWidget(self.scroll_in_progress)
        self.columns_layout.addWidget(self.column_in_progress, 1)

        # Колонка "Проверяется"
        self.column_review = QWidget()
        self.column_review_layout = QVBoxLayout(self.column_review)
        self.column_review_layout.setObjectName(u"column_review_layout")
        self.lbl_column_review = QLabel(self.column_review)
        self.lbl_column_review.setObjectName(u"lbl_column_review")
        self.lbl_column_review.setFont(QFont("Calibri", 12, 75, False))
        self.column_review_layout.addWidget(self.lbl_column_review)
        self.scroll_review = QScrollArea(self.column_review)
        self.scroll_review.setWidgetResizable(True)
        self.scroll_review_contents = QWidget()
        self.scroll_review_contents_layout = QVBoxLayout(self.scroll_review_contents)
        self.scroll_review.setWidget(self.scroll_review_contents)
        self.column_review_layout.addWidget(self.scroll_review)
        self.columns_layout.addWidget(self.column_review, 1)

        # Колонка "Выполнено"
        self.column_done = QWidget()
        self.column_done_layout = QVBoxLayout(self.column_done)
        self.column_done_layout.setObjectName(u"column_done_layout")
        self.lbl_column_done = QLabel(self.column_done)
        self.lbl_column_done.setObjectName(u"lbl_column_done")
        self.lbl_column_done.setFont(QFont("Calibri", 12, 75, False))
        self.column_done_layout.addWidget(self.lbl_column_done)
        self.scroll_done = QScrollArea(self.column_done)
        self.scroll_done.setWidgetResizable(True)
        self.scroll_done_contents = QWidget()
        self.scroll_done_contents_layout = QVBoxLayout(self.scroll_done_contents)
        self.scroll_done.setWidget(self.scroll_done_contents)
        self.column_done_layout.addWidget(self.scroll_done)
        self.columns_layout.addWidget(self.column_done, 1)

        # Колонка "Доработать"
        self.column_improve = QWidget()
        self.column_improve_layout = QVBoxLayout(self.column_improve)
        self.column_improve_layout.setObjectName(u"column_improve_layout")
        self.lbl_column_improve = QLabel(self.column_improve)
        self.lbl_column_improve.setObjectName(u"lbl_column_improve")
        self.lbl_column_improve.setFont(QFont("Calibri", 12, 75, False))
        self.column_improve_layout.addWidget(self.lbl_column_improve)
        self.scroll_improve = QScrollArea(self.column_improve)
        self.scroll_improve.setWidgetResizable(True)
        self.scroll_improve_contents = QWidget()
        self.scroll_improve_contents_layout = QVBoxLayout(self.scroll_improve_contents)
        self.scroll_improve.setWidget(self.scroll_improve_contents)
        self.column_improve_layout.addWidget(self.scroll_improve)
        self.columns_layout.addWidget(self.column_improve, 1)

        self.tasks_layout.addLayout(self.columns_layout)

        self.tab_widget.addTab(self.tab_tasks, u"Задачи")

        # Вкладка "Участники"
        self.tab_participants = QWidget()
        self.tab_participants.setObjectName(u"tab_participants")
        self.participants_layout = QVBoxLayout(self.tab_participants)
        self.participants_layout.setObjectName(u"participants_layout")

        self.scroll_participants = QScrollArea(self.tab_participants)
        self.scroll_participants.setWidgetResizable(True)
        self.scroll_participants_contents = QWidget()
        self.scroll_participants_contents_layout = QVBoxLayout(self.scroll_participants_contents)
        self.scroll_participants.setWidget(self.scroll_participants_contents)
        self.participants_layout.addWidget(self.scroll_participants)

        self.tab_widget.addTab(self.tab_participants, u"Участники")

        self.vertical_layout.addWidget(self.tab_widget, 10)

        self.retranslateUi(ProjectWindow)
        QMetaObject.connectSlotsByName(ProjectWindow)

    def retranslateUi(self, ProjectWindow):
        ProjectWindow.setWindowTitle(QCoreApplication.translate("ProjectWindow", u"Проект", None))
        self.btn_back.setText(QCoreApplication.translate("ProjectWindow", u"\u2190", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_info), QCoreApplication.translate("ProjectWindow", u"Инфо", None))
        self.btn_save_all.setText(QCoreApplication.translate("ProjectWindow", u"Сохранить все", None))
        self.lbl_goal.setText(QCoreApplication.translate("ProjectWindow", u"Цель:", None))
        self.btn_goal_save.setText(QCoreApplication.translate("ProjectWindow", u"Сохранить", None))
        self.btn_goal_cancel.setText(QCoreApplication.translate("ProjectWindow", u"Отмена", None))
        self.lbl_tasks.setText(QCoreApplication.translate("ProjectWindow", u"Задачи проекта:", None))
        self.btn_tasks_save.setText(QCoreApplication.translate("ProjectWindow", u"Сохранить", None))
        self.btn_tasks_cancel.setText(QCoreApplication.translate("ProjectWindow", u"Отмена", None))
        self.lbl_relevance.setText(QCoreApplication.translate("ProjectWindow", u"Актуальность:", None))
        self.btn_relevance_save.setText(QCoreApplication.translate("ProjectWindow", u"Сохранить", None))
        self.btn_relevance_cancel.setText(QCoreApplication.translate("ProjectWindow", u"Отмена", None))
        self.lbl_problem.setText(QCoreApplication.translate("ProjectWindow", u"Проблема:", None))
        self.btn_problem_save.setText(QCoreApplication.translate("ProjectWindow", u"Сохранить", None))
        self.btn_problem_cancel.setText(QCoreApplication.translate("ProjectWindow", u"Отмена", None))
        self.lbl_theses.setText(QCoreApplication.translate("ProjectWindow", u"Основные тезисы:", None))
        self.btn_thesis_save.setText(QCoreApplication.translate("ProjectWindow", u"Сохранить", None))
        self.btn_thesis_cancel.setText(QCoreApplication.translate("ProjectWindow", u"Отмена", None))
        self.lbl_plan_placeholder.setText(QCoreApplication.translate("ProjectWindow", u"[Раздел будет реализован позже]", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_plan), QCoreApplication.translate("ProjectWindow", u"План", None))
        self.btn_create_task.setText(QCoreApplication.translate("ProjectWindow", u"Создать задачу", None))
        self.lbl_column_planned.setText(QCoreApplication.translate("ProjectWindow", u"Запланировано", None))
        self.lbl_column_in_progress.setText(QCoreApplication.translate("ProjectWindow", u"В работе", None))
        self.lbl_column_review.setText(QCoreApplication.translate("ProjectWindow", u"Проверяется", None))
        self.lbl_column_done.setText(QCoreApplication.translate("ProjectWindow", u"Выполнено", None))
        self.lbl_column_improve.setText(QCoreApplication.translate("ProjectWindow", u"Доработать", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_tasks), QCoreApplication.translate("ProjectWindow", u"Задачи", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_participants), QCoreApplication.translate("ProjectWindow", u"Участники", None))
