"""Проверка переноса данных из исходной базы ПР7 в Django ORM (ПР9)."""

import hashlib
import shutil
import sqlite3
from datetime import date

import pytest

from db.import_sqlite_to_orm import import_from_sqlite
from db.inspect_source_db import inspect
from domains.models import Domain
from organizations.models import Organization
from rentals.models import Rental
from resources.models import Resource
from users.models import User
from conftest import TEST_DB


def source_rows(table):
    conn = sqlite3.connect(TEST_DB)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(f"SELECT * FROM {table} ORDER BY id").fetchall()
    finally:
        conn.close()


def test_counts_match_source(orm_data):
    assert orm_data == {
        "users": len(source_rows("users")),
        "organizations": len(source_rows("organizations")),
        "domains": len(source_rows("domains")),
        "resources": len(source_rows("resources")),
        "rentals": len(source_rows("rentals")),
    }


def test_ids_fields_and_links_are_preserved(orm_data):
    for row in source_rows("domains"):
        domain = Domain.objects.get(pk=row["id"])
        assert domain.name == row["name"]
        assert domain.organization_id == row["organization_id"]
        assert domain.owner_id == row["owner_id"]
        assert domain.registration_end == date.fromisoformat(row["registration_end"])
        assert domain.is_removed == bool(row["is_removed"])
    for row in source_rows("rentals"):
        rental = Rental.objects.get(pk=row["id"])
        assert (rental.user_id, rental.domain_id) == (row["user_id"], row["domain_id"])
        assert rental.is_cancelled == bool(row["is_cancelled"])
    for row in source_rows("resources"):
        resource = Resource.objects.get(pk=row["id"])
        assert (resource.name, resource.kind, resource.domain_id) == (
            row["name"],
            row["kind"],
            row["domain_id"],
        )
    assert User.objects.count() == len(source_rows("users"))
    assert Organization.objects.count() == len(source_rows("organizations"))


def test_import_is_repeatable(orm_data):
    again = import_from_sqlite(TEST_DB)
    assert again == orm_data


def test_source_database_is_not_modified(db):
    before = hashlib.sha256(TEST_DB.read_bytes()).hexdigest()
    import_from_sqlite(TEST_DB)
    assert hashlib.sha256(TEST_DB.read_bytes()).hexdigest() == before


def test_missing_source_raises(db, tmp_path):
    with pytest.raises(FileNotFoundError):
        import_from_sqlite(tmp_path / "nope.sqlite")


def test_inspect_finds_no_problems_in_good_source(capsys):
    assert inspect(TEST_DB) == []
    out = capsys.readouterr().out
    assert "Таблица: domains" in out and "Проблем не найдено." in out


def test_inspect_detects_broken_reference_and_date(tmp_path, capsys):
    broken = tmp_path / "broken.sqlite"
    shutil.copy(TEST_DB, broken)
    conn = sqlite3.connect(broken)
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("UPDATE resources SET domain_id = 9999 WHERE id = 1")
    conn.execute("UPDATE domains SET registration_end = 'вчера' WHERE id = 1")
    conn.commit()
    conn.close()
    problems = inspect(broken)
    assert any("resources.domain_id" in p for p in problems)
    assert any("registration_end" in p for p in problems)
