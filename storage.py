"""Загрузка и сохранение доменов и пользователей в JSON-файлах.

JSON остаётся форматом хранения данных: при загрузке словари
превращаются в объекты Domain/User, при сохранении — обратно
в словари. Связь домена с владельцем хранится как owner_id,
а не как вложенный объект.
"""

import json
from datetime import date
from typing import List

from models import Domain, User
from models.users import find_user_by_id


def load_users(filename: str) -> List[User]:
    """Загрузить пользователей из JSON-файла."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            raw_users = json.load(file)
    except FileNotFoundError:
        print(f"Файл {filename} не найден, будет создан новый список пользователей.")
        return []
    except json.JSONDecodeError:
        print(f"Файл {filename} повреждён, будет создан новый список пользователей.")
        return []
    return [User.from_data(item) for item in raw_users]


def save_users(filename: str, users: List[User]) -> None:
    """Сохранить пользователей в JSON-файл."""
    raw_users = [{"id": user.id, "name": user.name, "email": user.email} for user in users]
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(raw_users, file, ensure_ascii=False, indent=2)


def load_domains(filename: str, users: List[User]) -> List[Domain]:
    """Загрузить домены из JSON-файла, восстановив связь с владельцем."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            raw_domains = json.load(file)
    except FileNotFoundError:
        print(f"Файл {filename} не найден, будет создан новый реестр доменов.")
        return []
    except json.JSONDecodeError:
        print(f"Файл {filename} повреждён, будет создан новый реестр доменов.")
        return []

    domains: List[Domain] = []
    for item in raw_domains:
        owner = find_user_by_id(users, item["owner_id"])
        if owner is None:
            print(f"Домен {item['name']} пропущен: владелец не найден.")
            continue
        domain = Domain(
            domain_id=item["id"],
            name=item["name"],
            organization=item["organization"],
            registration_end=date.fromisoformat(item["registration_end"]),
            owner=owner,
        )
        domain.is_removed = item.get("is_removed", False)
        domains.append(domain)
    return domains


def save_domains(filename: str, domains: List[Domain]) -> None:
    """Сохранить домены в JSON-файл (владелец — по идентификатору)."""
    raw_domains = [
        {
            "id": domain.id,
            "name": domain.name,
            "organization": domain.organization,
            "registration_end": domain.registration_end.isoformat(),
            "owner_id": domain.owner.id,
            "is_removed": domain.is_removed,
        }
        for domain in domains
    ]
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(raw_domains, file, ensure_ascii=False, indent=2)
