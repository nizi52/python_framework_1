"""Представления приложения organizations: список и страница организации."""

from django.http import HttpResponse
from django.utils.html import escape

from domains.views import get_status_label
from homepage.views import DATE_FORMAT, badge, load_data, not_found_page, page
from models.domains import filter_domains_by_organization
from models.organizations import find_organization_by_id


def organizations(request):
    """Страница /organizations/: список организаций с числом доменов."""
    data = load_data()
    rows = ""
    for organization in data.organizations:
        count = len(filter_domains_by_organization(data.domains, organization.id))
        rows += f"""
        <tr>
            <td><a href="/organizations/{organization.id}/">{escape(organization.name)}</a></td>
            <td>{count}</td>
        </tr>
        """

    if rows:
        body = f"""
        <div class="table-responsive">
            <table class="table table-hover table-dark">
                <thead>
                    <tr><th>Организация</th><th>Доменов</th></tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """
    else:
        body = '<p class="text-muted">Организаций пока нет.</p>'

    return HttpResponse(page("Организации", f"<h1>Организации</h1>{body}"))


def organization_detail(request, organization_id):
    """Страница /organizations/<id>/: карточка организации или 404."""
    data = load_data()
    organization = find_organization_by_id(data.organizations, organization_id)

    if organization is None:
        return not_found_page(
            "Организация не найдена", "/organizations/", "← к списку организаций"
        )

    items = ""
    for domain in filter_domains_by_organization(data.domains, organization.id):
        status, css = get_status_label(domain)
        items += f"""
        <li>
            <a href="/domains/{domain.id}/">{escape(domain.name)}</a>
            – до {domain.registration_end.strftime(DATE_FORMAT)} {badge(status, css)}
        </li>
        """
    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{escape(organization.name)}</h5>
            <p class="card-text"><strong>ID:</strong> {organization.id}</p>
            <p class="card-text"><strong>Домены организации:</strong></p>
            <ul>{items or "<li>нет</li>"}</ul>
            <a href="/organizations/" class="btn btn-outline-secondary">
                ← к списку организаций
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(organization.name, content))
