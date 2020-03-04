"""Работа с категориями расходов"""
from typing import Dict, List, NamedTuple, Tuple

import db


class Category(NamedTuple):
    """Структура категории"""
    codename: str
    name: str
    is_base_expense: bool
    aliases: List[str]


class Categories:
    """Класс обработчика списка категорий"""

    def __init__(self):
        self._categories = self._load_categories()

    def _load_categories(self) -> List[Category]:
        """Возвращает справочник категорий из БД"""
        categories = db.fetchall("categories", "codename name is_base_expense aliases".split())
        categories = self._fill_aliases(categories)
        return categories

    @staticmethod
    def _fill_aliases(categories: List[Dict]) -> List[Category]:
        """Заполняет алиасы (псевдонимы)по каждой категории"""

        categories_result = []
        for index, category in enumerate(categories):
            aliases = category["aliases"].split(",")
            aliases = list(filter(None, map(str.strip, aliases)))
            aliases.append(category["codename"])
            aliases.append(category["name"])

            categories_result.append(Category(
                codename=category['codename'],
                name=category['name'],
                is_base_expense=category['is_base_expense'],
                aliases=aliases
            ))

        return categories_result

    def get_all_categories(self) -> List:
        """Возвращает справочник категорий"""
        return self._categories

    def get_category(self, category_name: str) -> Category:
        """Возвращает категорию по одному из её алиасов"""
        desired_category = None
        other_category = None

        for category in self._categories:
            if category.codename == "other":
                other_category = category
            for alias in category.aliases:
                if category_name in alias:
                    desired_category = category

        if not desired_category:
            desired_category = other_category

        return desired_category
