import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models import Domain, Organization, User  # noqa: E402
from models.domains import filter_domains_by_organization  # noqa: E402
from models.organizations import (  # noqa: E402
    add_organization,
    find_organization,
    find_organization_by_id,
)


def test_organization_creation_and_str():
    org = Organization(1, "ООО Ромашка")
    assert org.id == 1
    assert str(org) == "ООО Ромашка"


def test_organization_from_data():
    org = Organization.from_data({"id": 3, "name": "ИП Петров"})
    assert org.id == 3
    assert org.name == "ИП Петров"


def test_add_and_find_organization():
    orgs = []
    add_organization(orgs, "ООО Ромашка")
    add_organization(orgs, "ИП Петров")
    assert [org.id for org in orgs] == [1, 2]
    assert find_organization(orgs, "ромашка")[0].id == 1
    assert find_organization_by_id(orgs, 2).name == "ИП Петров"
    assert find_organization_by_id(orgs, 99) is None


def test_filter_domains_by_organization():
    owner = User(1, "Иванов И.И.", "ivanov@example.com")
    org_a = Organization(1, "A")
    org_b = Organization(2, "B")
    domains = [
        Domain(1, "a.ru", org_a, date(2030, 1, 1), owner),
        Domain(2, "b.ru", org_b, date(2030, 1, 1), owner),
    ]
    assert [d.id for d in filter_domains_by_organization(domains, 1)] == [1]
