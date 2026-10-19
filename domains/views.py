"""Представления приложения domains: список доменов и страница домена.

Данные загружаются из JSON средствами ПР3 (storage.py, пакет models/),
view-функции готовят контекст, а HTML формирует шаблон (ПР6).
"""

from typing import Tuple

from django.shortcuts import render
from django.urls import reverse

from homepage.views import load_data, not_found
from models import Domain
from models.domains import find_domain_by_id
from models.resources import filter_resources_by_domain


def get_status_label(domain: Domain) -> Tuple[str, str]:
    """Вернуть текст статуса домена и класс бейджа Bootstrap."""
    if domain.is_removed:
        return "удалён", "bg-secondary"
    if domain.is_active():
        return "активен", "bg-success"
    return "истёк", "bg-danger"


def with_status(domain: Domain) -> dict:
    """Упаковать домен вместе с его статусом для передачи в шаблон."""
    status, css = get_status_label(domain)
    return {"domain": domain, "status": status, "css": css}


def domain_list(request):
    """Страница /domains/: таблица доменов из data/domains.json."""
    rows = [with_status(domain) for domain in load_data().domains]
    context = {"title": "Домены", "rows": rows}
    return render(request, "domains/domain_list.html", context)


def domain_detail(request, domain_id):
    """Страница /domains/<id>/: карточка домена или 404, если не найден."""
    data = load_data()
    domain = find_domain_by_id(data.domains, domain_id)

    if domain is None:
        return not_found(
            request, "Домен не найден", reverse("domains:list"), "← к списку доменов"
        )

    context = {
        "title": domain.name,
        "item": with_status(domain),
        "resources": filter_resources_by_domain(data.resources, domain.id),
        "rentals": [rental for rental in data.rentals if rental.domain.id == domain.id],
    }
    return render(request, "domains/domain_detail.html", context)
