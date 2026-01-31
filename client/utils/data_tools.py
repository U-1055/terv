

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


if __name__ == '__main__':
    dicts = [{'name': i} for i in range(20)]
    print(dicts)
    result = make_unique_dict_names(dicts)
    print(result)
