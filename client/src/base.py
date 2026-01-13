from client.src.gui.widgets_view.userflow_view import TaskWidgetView
from common.base import CommonStruct


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

    max_requests = 10  # Максимальное число хранимых запросов в реквестере
    max_request_id = max_requests * 10  # Максимальное ID запроса


class GuiLabels:

    authorize = 'Войти'
    password = 'Пароль'
    login = 'Логин'
    register = 'Зарегистрироваться'
    email = 'Email'

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

    op_complete = 'Операция выполнена'

class GUIStyles:

    normal_style = ''
    error_style = ''





