import os
from typing import Dict, List, Tuple

import sqlite3

import config


connector = sqlite3.connect(os.path.join(config.DB_NAME))
cursor = connector.cursor()


def insert(table: str, column_values: Dict) -> bool:
    is_ready = False
    columns = ", ".join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join("?" * len(column_values.keys()))

    if cursor.executemany(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values):
        is_ready = True
    connector.commit()

    return is_ready


def fetchall(table: str, columns: List[str], filters: List[Dict[str, str]] = None) -> List[Tuple]:
    columns_joined = ", ".join(columns)

    # Подумать ещё над фильтром
    filters_line = ""
    if filters is not None:
        lines = []
        for column in filters:
            for name in column:
                lines.append(f"{name} = {str(column[name])}")

        filters_line = "WHERE " + " AND ".join(lines)

    cursor.execute(f"SELECT {columns_joined} FROM {table} {filters_line}")
    rows = cursor.fetchall()

    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)

    return result


def delete(table: str, row_id: int) -> None:
    cursor.execute(f"DELETE from {table} WHERE id={row_id}")
    connector.commit()


def update(table: str, columns: Dict, filters: Dict) -> bool:
    lines = []
    for name in columns:
        lines.append(f"{name} = {str(columns[name])}")
    columns_line = " AND ".join(lines)

    lines = []
    for name in filters:
        lines.append(f"{name} = {str(filters[name])}")
    filters_line = " AND ".join(lines)

    if not cursor.execute(f"UPDATE {table} SET {columns_line} WHERE {filters_line}"):
        return False
    connector.commit()
    return True


def get_cursor():
    return cursor


def _init_db():
    with open("createdb.sql", "r") as file:
        sql = file.read()
    cursor.executescript(sql)
    connector.commit()


def check_db_exists():
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' and name='expenses'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()


check_db_exists()
