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
    note = 'note'

    names_widgets = [tasks_widget, notes_widget, memory_widget]

    x, y = 'x', 'y'
    x_size = 'x_size'
    y_size = 'y_size'

    max_x_size = 3
    max_y_size = 3

    max_requests = 10  # Максимальное число хранимых запросов в реквестере
    max_request_id = max_requests * 10  # Максимальное ID запроса


class GuiLabels:

    authorize = 'Войти'
    password = 'Пароль'
    login = 'Логин'
    register = 'Зарегистрироваться'
    apply = 'Применить'
    email = 'Email'
    userflow_settings = 'Настройки пространства'
    label_userflow_settings = 'Выберите виджеты, которые хотите разместить в пространстве'

    tasks_widget = 'Задачи на сегодня'
    notes_widget = 'Заметки'
    memory_widget = 'Напоминания'

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
    network_error = 'Ошибка сети: не удалось выполнить операцию. Попробуйте обновить окно.'

    op_complete = 'Операция выполнена'
    error_occurred = 'Произошла ошибка'


class GUIStyles:

    normal_style = ''
    error_style = ''


widgets_labels = {  # Соответствие названий виджетов надписям на них
    DataStructConst.tasks_widget: GuiLabels.tasks_widget,
    DataStructConst.notes_widget: GuiLabels.notes_widget,
    DataStructConst.memory_widget: GuiLabels.memory_widget
}

labels_widgets = {widgets_labels[key]: key for key in widgets_labels}  # Соответствие надписей на виджетах их названиям



