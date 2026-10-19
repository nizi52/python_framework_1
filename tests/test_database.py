"""Проверка базы SQLite (ПР7): таблицы, ключи, перенос данных, запросы."""

import json
import sqlite3

import pytest

from db.database import BASE_DIR, fetch_all, fetch_one, get_connection


def json_count(name: str) -> int:
    with open(BASE_DIR / "data" / name, encoding="utf-8") as file:
        return len(json.load(file))


def test_tables_created():
    names = {row["name"] for row in fetch_all("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"users", "organizations", "domains", "resources", "rentals"} <= names


def test_foreign_keys_declared():
    conn = get_connection()
    refs = {row["table"] for row in conn.execute("PRAGMA foreign_key_list(rentals)")}
    conn.close()
    assert refs == {"users", "domains"}


def test_all_json_rows_imported():
    for table in ("users", "organizations", "domains", "resources", "rentals"):
        count = fetch_one(f"SELECT COUNT(*) AS n FROM {table}")["n"]
        assert count == json_count(f"{table}.json"), table


def test_foreign_key_check_is_on():
    conn = get_connection()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO resources (name, kind, domain_id) VALUES (?, ?, ?)", ["x", "DNS", 9999]
        )
    conn.close()


def test_rows_are_named():
    row = fetch_one("SELECT id, name FROM domains WHERE id = ?", [1])
    assert isinstance(row, sqlite3.Row)
    assert row["name"] == "example.ru"


def test_queries_file_has_required_kinds():
    text = (BASE_DIR / "sql" / "queries.sql").read_text(encoding="utf-8").upper()
    statements = [s for s in text.split(";") if "SELECT" in s]
    assert len(statements) >= 10
    for keyword in ("WHERE", "JOIN", "GROUP BY"):
        assert sum(keyword in s for s in statements) >= 2, keyword
    aggregates = ("COUNT(", "AVG(", "MIN(", "MAX(", "SUM(")
    assert sum(any(f in s for f in aggregates) for s in statements) >= 2
    assert "HAVING" in text


def test_queries_file_runs():
    conn = sqlite3.connect(":memory:")
    conn.executescript((BASE_DIR / "sql" / "schema.sql").read_text(encoding="utf-8"))
    lines = (BASE_DIR / "sql" / "queries.sql").read_text(encoding="utf-8").splitlines()
    script = "\n".join(line for line in lines if not line.startswith("."))
    for statement in script.split(";"):
        if statement.strip():
            conn.execute(statement)
    conn.close()
