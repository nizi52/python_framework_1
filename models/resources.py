"""Класс Resource и функции для работы с ресурсами доменов."""

from typing import List, Optional

from .domains import Domain


class Resource:
    """Ресурс, привязанный к домену: хостинг, SSL-сертификат, почта, DNS."""

    def __init__(self, resource_id: int, name: str, kind: str, domain: Domain) -> None:
        """Создать объект ресурса."""
        self.id = resource_id
        self.name = name
        self.kind = kind
        self.domain = domain

    def is_active(self) -> bool:
        """Ресурс доступен, пока активен домен, к которому он привязан."""
        return self.domain.is_active()

    def __str__(self) -> str:
        """Вернуть строковое представление ресурса."""
        status = "активен" if self.is_active() else "неактивен"
        return f"{self.name} ({self.kind}) | домен: {self.domain.name} | {status}"


def add_resource(resources: List[Resource], name: str, kind: str, domain: Domain) -> Resource:
    """Создать объект Resource и добавить его в коллекцию."""
    new_id = max((resource.id for resource in resources), default=0) + 1
    resource = Resource(new_id, name, kind, domain)
    resources.append(resource)
    return resource


def find_resource_by_id(resources: List[Resource], resource_id: int) -> Optional[Resource]:
    """Найти ресурс по идентификатору."""
    for resource in resources:
        if resource.id == resource_id:
            return resource
    return None


def filter_resources_by_domain(resources: List[Resource], domain_id: int) -> List[Resource]:
    """Отобрать ресурсы, привязанные к домену."""
    return [resource for resource in resources if resource.domain.id == domain_id]


def show_resources(resources: List[Resource]) -> None:
    """Вывести список ресурсов."""
    if not resources:
        print("Ресурсов нет.")
        return
    for resource in resources:
        print(f"[{resource.id}] {resource}")
