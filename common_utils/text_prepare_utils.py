"""Утилиты обработки текста."""


def snake_to_camel_case(line: str, up_first: bool = False) -> str:
    """
    Преобразует строку в snake_case в CamelCase.

    :param line: Преобразуемая строка.
    :param up_first: Делать ли первую букву заглавной? По умолчанию: False.

    """
    res = []

    last_char = '_' if up_first else ''
    for char in line:
        if last_char == '_' and char.islower():
            char = char.upper()
        last_char = char
        if char != '_':
            res.append(char)

    return ''.join(res)


if __name__ == '__main__':
    print(snake_to_camel_case('snake_case'))