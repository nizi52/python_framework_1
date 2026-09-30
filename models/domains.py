"""Класс Domain и функции для работы с коллекцией доменов."""

from datetime import date
from typing import List, Optional

from .users import User


class Domain:
    """Доменное имя, зарегистрированное за организацией и владельцем."""

    def __init__(
        self,
        domain_id: int,
        name: str,
        organization: str,
        registration_end: date,
        owner: User,
    ) -> None:
        """Создать объект домена."""
        self.id = domain_id
        self.name = name
        self.organization = organization
        self.registration_end = registration_end
        self.owner = owner
        self.is_removed = False

    def is_active(self) -> bool:
        """Проверить, активен ли домен на текущую дату."""
        return not self.is_removed and self.registration_end >= date.today()

    def renew(self, new_end_date: date) -> None:
        """Продлить регистрацию, установив новый срок действия."""
        self.registration_end = new_end_date

    def remove(self) -> None:
        """Исключить домен из активного использования.

        Домен не удаляется из коллекции — его история сохраняется,
        как и отменённое бронирование в сквозном примере.
        """
        self.is_removed = True

    def __str__(self) -> str:
        """Вернуть строковое представление домена."""
        status = "активен" if self.is_active() else "неактивен"
        return (
            f"{self.name} | организация: {self.organization} | "
            f"владелец: {self.owner.name} | до {self.registration_end} | {status}"
        )


def add_domain(
    domains: List[Domain],
    name: str,
    organization: str,
    registration_end: date,
    owner: User,
) -> Domain:
    """Создать объект Domain и добавить его в коллекцию."""
    new_id = max((domain.id for domain in domains), default=0) + 1
    domain = Domain(new_id, name, organization, registration_end, owner)
    domains.append(domain)
    return domain


def find_domain(domains: List[Domain], query: str) -> List[Domain]:
    """Найти домены по подстроке в названии или организации."""
    query_lower = query.lower()
    return [
        domain
        for domain in domains
        if query_lower in domain.name.lower() or query_lower in domain.organization.lower()
    ]


def find_domain_by_id(domains: List[Domain], domain_id: int) -> Optional[Domain]:
    """Найти домен по идентификатору."""
    for domain in domains:
        if domain.id == domain_id:
            return domain
    return None


def filter_domains_by_organization(domains: List[Domain], organization: str) -> List[Domain]:
    """Отобрать домены, закреплённые за указанной организацией."""
    return [domain for domain in domains if domain.organization.lower() == organization.lower()]


def sort_domains_by_expiration(domains: List[Domain]) -> List[Domain]:
    """Вернуть домены, отсортированные по сроку окончания регистрации."""
    return sorted(domains, key=lambda domain: domain.registration_end)


def renew_domain(domains: List[Domain], domain_id: int, new_end_date: date) -> bool:
    """Найти домен по id и продлить его регистрацию."""
    domain = find_domain_by_id(domains, domain_id)
    if domain is None:
        return False
    domain.renew(new_end_date)
    return True


def remove_domain(domains: List[Domain], domain_id: int) -> bool:
    """Найти домен по id и пометить его удалённым."""
    domain = find_domain_by_id(domains, domain_id)
    if domain is None:
        return False
    domain.remove()
    return True


def get_domain_status(domain: Domain) -> str:
    """Вернуть текстовый статус домена (функция из ПР1, адаптирована к объекту)."""
    if domain.is_active():
        return "Домен активен"
    return "Домен истёк"


def domain_statistics(domains: List[Domain]) -> dict:
    """Собрать статистику по реестру: активные/истёкшие домены и средний
    остаток дней до окончания срока среди активных доменов.
    """
    active = [domain for domain in domains if domain.is_active()]
    days_left = [(domain.registration_end - date.today()).days for domain in active]
    average_days_left = sum(days_left) / len(days_left) if days_left else 0
    return {
        "total": len(domains),
        "active": len(active),
        "expired": len(domains) - len(active),
        "average_days_left": round(average_days_left, 1),
    }


def show_domains(domains: List[Domain]) -> None:
    """Вывести список доменов, отсортированный по сроку регистрации."""
    if not domains:
        print("Реестр пуст.")
        return
    for domain in sort_domains_by_expiration(domains):
        print(f"[{domain.id}] {domain}")
