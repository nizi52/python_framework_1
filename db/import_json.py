"""Перенос данных проекта из JSON-файлов каталога data/ в базу SQLite.

Запуск из корня проекта:
    python -m db.import_json

Скрипт создаёт таблицы (если их нет), очищает их и заново заполняет
данными из JSON, поэтому его можно запускать повторно.
"""

import json

from db.database import BASE_DIR, DB_PATH, create_schema, get_connection

DATA_DIR = BASE_DIR / "data"

# Порядок важен из-за внешних ключей: сначала справочники, потом зависимые таблицы.
TABLES_IN_ORDER = ["users", "organizations", "domains", "resources", "rentals"]


def load_json(filename: str) -> list:
    """Прочитать список записей из JSON-файла каталога data/."""
    with open(DATA_DIR / filename, encoding="utf-8") as file:
        return json.load(file)


def import_users(conn) -> None:
    conn.executemany(
        "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
        [(u["id"], u["name"], u["email"]) for u in load_json("users.json")],
    )


def import_organizations(conn) -> None:
    conn.executemany(
        "INSERT INTO organizations (id, name) VALUES (?, ?)",
        [(o["id"], o["name"]) for o in load_json("organizations.json")],
    )


def import_domains(conn) -> None:
    conn.executemany(
        """
        INSERT INTO domains (id, name, organization_id, owner_id, registration_end, is_removed)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                d["id"],
                d["name"],
                d["organization_id"],
                d["owner_id"],
                d["registration_end"],
                int(d.get("is_removed", False)),
            )
            for d in load_json("domains.json")
        ],
    )


def import_resources(conn) -> None:
    conn.executemany(
        "INSERT INTO resources (id, name, kind, domain_id) VALUES (?, ?, ?, ?)",
        [(r["id"], r["name"], r["kind"], r["domain_id"]) for r in load_json("resources.json")],
    )


def import_rentals(conn) -> None:
    conn.executemany(
        """
        INSERT INTO rentals (id, user_id, domain_id, start_date, end_date, is_cancelled)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                r["id"],
                r["user_id"],
                r["domain_id"],
                r["start_date"],
                r["end_date"],
                int(r.get("is_cancelled", False)),
            )
            for r in load_json("rentals.json")
        ],
    )


def main() -> None:
    conn = get_connection()
    try:
        create_schema(conn)
        for table in reversed(TABLES_IN_ORDER):
            conn.execute(f"DELETE FROM {table}")  # имя таблицы из константы, не от пользователя
        import_users(conn)
        import_organizations(conn)
        import_domains(conn)
        import_resources(conn)
        import_rentals(conn)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    print(f"Данные перенесены в {DB_PATH}")


if __name__ == "__main__":
    main()
