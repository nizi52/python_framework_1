"""Загрузка и сохранение данных приложения в JSON-файлах.

JSON остаётся форматом хранения данных: при загрузке словари
превращаются в объекты предметной области, при сохранении — обратно
в словари. Связи между объектами хранятся как идентификаторы
(owner_id, organization_id, domain_id, user_id), а не как вложенные
объекты.
"""

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import List, Optional

from models import Domain, Organization, Rental, Resource, User
from models.domains import find_domain_by_id
from models.organizations import find_organization_by_id
from models.users import find_user_by_id


def _read_json(filename: str, title: str) -> Optional[list]:
    """Прочитать JSON-список из файла; при ошибке вернуть None."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Файл {filename} не найден, будет создан новый список ({title}).")
    except json.JSONDecodeError:
        print(f"Файл {filename} повреждён, будет создан новый список ({title}).")
    return None


def _write_json(filename: str, raw_items: list) -> None:
    """Записать список словарей в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(raw_items, file, ensure_ascii=False, indent=2)


def load_users(filename: str) -> List[User]:
    """Загрузить пользователей из JSON-файла."""
    raw_users = _read_json(filename, "пользователи")
    return [User.from_data(item) for item in raw_users or []]


def save_users(filename: str, users: List[User]) -> None:
    """Сохранить пользователей в JSON-файл."""
    _write_json(filename, [{"id": u.id, "name": u.name, "email": u.email} for u in users])


def load_organizations(filename: str) -> List[Organization]:
    """Загрузить организации из JSON-файла."""
    raw_organizations = _read_json(filename, "организации")
    return [Organization.from_data(item) for item in raw_organizations or []]


def save_organizations(filename: str, organizations: List[Organization]) -> None:
    """Сохранить организации в JSON-файл."""
    _write_json(filename, [{"id": org.id, "name": org.name} for org in organizations])


def load_domains(
    filename: str, users: List[User], organizations: List[Organization]
) -> List[Domain]:
    """Загрузить домены из JSON-файла, восстановив связи с владельцем и организацией."""
    domains: List[Domain] = []
    for item in _read_json(filename, "домены") or []:
        owner = find_user_by_id(users, item["owner_id"])
        organization = find_organization_by_id(organizations, item["organization_id"])
        if owner is None or organization is None:
            print(f"Домен {item['name']} пропущен: владелец или организация не найдены.")
            continue
        domain = Domain(
            domain_id=item["id"],
            name=item["name"],
            organization=organization,
            registration_end=date.fromisoformat(item["registration_end"]),
            owner=owner,
        )
        domain.is_removed = item.get("is_removed", False)
        domains.append(domain)
    return domains


def save_domains(filename: str, domains: List[Domain]) -> None:
    """Сохранить домены в JSON-файл (связи — по идентификаторам)."""
    _write_json(
        filename,
        [
            {
                "id": domain.id,
                "name": domain.name,
                "organization_id": domain.organization.id,
                "registration_end": domain.registration_end.isoformat(),
                "owner_id": domain.owner.id,
                "is_removed": domain.is_removed,
            }
            for domain in domains
        ],
    )


def load_resources(filename: str, domains: List[Domain]) -> List[Resource]:
    """Загрузить ресурсы из JSON-файла, восстановив связь с доменом."""
    resources: List[Resource] = []
    for item in _read_json(filename, "ресурсы") or []:
        domain = find_domain_by_id(domains, item["domain_id"])
        if domain is None:
            print(f"Ресурс {item['name']} пропущен: домен не найден.")
            continue
        resources.append(Resource(item["id"], item["name"], item["kind"], domain))
    return resources


def save_resources(filename: str, resources: List[Resource]) -> None:
    """Сохранить ресурсы в JSON-файл (домен — по идентификатору)."""
    _write_json(
        filename,
        [
            {"id": r.id, "name": r.name, "kind": r.kind, "domain_id": r.domain.id}
            for r in resources
        ],
    )


def load_rentals(filename: str, users: List[User], domains: List[Domain]) -> List[Rental]:
    """Загрузить аренды из JSON-файла, восстановив связи с пользователем и доменом."""
    rentals: List[Rental] = []
    for item in _read_json(filename, "аренды") or []:
        user = find_user_by_id(users, item["user_id"])
        domain = find_domain_by_id(domains, item["domain_id"])
        if user is None or domain is None:
            print(f"Аренда {item['id']} пропущена: пользователь или домен не найдены.")
            continue
        rental = Rental(
            rental_id=item["id"],
            user=user,
            domain=domain,
            start_date=date.fromisoformat(item["start_date"]),
            end_date=date.fromisoformat(item["end_date"]),
        )
        rental.is_cancelled = item.get("is_cancelled", False)
        rentals.append(rental)
    return rentals


def save_rentals(filename: str, rentals: List[Rental]) -> None:
    """Сохранить аренды в JSON-файл (связи — по идентификаторам)."""
    _write_json(
        filename,
        [
            {
                "id": rental.id,
                "user_id": rental.user.id,
                "domain_id": rental.domain.id,
                "start_date": rental.start_date.isoformat(),
                "end_date": rental.end_date.isoformat(),
                "is_cancelled": rental.is_cancelled,
            }
            for rental in rentals
        ],
    )


@dataclass
class Registry:
    """Все объекты предметной области, загруженные из каталога data/."""

    users: List[User]
    organizations: List[Organization]
    domains: List[Domain]
    resources: List[Resource]
    rentals: List[Rental]


def load_registry(data_dir: Path) -> Registry:
    """Загрузить все JSON-файлы каталога данных и связать объекты между собой."""
    users = load_users(str(data_dir / "users.json"))
    organizations = load_organizations(str(data_dir / "organizations.json"))
    domains = load_domains(str(data_dir / "domains.json"), users, organizations)
    resources = load_resources(str(data_dir / "resources.json"), domains)
    rentals = load_rentals(str(data_dir / "rentals.json"), users, domains)
    return Registry(users, organizations, domains, resources, rentals)
