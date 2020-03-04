from typing import NamedTuple, Optional
from re import search, findall

import db
import expenses
from categories import Categories


def processing_command(command: str, user_id: int) -> str:
    template_add_expense = r"^/(\d+[\.\d+|,\d+]*)р? (\w+)"
    template_delete_expense = r"/удалить (\d)"
    template_get_limit = r"^/лимит$"
    template_change_limit = r"^/лимит (\d+[\.\d+|,\d+]*)р?$"

    if command in ["/старт", "/помощь"]:
        return get_welcome_message()

    elif search(template_add_expense, command):
        expense = expenses.add_expense(message=command, user_id=user_id)
        answer_message = f"{expense.amount}р добавлено в категорию {expense.category_name}\n"
        return answer_message

    elif search(template_delete_expense, command):
        expense_id = findall(template_delete_expense, command)[0]
        expenses.delete_expense(expense_id=expense_id)
        return "Расход удалён"

    elif command in ["/категории"]:
        return get_categories()

    elif command in ["/день"]:
        return expenses.get_today_statistics(user_id=user_id)

    elif command in ["/месяц"]:
        return expenses.get_month_statistics(user_id=user_id)

    elif command in ["/затраты"]:
        last_expenses = expenses.last_expenses(user_id=user_id)
        if not last_expenses:
            return "Расходы ещё не заведены"

        last_expenses_rows = [
            f"{expense.amount} руб. на {expense.category_name} — введите "
            f"\"/удалить {expense.id}\" для удаления"
            for expense in last_expenses]
        answer_message = "Последние сохранённые траты:\n\n— " + "\n\n— ".join(last_expenses_rows)

        return answer_message

    elif search(template_get_limit, command):
        daily_limit = expenses.get_daily_limit(user_id=user_id)
        answer_message = f"Ваш дневной лимит: {daily_limit}"
        return answer_message

    elif search(template_change_limit, command):
        new_daily_limit = findall(template_change_limit, command)[0]
        if expenses.change_daily_limit(new_daily_limit=new_daily_limit, user_id=user_id):
            answer_message = "Суточнный лимит изменён"
        else:
            answer_message = "Ошибка! Суточный лимит не изменён"

        return answer_message

    else:
        answer_message = "Ошибка! Неверная команда"
        return answer_message


def is_user_present(user_id: int) -> bool:
    table = "users"
    columns = ["id"]
    filters = [{"id": str(user_id)}]
    if len(db.fetchall(table, columns, filters)):
        return True
    return False


def add_user(user_id: int) -> str:
    answer_message = "Вы успешно добавлены в систему"
    inserted_row_id = db.insert("users", {"id": user_id})
    if not inserted_row_id:
        answer_message = "Возникшла ошибка при добавлении вас в систему"

    return answer_message


def get_welcome_message() -> str:
    answer_message = "Бот учёта расходов\n\n" \
                     "Добавить расход: /100 чай\n" \
                     "Список категорий: /категории\n" \
                     "Статистика за день: /день\n" \
                     "Статистика за месяц: /месяц\n" \
                     "Последние затраты: /затраты\n" \
                     "Удалить расход: /удалить 100 (идентификатор расхода)\n"
    return answer_message


def get_categories() -> str:
    categories = Categories().get_all_categories()
    answer_message = "Категории трат:\n\n- " + \
                     ("\n- ".join([c.name + ' (' + ", ".join(c.aliases) + ')\n' for c in categories]))
    return answer_message
