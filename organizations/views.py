"""Представления приложения organizations: список и страница организации."""

from django.shortcuts import render
from django.urls import reverse

from domains.views import with_status
from homepage.views import load_data, not_found
from models.domains import filter_domains_by_organization
from models.organizations import find_organization_by_id


def organization_list(request):
    """Страница /organizations/: список организаций с их доменами."""
    data = load_data()
    rows = [
        {
            "organization": organization,
            "domains": filter_domains_by_organization(data.domains, organization.id),
        }
        for organization in data.organizations
    ]
    return render(
        request, "organizations/organization_list.html", {"title": "Организации", "rows": rows}
    )


def organization_detail(request, organization_id):
    """Страница /organizations/<id>/: карточка организации или 404."""
    data = load_data()
    organization = find_organization_by_id(data.organizations, organization_id)

    if organization is None:
        return not_found(
            request,
            "Организация не найдена",
            reverse("organizations:list"),
            "← к списку организаций",
        )

    domains = filter_domains_by_organization(data.domains, organization.id)
    context = {
        "title": organization.name,
        "organization": organization,
        "domains": [with_status(domain) for domain in domains],
    }
    return render(request, "organizations/organization_detail.html", context)
