"""Представления приложения resources: список и страница ресурса (Django ORM)."""

from django.shortcuts import render
from django.urls import reverse

from homepage.views import not_found
from resources.models import Resource


def resource_list(request):
    """Страница /resources/: ресурсы с названием домена."""
    rows = Resource.objects.order_by("domain__name", "kind").as_rows()
    return render(request, "resources/resource_list.html", {"title": "Ресурсы", "rows": rows})


def resource_detail(request, resource_id):
    """Страница /resources/<id>/: карточка ресурса или 404."""
    try:
        resource = Resource.objects.select_related("domain").with_status().get(pk=resource_id)
    except Resource.DoesNotExist:
        return not_found(
            request, "Ресурс не найден", reverse("resources:list"), "← к списку ресурсов"
        )
    context = {"title": resource.name, "resource": resource}
    return render(request, "resources/resource_detail.html", context)
