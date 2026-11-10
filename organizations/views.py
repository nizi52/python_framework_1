"""Представления приложения organizations: список и страница организации (Django ORM)."""

from django.db.models import Count
from django.shortcuts import render
from django.urls import reverse

from domains.models import Domain
from homepage.views import not_found
from organizations.models import Organization


def organization_list(request):
    """Страница /organizations/: организации и число их доменов.

    Count по обратной связи domains даёт 0 для организаций без доменов: они
    остаются в списке (LEFT JOIN), prefetch_related загружает домены отдельным запросом.
    """
    organizations = Organization.objects.annotate(domains_count=Count("domains")).prefetch_related(
        "domains"
    )
    return render(
        request,
        "organizations/organization_list.html",
        {"title": "Организации", "rows": organizations},
    )


def organization_detail(request, organization_id):
    """Страница /organizations/<id>/: карточка организации и её домены, или 404."""
    try:
        organization = Organization.objects.get(pk=organization_id)
    except Organization.DoesNotExist:
        return not_found(
            request,
            "Организация не найдена",
            reverse("organizations:list"),
            "← к списку организаций",
        )

    domains = Domain.objects.filter(organization=organization).order_by("registration_end")
    context = {
        "title": organization.name,
        "organization": organization,
        "domains": domains.with_status(),
    }
    return render(request, "organizations/organization_detail.html", context)
