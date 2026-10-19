"""Подключение к базе данных SQLite проекта.

Путь к файлу базы можно переопределить переменной окружения DOMAINREG_DB
(используется в тестах, чтобы не трогать рабочую базу).
"""

import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.environ.get("DOMAINREG_DB", BASE_DIR / "data" / "domainreg.sqlite"))
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """Открыть соединение: проверка внешних ключей и доступ к полям по имени."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    """Создать таблицы по скрипту sql/schema.sql (IF NOT EXISTS – повторно безопасно)."""
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def fetch_all(query: str, params=()) -> list:
    """Выполнить SELECT с параметрами ? и вернуть все строки (sqlite3.Row)."""
    conn = get_connection()
    try:
        return conn.execute(query, params).fetchall()
    finally:
        conn.close()


def fetch_one(query: str, params=()):
    """Выполнить SELECT с параметрами ? и вернуть одну строку или None."""
    conn = get_connection()
    try:
        return conn.execute(query, params).fetchone()
    finally:
        conn.close()
