from PySide6.QtGui import QFont, QColor

from common.base import CommonStruct, DBFields


class DataStructConst:

    access_token = 'access_token'
    refresh_token = 'refresh_token'
    userspace_widgets = 'userspace_widgets'
    settings = 'settings'
    style = 'style'
    styles = 'styles'

    styles_paths = {
        'style_1': r'..\data\resources\ui\styles\light_theme.qss',
        'style_2': r'..\data\resources\ui\styles\dark_theme.qss'
    }

    light = 'light'  # Названия стилей
    dark = 'dark'

    light_main_color = '#B2F0FF'  # Основные цвета стилей
    dark_main_color = '#051a39'

    light_style = f':\\styles\\{light}'  # Пути к стилям
    dark_style = f':\\styles\\{dark}'

    gui_date_format = '%d %b. %Y г.'
    gui_day_date_format = '%a, %d %b.'
    gui_month_date_format = '%a %b'
    tasks_widget = 'tasks_widget'
    schedule_widget = 'schedule_widget'
    reminder_widget = 'reminder_widget'
    notes_widget = 'notes_widget'
    note = 'note'
    reminders = 'reminders'

    dark_marking_color = QColor('black')
    light_marking_color = QColor('#B0B0B0')

    names_widgets = [tasks_widget, notes_widget, reminder_widget, schedule_widget]

    x, y = 'x', 'y'
    x_size = 'x_size'
    y_size = 'y_size'

    max_reminder_length = 40  # Максимальная длина напоминания (символы)

    max_x_size = 2
    max_y_size = 3

    max_requests = 10  # Максимальное число хранимых запросов в реквестере
    max_request_id = max_requests * 10  # Максимальное ID запроса

    userspace_loading_time = 1000  # Число миллисекунд, в течение которых работает окно загрузки перед открытием окна ПП

    char_plus = '+'


class ObjectNames:
    """Имена объектов, использующиеся в QSS-стилях."""

    small_btn_add = 'small_btn_add'
    small_btn_complete = 'small_btn_complete'
    btn_show_details = 'btn_show_details'
    btn_exit = 'btn_exit'
    wdg_border = 'wdg_border'  # Виджет с границей
    btn_log_in = 'btn_log_in'


class GuiLabels:

    exit = 'Выйти'
    authorize = 'Войти'
    password = 'Пароль'
    login = 'Логин'
    register = 'Зарегистрироваться'
    apply = 'Применить'
    email = 'Email'
    userspace_settings = 'Настройки пространства'
    label_userspace_settings = 'Выберите виджеты, которые хотите разместить в пространстве'
    change_theme = 'Сменить тему'

    tasks_widget = 'Задачи на сегодня'
    notes_widget = 'Заметки'
    reminder_widget = 'Напоминания'
    schedule_widget = 'Расписание'
    events_today = 'Мероприятия на сегодня'

    new_reminder = 'Новое напоминание'

    authorization = 'Авторизация'

    default_dialog_window_title = 'terv'
    registration_window = 'Регистрация'
    widgets_settings_window = 'Настройки виджетов ПП'

    hide_password = 'Скрыть'

    incorrect_credentials = 'Неверный логин или пароль'
    incorrect_login = f'Логин должен быть длиной от {CommonStruct.min_login_length} до {CommonStruct.max_login_length} символов'
    incorrect_email = 'Некорректный email'
    used_email = 'Уже существует аккаунт с таким email'
    used_login = 'Имя пользователя должно быть уникальным'
    fill_all = 'Необходимо заполнить все поля'
    incorrect_password = (f'Пароль должен быть длиной от {CommonStruct.min_password_length} до '
                          f'{CommonStruct.max_password_length} символов и включать в себя буквы латинского алфавита, цифры и другие символы')

    register_complete = 'Регистрация прошла успешно. Теперь войдите в аккаунт'
    authentication_complete = 'Аутентификация прошла успешно!'
    network_error = 'Произошла ошибка сети. Проверьте интернет-соединение.'

    op_complete = 'Операция выполнена'
    error_occurred = 'Произошла ошибка'
    default_time_separator = '-'
    lasting_label = 'Длительность: '
    start_end_label = 'Время: '

    workspace = 'Рабочее пространство'
    project = 'Проект'
    entrusted = 'Поручил'
    plan_deadline = 'Дедлайн'
    title = 'Название'
    description = 'Описание'
    fact_start_work_date = 'Взято в работу'
    plan_start_work_date = 'Планируется взять в работу'
    responsible = 'Ответственный'
    notifieds = 'Уведомляются'
    creator = 'Создатель'
    lasting = 'Длительность'
    days = 'дней'

    userspace = 'Моё пространство'
    tasks = 'Задачи'
    calendar = 'Календарь'
    knowledge_base = 'База знаний'
    workspaces = 'Рабочие пространства'
    projects = 'Проекты'
    settings = 'Настройки'
    account_leaved = 'Вы вышли из аккаунта'
    message = 'Сообщение'
    enter_account = 'Войдите в аккаунт'
    executors = 'Исполнители'

    loading = 'Загрузка...'
    ready = 'Готово!'


class GUIStyles:

    normal_style = ''
    error_style = ''
    base_font = QFont('Segoe UI', 9, 2, False)
    bold_font = QFont('Segoe UI', 9, 2, False)
    title_font = QFont('Segoe UI', 15, 2, False)
    bold_font.setBold(True)


widgets_labels = {  # Соответствие названий виджетов надписям на них
    DataStructConst.tasks_widget: GuiLabels.tasks_widget,
    DataStructConst.notes_widget: GuiLabels.notes_widget,
    DataStructConst.reminder_widget: GuiLabels.reminder_widget,
    DataStructConst.schedule_widget: GuiLabels.schedule_widget
}

labels_widgets = {widgets_labels[key]: key for key in widgets_labels}  # Соответствие надписей на виджетах их названиям

styles_paths = {
    DataStructConst.light: DataStructConst.light_style,
    DataStructConst.dark: DataStructConst.dark_style
                }

db_fields_labels = {  # Соответствие между полями БД и надписями в GUI
    DBFields.workspace: GuiLabels.workspace,
    DBFields.creator: GuiLabels.creator,
    DBFields.email: GuiLabels.email,
}

