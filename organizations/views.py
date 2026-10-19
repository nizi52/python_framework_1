"""Представления приложения organizations: список и страница организации (SQLite, ПР7)."""

from django.shortcuts import render
from django.urls import reverse

from db.database import fetch_all, fetch_one
from domains.views import DOMAIN_COLUMNS, DOMAIN_JOINS
from homepage.views import not_found


def organization_list(request):
    """Страница /organizations/: организации и число их доменов (LEFT JOIN + GROUP BY)."""
    rows = fetch_all(
        """
        SELECT organizations.id,
               organizations.name,
               COUNT(domains.id) AS domains_count,
               GROUP_CONCAT(domains.name, ', ') AS domain_names
        FROM organizations
        LEFT JOIN domains ON domains.organization_id = organizations.id
        GROUP BY organizations.id, organizations.name
        ORDER BY organizations.name
        """
    )
    return render(
        request, "organizations/organization_list.html", {"title": "Организации", "rows": rows}
    )


def organization_detail(request, organization_id):
    """Страница /organizations/<id>/: карточка организации и её домены, или 404."""
    organization = fetch_one(
        "SELECT id, name FROM organizations WHERE id = ?", [organization_id]
    )
    if organization is None:
        return not_found(
            request,
            "Организация не найдена",
            reverse("organizations:list"),
            "← к списку организаций",
        )

    domains = fetch_all(
        f"""
        SELECT {DOMAIN_COLUMNS} {DOMAIN_JOINS}
        WHERE domains.organization_id = ?
        ORDER BY domains.registration_end
        """,
        [organization_id],
    )
    context = {"title": organization["name"], "organization": organization, "domains": domains}
    return render(request, "organizations/organization_detail.html", context)
