from PySide6.QtWidgets import QGridLayout


def filled_columns_count(layout: QGridLayout) -> int:
    """Возвращает число непустых столбцов (таких, в строках которых есть хотя бы один виджет)."""
    columns = 0
    for col in range(layout.columnCount()):
        is_empty = True
        for row in range(layout.rowCount()):
            content = layout.itemAtPosition(row, col)
            if content:
                is_empty = False
                break

        if not is_empty:
            columns += 1

    return columns


def filled_rows_count(layout: QGridLayout) -> int:
    """Возвращает число непустых строк (таких, в столбцах которых есть хотя бы один виджет)."""
    rows = 0
    for row in range(layout.rowCount()):
        is_empty = True
        for col in range(layout.columnCount()):
            content = layout.itemAtPosition(row, col)
            if content:
                is_empty = False
                break

        if not is_empty:
            rows += 1

    return rows


def get_next_widget_grid_pos(layout: QGridLayout, next_row: bool = True) -> tuple[int, int]:
    """
    Возвращает первую свободную позицию в QGridLayout. (row, column).

    :param next_row: Устанавливать ли следующую строку после последней занятой, если нет свободных позиций в виджете.
                     Если False - будет установлен следующий столбец.
    :param layout: QGridLayout, для которого производится расчёт.
    """
    row, column = 0, 0
    for row in range(layout.rowCount()):
        for column in range(layout.columnCount()):
            content = layout.itemAtPosition(row, column)
            if not content:
                return row, column
    if next_row:
        return row + 1, 0
    return 0, column + 1
