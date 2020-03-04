import datetime
import re
from typing import List, NamedTuple, Optional

import pytz

import db
from categories import Categories


class Message(NamedTuple):
    """Структура сообщения о новом расходе"""
    amount: int
    category_text: str


class Expense(NamedTuple):
    """Структура расхода"""
    id: Optional[int]
    user_id: Optional[int]
    amount: int
    category_name: str


def add_expense(message: str, user_id: int) -> Expense:
    """
    Функция добавления расхода в БД
    :param message: полученное сообщение
    :param user_id: идентификатор пользователя в VK
    :return: class Expense - структура расхода
    """

    parsed_message = _parse_message(message)
    category = Categories().get_category(parsed_message.category_text)

    db.insert("expenses", {
        "user_id": str(user_id),
        "amount": parsed_message.amount,
        "created": _get_now_formatted(),
        "category_codename": category.codename,
        "raw_text": message
    })

    return Expense(id=None, user_id=None, amount=parsed_message.amount, category_name=category.name)


def delete_expense(expense_id: int):
    """
    Функция удаления расхода
    :param expense_id: идентификатор расхода
    :return: None
    """
    db.delete("expenses", row_id=expense_id)


def get_today_statistics(user_id: int) -> str:
    """
    Функция получения статистики за день
    :param user_id: идентификатор пользователя в VK
    :return: сообщения о расходах за день
    """

    cursor = db.get_cursor()

    # Получения всех расходов за день
    cursor.execute("SELECT SUM(amount) "
                   "FROM expenses "
                   f"WHERE DATE(created)=DATE('now', 'localtime') AND user_id = {user_id}")
    result = cursor.fetchone()
    if not result[0]:
        return "Сегодня ещё нет расходов"
    all_today_expenses = result[0]

    # Получение базовых расходов за день
    cursor.execute("SELECT SUM(amount) "
                   "FROM expenses "
                   "WHERE DATE(created)=DATE('now', 'localtime') "
                   "AND category_codename IN (select codename FROM categories WHERE is_base_expense=true) "
                   f"AND user_id = {user_id}")
    result = cursor.fetchone()
    base_today_expenses = result[0] if result[0] else 0

    answer_message = ("Расходы сегодня:\n"
                      f"всего — {all_today_expenses} руб.\n"
                      f"базовые — {base_today_expenses} руб. из {get_daily_limit(user_id=user_id)} руб.\n\n"
                      "За текущий месяц: /месяц")
    return answer_message


def get_month_statistics(user_id: int) -> str:
    """
    Функция получения статистики за месяц
    :param user_id: идентификатор пользователя в VK
    :return: сообщения о расходах за месяц
    """

    cursor = db.get_cursor()
    now = _get_now_datetime()
    first_day_of_month = f'{now.year:04d}-{now.month:02d}-01'

    # Получения всех расходов за месяц
    cursor.execute("SELECT SUM(amount) "
                   "FROM expenses "
                   f"WHERE DATE(created) >= '{first_day_of_month}' "
                   f"AND user_id = {user_id}")
    result = cursor.fetchone()
    if not result[0]:
        return "В этом месяце ещё нет расходов"
    all_today_expenses = result[0]

    # Получение базовых расходов за месяц
    cursor.execute("SELECT SUM(amount) "
                   f"FROM expenses WHERE DATE(created) >= '{first_day_of_month}' "
                   "AND category_codename IN (SELECT codename FROM categories WHERE is_base_expense=true) "
                   f"AND user_id = {user_id}")
    result = cursor.fetchone()
    base_today_expenses = result[0] if result[0] else 0

    answer_message = (f"Расходы в текущем месяце:\n"
                      f"всего — {all_today_expenses} руб.\n"
                      f"базовые — {base_today_expenses} руб. из "
                      f"{now.day * get_daily_limit(user_id=user_id)} руб.")
    return answer_message


def last_expenses(user_id: int) -> List[Expense]:
    """
    Функция получения последних расходов пользователя (10 шт)
    :param user_id: идентификатор пользователя в VK
    :return: список расходов
    """

    cursor = db.get_cursor()
    cursor.execute(
        "SELECT e.id, e.amount, c.name "
        "FROM expenses e LEFT JOIN categories c "
        "ON c.codename=e.category_codename "
        f"WHERE user_id = {user_id} "
        "ORDER BY created DESC limit 10 ")
    rows = cursor.fetchall()

    list_expenses = [Expense(id=row[0], user_id = None, amount=row[1], category_name=row[2]) for row in rows]
    return list_expenses


def get_daily_limit(user_id: int) -> int:
    """Функция получения суточного лимита пользователя"""
    return db.fetchall("users",
                       ["daily_limit"],
                       [{"id": str(user_id)}])[0]["daily_limit"]


def change_daily_limit(new_daily_limit: int, user_id: int) -> bool:
    """Функция изменения суточного лимита пользователя"""
    return db.update("users",
                     {"daily_limit": new_daily_limit},
                     {"id": user_id})


def _parse_message(message: str) -> Message:
    """
    Функция разбора сообщения
    Позволяет получить из сообщения сумму расхода и псевдоним категории"""
    template_add_expense = r"^/(\d+[\.\d+|,\d+]*)р? (\w+)"
    regexp_result = re.findall(template_add_expense, message)[0]

    amount = regexp_result[0]
    category_text = regexp_result[1]

    return Message(amount=amount, category_text=category_text)


def _get_now_formatted() -> str:
    """Возвращает текущую дату строкой"""
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


def _get_now_datetime() -> datetime.datetime:
    """Возвращает datetime с учётом установленной временной зоны (Екб)"""
    tz = pytz.timezone("Asia/Yekaterinburg")
    now = datetime.datetime.now(tz)
    return now