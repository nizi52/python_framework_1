"""Представления приложения resources: список и страница ресурса (SQLite, ПР7)."""

from django.shortcuts import render
from django.urls import reverse

from db.database import fetch_all, fetch_one
from homepage.views import not_found

# Ресурс доступен, пока активен домен, к которому он привязан (логика ПР3).
RESOURCE_QUERY = """
    SELECT resources.id,
           resources.name,
           resources.kind,
           domains.id AS domain_id,
           domains.name AS domain_name,
           CASE
               WHEN domains.is_removed = 0
                    AND domains.registration_end >= date('now', 'localtime') THEN 'активен'
               ELSE 'неактивен'
           END AS status
    FROM resources
    JOIN domains ON resources.domain_id = domains.id
"""


def resource_list(request):
    """Страница /resources/: ресурсы с названием домена (JOIN)."""
    rows = fetch_all(RESOURCE_QUERY + " ORDER BY domains.name, resources.kind")
    return render(request, "resources/resource_list.html", {"title": "Ресурсы", "rows": rows})


def resource_detail(request, resource_id):
    """Страница /resources/<id>/: карточка ресурса или 404."""
    resource = fetch_one(RESOURCE_QUERY + " WHERE resources.id = ?", [resource_id])
    if resource is None:
        return not_found(
            request, "Ресурс не найден", reverse("resources:list"), "← к списку ресурсов"
        )
    context = {"title": resource["name"], "resource": resource}
    return render(request, "resources/resource_detail.html", context)
