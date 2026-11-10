"""Осмотр исходной базы ПР7 (data/domainreg.sqlite) перед переносом в Django ORM.

Скрипт только читает базу: выводит таблицы, столбцы, количество записей и
проверяет ссылочную целостность и формат данных, от которых зависит перенос.

Запуск из корня проекта:
    python db/inspect_source_db.py
"""

import sqlite3
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db.database import DB_PATH  # noqa: E402


def inspect(source_db: Path = DB_PATH) -> list[str]:
    """Вывести описание базы и вернуть список найденных проблем (пустой, если всё в порядке)."""
    if not source_db.exists():
        raise FileNotFoundError(f"Исходная база не найдена: {source_db}")

    problems = []
    with sqlite3.connect(f"file:{source_db}?mode=ro", uri=True) as connection:
        connection.row_factory = sqlite3.Row
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        ).fetchall()
        for (table_name,) in tables:
            print(f"\nТаблица: {table_name}")
            for column in connection.execute(f'PRAGMA table_info("{table_name}")'):
                print(
                    f"  имя={column['name']}, тип={column['type']}, "
                    f"NOT NULL={column['notnull']}, PRIMARY KEY={column['pk']}"
                )
            count = connection.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0]
            print(f"  Количество записей: {count}")

        # Ссылочная целостность: каждая ссылка должна указывать на существующую запись.
        references = [
            ("domains", "organization_id", "organizations"),
            ("domains", "owner_id", "users"),
            ("resources", "domain_id", "domains"),
            ("rentals", "user_id", "users"),
            ("rentals", "domain_id", "domains"),
        ]
        for table, column, target in references:
            broken = connection.execute(
                f"SELECT COUNT(*) FROM {table} WHERE {column} NOT IN (SELECT id FROM {target})"
            ).fetchone()[0]
            if broken:
                problems.append(f"{table}.{column}: {broken} ссылок на несуществующие {target}")

        # Формат дат (ГГГГ-ММ-ДД) и признаков (0/1).
        for table, column in [
            ("domains", "registration_end"),
            ("rentals", "start_date"),
            ("rentals", "end_date"),
        ]:
            for (value,) in connection.execute(f"SELECT {column} FROM {table}"):
                try:
                    date.fromisoformat(value)
                except (TypeError, ValueError):
                    problems.append(f"{table}.{column}: неверная дата {value!r}")
        for table, column in [("domains", "is_removed"), ("rentals", "is_cancelled")]:
            bad = connection.execute(
                f"SELECT COUNT(*) FROM {table} WHERE {column} NOT IN (0, 1)"
            ).fetchone()[0]
            if bad:
                problems.append(f"{table}.{column}: значения не 0/1 ({bad} шт.)")

    print("\nПроблем не найдено." if not problems else "\nНайдены проблемы:")
    for problem in problems:
        print(f"  - {problem}")
    return problems


if __name__ == "__main__":
    sys.exit(1 if inspect() else 0)
