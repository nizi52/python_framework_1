"""Перенос данных из исходной базы ПР7 (data/domainreg.sqlite) в базу Django (db.sqlite3).

Стратегия ПР9: исходная база остаётся источником и не изменяется, а Django
работает со своей базой, где таблицы создаются миграциями. Идентификаторы записей
сохраняются, поэтому связи не теряются. Перенос идёт одной транзакцией в порядке
зависимостей: пользователи, организации, домены, ресурсы, аренды.

Миграции должны быть применены заранее. Запуск из корня проекта:
    python manage.py migrate
    python db/import_sqlite_to_orm.py

Повторный запуск безопасен: записи ищутся по первичному ключу и обновляются.
Записи целевой базы, которых нет в источнике, не удаляются.
"""

import os
import sqlite3
import sys
from datetime import date
from pathlib import Path

import django
from django.db import transaction

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "domainreg.settings")
django.setup()

from db.database import DB_PATH  # noqa: E402
from domains.models import Domain  # noqa: E402
from organizations.models import Organization  # noqa: E402
from rentals.models import Rental  # noqa: E402
from resources.models import Resource  # noqa: E402
from users.models import User  # noqa: E402


def read_rows(connection: sqlite3.Connection, table: str) -> list:
    # Имя таблицы берётся из фиксированного списка ниже, а не от пользователя.
    return connection.execute(f"SELECT * FROM {table} ORDER BY id").fetchall()


def import_from_sqlite(source_db: Path = DB_PATH) -> dict:
    """Перенести данные в базу Django и вернуть количество записей по моделям."""
    if not Path(source_db).exists():
        raise FileNotFoundError(f"Исходная база не найдена: {source_db}")

    with sqlite3.connect(f"file:{source_db}?mode=ro", uri=True) as connection:
        connection.row_factory = sqlite3.Row
        users = read_rows(connection, "users")
        organizations = read_rows(connection, "organizations")
        domains = read_rows(connection, "domains")
        resources = read_rows(connection, "resources")
        rentals = read_rows(connection, "rentals")

    with transaction.atomic():
        for row in users:
            User.objects.update_or_create(
                pk=row["id"], defaults={"name": row["name"], "email": row["email"]}
            )
        for row in organizations:
            Organization.objects.update_or_create(pk=row["id"], defaults={"name": row["name"]})
        for row in domains:
            Domain.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "organization_id": row["organization_id"],
                    "owner_id": row["owner_id"],
                    "registration_end": date.fromisoformat(row["registration_end"]),
                    "is_removed": bool(row["is_removed"]),
                },
            )
        for row in resources:
            Resource.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "kind": row["kind"],
                    "domain_id": row["domain_id"],
                },
            )
        for row in rentals:
            Rental.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "user_id": row["user_id"],
                    "domain_id": row["domain_id"],
                    "start_date": date.fromisoformat(row["start_date"]),
                    "end_date": date.fromisoformat(row["end_date"]),
                    "status": (
                        Rental.Status.CANCELLED if row["is_cancelled"] else Rental.Status.ACTIVE
                    ),
                },
            )

    return {
        "users": User.objects.count(),
        "organizations": Organization.objects.count(),
        "domains": Domain.objects.count(),
        "resources": Resource.objects.count(),
        "rentals": Rental.objects.count(),
    }


def main() -> None:
    counts = import_from_sqlite()
    print("Перенос данных завершён.")
    for name, count in counts.items():
        print(f"  {name}: {count}")


if __name__ == "__main__":
    main()
