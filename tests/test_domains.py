import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from domains import add_domain, find_domain  # noqa: E402
from registrations import get_domain_status, is_domain_active  # noqa: E402


def test_add_domain():
    domains = {}
    add_domain(domains, "example.ru", "Иванов И.И.", "ООО Ромашка", date(2026, 12, 31))
    assert len(domains) == 1


def test_find_domain():
    domains = {}
    add_domain(domains, "example.ru", "Иванов И.И.", "ООО Ромашка", date(2026, 12, 31))
    assert find_domain(domains, "example")


def test_is_domain_active_true():
    assert is_domain_active(date.today() + timedelta(days=10))


def test_is_domain_active_false():
    assert not is_domain_active(date.today() - timedelta(days=1))


def test_get_domain_status():
    assert get_domain_status(True) == "Домен активен"
    assert get_domain_status(False) == "Домен истёк"
