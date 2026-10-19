"""Представления приложения resources: список и страница ресурса."""

from django.shortcuts import render
from django.urls import reverse

from homepage.views import load_data, not_found
from models import Resource
from models.resources import find_resource_by_id


def get_status_label(resource: Resource) -> tuple[str, str]:
    """Вернуть текст статуса ресурса и класс бейджа Bootstrap."""
    if resource.is_active():
        return "активен", "bg-success"
    return "неактивен", "bg-danger"


def with_status(resource: Resource) -> dict:
    """Упаковать ресурс вместе с его статусом для передачи в шаблон."""
    status, css = get_status_label(resource)
    return {"resource": resource, "status": status, "css": css}


def resource_list(request):
    """Страница /resources/: таблица ресурсов доменов."""
    rows = [with_status(resource) for resource in load_data().resources]
    return render(request, "resources/resource_list.html", {"title": "Ресурсы", "rows": rows})


def resource_detail(request, resource_id):
    """Страница /resources/<id>/: карточка ресурса или 404."""
    resource = find_resource_by_id(load_data().resources, resource_id)

    if resource is None:
        return not_found(
            request, "Ресурс не найден", reverse("resources:list"), "← к списку ресурсов"
        )

    context = {"title": resource.name, "item": with_status(resource)}
    return render(request, "resources/resource_detail.html", context)
