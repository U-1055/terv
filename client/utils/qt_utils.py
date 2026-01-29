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
