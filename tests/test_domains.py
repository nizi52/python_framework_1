import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models import Domain, User  # noqa: E402
from models.domains import add_domain, find_domain, get_domain_status  # noqa: E402


def make_owner() -> User:
    return User(1, "Иванов И.И.", "ivanov@example.com")


def test_domain_creation_and_owner_link():
    owner = make_owner()
    domain = Domain(1, "example.ru", "ООО Ромашка", date(2026, 12, 31), owner)

    assert domain.id == 1
    assert domain.name == "example.ru"
    assert domain.owner is owner
    assert domain.owner.name == "Иванов И.И."


def test_domain_is_active_true():
    owner = make_owner()
    domain = Domain(1, "example.ru", "ООО Ромашка", date.today() + timedelta(days=10), owner)
    assert domain.is_active()


def test_domain_is_active_false_expired():
    owner = make_owner()
    domain = Domain(1, "example.ru", "ООО Ромашка", date.today() - timedelta(days=1), owner)
    assert not domain.is_active()


def test_domain_renew():
    owner = make_owner()
    domain = Domain(1, "example.ru", "ООО Ромашка", date.today() - timedelta(days=1), owner)
    domain.renew(date.today() + timedelta(days=30))
    assert domain.is_active()


def test_domain_remove_keeps_history():
    owner = make_owner()
    domain = Domain(1, "example.ru", "ООО Ромашка", date.today() + timedelta(days=10), owner)
    domain.remove()
    assert domain.is_removed
    assert not domain.is_active()


def test_add_domain_and_find():
    owner = make_owner()
    domains = []
    add_domain(domains, "example.ru", "ООО Ромашка", date(2026, 12, 31), owner)
    assert len(domains) == 1
    assert find_domain(domains, "example")
    assert find_domain(domains, "ромашка")


def test_get_domain_status():
    owner = make_owner()
    active = Domain(1, "a.ru", "Org", date.today() + timedelta(days=5), owner)
    expired = Domain(2, "b.ru", "Org", date.today() - timedelta(days=5), owner)

    assert get_domain_status(active) == "Домен активен"
    assert get_domain_status(expired) == "Домен истёк"
