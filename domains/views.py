"""Представления приложения domains: список доменов и страница домена.

Данные загружаются из JSON средствами ПР3 (storage.py, пакет models/),
view-функции только готовят HTML-ответ.
"""

from typing import Tuple

from django.http import HttpResponse
from django.utils.html import escape

from homepage.views import DATE_FORMAT, badge, load_data, not_found_page, page
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


def domains(request):
    """Страница /domains/: таблица доменов из data/domains.json."""
    rows = ""
    for domain in load_data().domains:
        status, css = get_status_label(domain)
        rows += f"""
        <tr>
            <td><a href="/domains/{domain.id}/">{escape(domain.name)}</a></td>
            <td>
                <a href="/organizations/{domain.organization.id}/">
                    {escape(domain.organization.name)}
                </a>
            </td>
            <td>{escape(domain.owner.name)}</td>
            <td>{domain.registration_end.strftime(DATE_FORMAT)}</td>
            <td>{badge(status, css)}</td>
        </tr>
        """

    if rows:
        body = f"""
        <div class="table-responsive">
            <table class="table table-hover table-dark">
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
    data = load_data()
    domain = find_domain_by_id(data.domains, domain_id)

    if domain is None:
        return not_found_page("Домен не найден", "/domains/", "← к списку доменов")

    status, css = get_status_label(domain)
    resources = "".join(
        f'<li><a href="/resources/{r.id}/">{escape(r.name)}</a> ({escape(r.kind)})</li>'
        for r in filter_resources_by_domain(data.resources, domain.id)
    )
    rentals = "".join(
        f'<li><a href="/rentals/{r.id}/">Аренда №{r.id}</a>: {escape(r.user.name)}, '
        f"{r.start_date.strftime(DATE_FORMAT)} – {r.end_date.strftime(DATE_FORMAT)}</li>"
        for r in data.rentals
        if r.domain.id == domain.id
    )
    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{escape(domain.name)}</h5>
            <p class="card-text">
                <strong>ID:</strong> {domain.id}
            </p>
            <p class="card-text">
                <strong>Организация:</strong>
                <a href="/organizations/{domain.organization.id}/">
                    {escape(domain.organization.name)}
                </a>
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
                Статус на текущую дату: {badge(status, css)}
            </p>
            <p class="card-text"><strong>Ресурсы:</strong></p>
            <ul>{resources or "<li>нет</li>"}</ul>
            <p class="card-text"><strong>Аренда:</strong></p>
            <ul>{rentals or "<li>нет</li>"}</ul>
            <a href="/domains/" class="btn btn-outline-secondary">
                ← к списку доменов
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(domain.name, content), status=200)
