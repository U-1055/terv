from pathlib import Path


def generate_base_const(models_file_path: Path, const_file_path: Path, encoding: str = 'utf-8', unique=True):
    """
    Генерирует файл с классом констант (названий полей) по полям моделей sqlalchemy из заданного файла
    Предполагается, что каждое поле каждого класса имеет аннотацию типа и все модели наследуются от какого-либо класса.
    Например, из файла вида :

    class SqlAlchemyModel(Base):
        id: Mapped[int] = ...
        name: Mapped[str] = ...

    Получится:

    class DBFieldsConst:
        # SqlAlchemyModel's fields
        id = 'id'
        name = 'name'

    :param models_file_path: Файл с моделями.
    :param const_file_path: Файл, в который будут записаны константы (не должен существовать).
    :param encoding: Кодировка (по умолч. - utf-8).
    :param unique: Если True - записывать только те параметры, которые ещё не встречались в других моделях, иначе - все.
    """

    if const_file_path.is_file():
        raise ValueError(f'Creating const file already exists: {const_file_path}')
    result_lines = []

    with open(models_file_path) as file:
        lines = file.readlines()

    result_lines.append('# Generated with server/utils/base_const_generator.generate_base_const\n')
    result_lines.append('class DBFieldsConst:\n')

    for line in lines:
        if 'class' in line:
            splitted_line = line.split()
            class_name = splitted_line[1].split('(')[0]
            result_lines.append(f"    # {class_name}'s fields\n")
        if line.startswith('    ') and ':' in line:  # Отступ в начале строки и есть разделитель :
            field_name = line.split(':')[0]  # Предполагаются аннотации для всех полей моделей в файле
            result_line = f"{field_name} = '{field_name.strip()}'\n"
            if unique and not result_line in result_lines or not unique:
                result_lines.append(f"{field_name} = '{field_name.strip()}'\n")

    with open(const_file_path, 'w', encoding=encoding) as file:
        file.writelines(''.join(result_lines))


if __name__ == '__main__':
    generate_base_const(Path('../database/models/common_models.py'), Path('common_const.py'), unique=True)
