from terv.src.gui.widgets_view.userflow_view import TaskWidgetView


class DataStructConst:

    access_token = 'access_token'
    refresh_token = 'refresh_token'
    userflow_widgets = 'userflow_widgets'
    settings = 'settings'
    style = 'style'

    styles_paths = {
        'style_1': r'..\data\resources\ui\styles\light_theme.qss',
        'style_2': r'..\data\resources\ui\styles\dark_theme.qss'
    }

    tasks_widget = 'tasks_widget'
    schedule_widget = 'schedule_widget'
    memory_widget = 'memory_widget'
    notes_widget = 'notes_widget'

    names_widgets = {  # Типы виджетов и их имена
        tasks_widget: TaskWidgetView
    }

    x, y = 'x', 'y'
    x_size = 'x_size'
    y_size = 'y_size'

    min_password_length = 8
    min_login_length = 3


class GuiLabels:

    authorize = 'Войти'
    password = 'Пароль'
    login = 'Логин'
    register = 'Зарегистрироваться'
    email = 'Email'


class GUIStyles:

    normal_style = ''
    error_style = ''





