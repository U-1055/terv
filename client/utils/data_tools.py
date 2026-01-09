

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


if __name__ == '__main__':
    dicts = [{'name': i} for i in range(20)]
    print(dicts)
    result = make_unique_dict_names(dicts)
    print(result)
