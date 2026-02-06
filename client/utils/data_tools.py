import datetime
import typing as tp


def make_unique_dict_names(values: list[dict], sep: str = '_'):
    """
    Превращает набор пар ключ-значение в словарь с уникальными ключами. К каждой строке-ключу добавляет число её предыдущих вхождений.

    :param values: список вида [{<name>: <value>}, {<name>: <value>}]
    """

    names = {}
    result = {}
    for dict_ in values:
        name = list(dict_.keys())[0]
        if name in names:
            names[name] += 1
            result.update({f'{name}{sep}{names[name]}': dict_[name]})
        else:
            names[name] = 1
            result.update(dict_)

    return result


def parse_time(time_: str, minutes_in_interval: int) -> int:
    """
    Переводит время из формата HH:MM в минуты. Возвращает целое число интервалов длительностью minutes_in_interval,
    округляемое в меньшую сторону.
    Пример:
    ("14:15", 1) -> 840
    ("12:15", 15) -> 49
    ("10:20", 15) -> 11

    :param time_: время в формате HH:MM.
    :param minutes_in_interval: число минут в интервале.
    """

    hours, minutes = time_.split(':')
    total_minutes = int(hours) * 60 + int(minutes)
    intervals = total_minutes // minutes_in_interval
    return intervals


def iterable_to_str(list_: tp.Iterable, separator: str, prefix: str = '', suffix: str = ''):
    """
    Превращает итерируемый в строку, обрабатываемую по заданным параметрам (separator, preffix, suffix).

    :param list_: Итерируемый объект.
    :param separator: Разделитель для элементов list_ в преобразованной строке.
    :param prefix: Строка, которая будет добавлена в начало каждого элемента.
    :param suffix: Строка, которая будет добавлена в конец каждого элемента.

    """
    return separator.join([f'{prefix}{str(el)}{suffix}' for el in list_])


def date_to_gui_view(date: datetime.date, year: bool = True, month: bool = True, day: bool = True) -> str:
    """
    Преобразует дату к формату GUI по переданным параметрам.

    :param date: Дата (объект datetime.date).
    :param year: Оставлять ли год в дате?
    :param month: Оставлять ли месяц в дате?
    :param day: Оставлять ли день в дате?

    """
    return date.strftime()


if __name__ == '__main__':
    dicts = [{'name': i} for i in range(20)]
    print(dicts)
    result = make_unique_dict_names(dicts)
    print(result)
