"""Представления приложения domains: список доменов и страница домена.

Данные загружаются из JSON средствами ПР3 (storage.py, пакет models/),
view-функции только готовят HTML-ответ.
"""

from typing import List

from django.conf import settings
from django.http import HttpResponse
from django.utils.html import escape

from homepage.views import page
from models import Domain
from models.domains import find_domain_by_id
from storage import load_domains, load_users

DOMAINS_FILE = str(settings.BASE_DIR / "data" / "domains.json")
USERS_FILE = str(settings.BASE_DIR / "data" / "users.json")
DATE_FORMAT = "%d.%m.%Y"


def load_all_domains() -> List[Domain]:
    """Загрузить домены вместе с владельцами (JSON -> объекты)."""
    users = load_users(USERS_FILE)
    return load_domains(DOMAINS_FILE, users)


def get_status_label(domain: Domain) -> tuple[str, str]:
    """Вернуть текст статуса домена и класс бейджа Bootstrap."""
    if domain.is_removed:
        return "удалён", "bg-secondary"
    if domain.is_active():
        return "активен", "bg-success"
    return "истёк", "bg-danger"


def domains(request):
    """Страница /domains/: таблица доменов из data/domains.json."""
    rows = ""
    for domain in load_all_domains():
        status, badge = get_status_label(domain)
        rows += f"""
        <tr>
            <td><a href="/domains/{domain.id}/">{escape(domain.name)}</a></td>
            <td>{escape(domain.organization)}</td>
            <td>{escape(domain.owner.name)}</td>
            <td>{domain.registration_end.strftime(DATE_FORMAT)}</td>
            <td><span class="badge {badge}">{status}</span></td>
        </tr>
        """

    if rows:
        body = f"""
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Домен</th>
                        <th>Организация</th>
                        <th>Владелец</th>
                        <th>Срок до</th>
                        <th>Статус</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """
    else:
        body = '<p class="text-muted">Реестр доменов пуст.</p>'

    content = f"<h1>Домены</h1>{body}"
    return HttpResponse(page("Система учета доменных имен – домены", content))


def domain_detail(request, domain_id):
    """Страница /domains/<id>/: карточка домена или 404, если не найден."""
    domain = find_domain_by_id(load_all_domains(), domain_id)

    if domain is None:
        content = """
        <h1 class="text-danger">Домен не найден</h1>
        <a href="/domains/" class="btn btn-outline-secondary">
            ← к списку доменов
        </a>
        """
        return HttpResponse(page("Домен не найден", content), status=404)

    status, badge = get_status_label(domain)
    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{escape(domain.name)}</h5>
            <p class="card-text">
                <strong>ID:</strong> {domain.id}
            </p>
            <p class="card-text">
                <strong>Организация:</strong> {escape(domain.organization)}
            </p>
            <p class="card-text">
                <strong>Владелец:</strong> {escape(domain.owner.name)}
                ({escape(domain.owner.email)})
            </p>
            <p class="card-text">
                <strong>Срок регистрации до:</strong>
                {domain.registration_end.strftime(DATE_FORMAT)}
            </p>
            <p class="card-text">
                Статус на текущую дату:
                <span class="badge {badge}">{status}</span>
            </p>
            <a href="/domains/" class="btn btn-outline-secondary">
                ← к списку доменов
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(domain.name, content), status=200)
