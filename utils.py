"""Вспомогательные функции безопасного ввода данных."""

from datetime import date, datetime


def input_int(prompt: str) -> int:
    """Запросить у пользователя целое число, повторяя запрос при ошибке."""
    while True:
        raw_value = input(prompt)
        try:
            return int(raw_value)
        except ValueError:
            print("Введите целое число.")


def input_date(prompt: str) -> date:
    """Запросить у пользователя дату в формате ДД.ММ.ГГГГ."""
    while True:
        raw_value = input(prompt)
        try:
            return datetime.strptime(raw_value, "%d.%m.%Y").date()
        except ValueError:
            print("Введите дату в формате ДД.ММ.ГГГГ.")


def input_nonempty(prompt: str) -> str:
    """Запросить у пользователя непустую строку."""
    while True:
        raw_value = input(prompt).strip()
        if raw_value:
            return raw_value
        print("Значение не может быть пустым.")
