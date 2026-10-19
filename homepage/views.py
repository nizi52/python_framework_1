"""Представления приложения homepage: главная страница и страницы 404.

Здесь же находятся вспомогательные функции, общие для всех приложений:
загрузка данных ПР3 и ответ «объект не найден». HTML-разметка страниц
вынесена в шаблоны каталога templates/ (ПР6).
"""

from django.conf import settings
from django.shortcuts import render

from storage import Registry, load_registry


def load_data() -> Registry:
    """Загрузить все данные ПР3 из каталога data/ (JSON -> объекты)."""
    return load_registry(settings.BASE_DIR / "data")


def not_found(request, title: str, back_url: str, back_text: str):
    """Страница «объект не найден» с кодом 404 и ссылкой назад к списку."""
    context = {"title": title, "back_url": back_url, "back_text": back_text}
    return render(request, "not_found.html", context, status=404)


def index(request):
    """Главная страница: описание приложения, разделы и краткая сводка."""
    data = load_data()
    active_domains = [domain for domain in data.domains if domain.is_active()]
    sections = [
        {"title": "Домены", "url": "domains:list", "items": data.domains},
        {"title": "Организации", "url": "organizations:list", "items": data.organizations},
        {"title": "Ресурсы", "url": "resources:list", "items": data.resources},
        {"title": "Аренда", "url": "rentals:list", "items": data.rentals},
    ]
    context = {
        "title": "Система учета доменных имен",
        "sections": sections,
        "active_domains": active_domains,
        "domains_total": len(data.domains),
    }
    return render(request, "homepage/index.html", context)


def page_not_found(request, exception):
    """Собственная страница 404 для любого адреса без маршрута."""
    return render(request, "404.html", {"title": "404 – страница не найдена"}, status=404)
