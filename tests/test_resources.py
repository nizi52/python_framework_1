import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models import Domain, Organization, Resource, User  # noqa: E402
from models.resources import (  # noqa: E402
    add_resource,
    filter_resources_by_domain,
    find_resource_by_id,
)

OWNER = User(1, "Иванов И.И.", "ivanov@example.com")
ORG = Organization(1, "ООО Ромашка")


def make_domain(domain_id: int, days: int) -> Domain:
    return Domain(domain_id, f"d{domain_id}.ru", ORG, date.today() + timedelta(days=days), OWNER)


def test_resource_active_follows_domain():
    assert Resource(1, "Хостинг", "Хостинг", make_domain(1, 10)).is_active()
    assert not Resource(2, "Хостинг", "Хостинг", make_domain(2, -10)).is_active()


def test_add_find_and_filter_resources():
    first, second = make_domain(1, 10), make_domain(2, 10)
    resources = []
    add_resource(resources, "Хостинг", "Хостинг", first)
    add_resource(resources, "SSL", "SSL", first)
    add_resource(resources, "Почта", "Почта", second)

    assert [r.id for r in resources] == [1, 2, 3]
    assert find_resource_by_id(resources, 3).name == "Почта"
    assert find_resource_by_id(resources, 99) is None
    assert len(filter_resources_by_domain(resources, 1)) == 2


def test_resource_str_contains_domain():
    resource = Resource(1, "Хостинг", "Хостинг", make_domain(1, 10))
    assert "d1.ru" in str(resource)
