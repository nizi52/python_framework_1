"""Класс Organization и функции для работы с коллекцией организаций."""

from typing import List, Optional


class Organization:
    """Организация, за которой закрепляются домены."""

    def __init__(self, organization_id: int, name: str) -> None:
        """Создать объект организации."""
        self.id = organization_id
        self.name = name

    def __str__(self) -> str:
        """Вернуть строковое представление организации."""
        return self.name

    @classmethod
    def from_data(cls, data: dict) -> "Organization":
        """Создать организацию из словаря данных (например, из JSON)."""
        return cls(data["id"], data["name"])


def add_organization(organizations: List[Organization], name: str) -> Organization:
    """Создать объект Organization и добавить его в коллекцию."""
    new_id = max((org.id for org in organizations), default=0) + 1
    organization = Organization(new_id, name)
    organizations.append(organization)
    return organization


def find_organization(organizations: List[Organization], query: str) -> List[Organization]:
    """Найти организации по подстроке в названии."""
    query_lower = query.lower()
    return [org for org in organizations if query_lower in org.name.lower()]


def find_organization_by_id(
    organizations: List[Organization], organization_id: int
) -> Optional[Organization]:
    """Найти организацию по идентификатору."""
    for organization in organizations:
        if organization.id == organization_id:
            return organization
    return None


def show_organizations(organizations: List[Organization]) -> None:
    """Вывести список организаций."""
    if not organizations:
        print("Организаций нет.")
        return
    for organization in organizations:
        print(f"[{organization.id}] {organization}")
