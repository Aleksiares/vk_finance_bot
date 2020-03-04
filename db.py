import os
from typing import Dict, List, Tuple

import sqlite3

import config


connector = sqlite3.connect(os.path.join(config.DB_NAME))
cursor = connector.cursor()


def insert(table: str, column_values: Dict) -> bool:
    """
    Функция вставки значений в таблицу
    :param table: имя таблицы
    :param column_values: список столбцов и соответствующих им значений
    :return: bool значение - получилось ли выполнить вставку в таблицу
    """
    is_ready = False
    columns = ", ".join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join("?" * len(column_values.keys()))

    if cursor.executemany(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values):
        is_ready = True
    connector.commit()

    return is_ready


def fetchall(table: str, columns: List[str], filters: List[Dict[str, str]] = None) -> List[Tuple]:
    """
    Функция получения значений из таблицы, с возможностью простой фильтрации
    (WHERE column1 = value1 AND column2 = value2 AND ...)
    :param table: имя таблицы
    :param columns: список столбцов
    :param filters: список столбцов и соответствующих им значений для выражения (WHERE)
    :return: список кортежей столбцов таблицы
    """

    columns_joined = ", ".join(columns)

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
    """
    Функция удаления кортежа из таблицы по его id
    :param table: имя таблицы
    :param row_id: id кортежа
    :return: None
    """
    cursor.execute(f"DELETE from {table} WHERE id={row_id}")
    connector.commit()


def update(table: str, columns: Dict, filters: Dict) -> bool:
    """
    Функция обновления записи в таблице в соответствие с заданным простым условием
    (WHERE column1 = value1 AND column2 = value2 AND ...)
    :param table: имя таблицы
    :param columns: списки обновляемых колонок и их значений
    :param filters: список столбцов и соответствующих им значений для выражения (WHERE)
    :return: bool значение - получилось ли выполнить обновление в таблице
    """
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
    """Функция получения курсора"""
    return cursor


def _init_db():
    """
    Функция иницилизации БД
    Выполняет SQL код из файла createdb.sql
    """

    with open("createdb.sql", "r", encoding="utf-8") as file:
        sql = file.read()
    cursor.executescript(sql)
    connector.commit()


def check_db_exists():
    """
    Функция проверки структуры БД
    Если структура не создана - вызывает иницилизацию
    """

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' and name='expenses'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()


check_db_exists()
