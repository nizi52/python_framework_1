"""Функции для работы с реестром доменов (сущность «домен»)."""

from datetime import date


def add_domain(
    domains: dict[int, dict],
    name: str,
    owner: str,
    organization: str,
    registration_end: date,
) -> int:
    """Добавить домен в словарь domains.

    Идентификатор формируется автоматически как следующий свободный
    номер. Возвращает id добавленного домена.
    """
    new_id = max(domains.keys(), default=0) + 1
    domains[new_id] = {
        "id": new_id,
        "name": name,
        "owner": owner,
        "organization": organization,
        "registration_end": registration_end,
    }
    return new_id


def find_domain(domains: dict[int, dict], query: str) -> dict[int, dict]:
    """Найти домены по подстроке в названии или организации."""
    query_lower = query.lower()
    return {
        domain_id: data
        for domain_id, data in domains.items()
        if query_lower in data["name"].lower()
        or query_lower in data["organization"].lower()
    }


def filter_domains_by_organization(
    domains: dict[int, dict], organization: str
) -> dict[int, dict]:
    """Отобрать домены, закреплённые за указанной организацией."""
    return {
        domain_id: data
        for domain_id, data in domains.items()
        if data["organization"].lower() == organization.lower()
    }
