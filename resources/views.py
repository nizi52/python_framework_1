"""Представления приложения resources: список и страница ресурса."""

from django.http import HttpResponse
from django.utils.html import escape

from homepage.views import badge, load_data, not_found_page, page
from models import Resource
from models.resources import find_resource_by_id


def get_status_label(resource: Resource) -> tuple[str, str]:
    """Вернуть текст статуса ресурса и класс бейджа Bootstrap."""
    if resource.is_active():
        return "активен", "bg-success"
    return "неактивен", "bg-danger"


def resources(request):
    """Страница /resources/: таблица ресурсов доменов."""
    rows = ""
    for resource in load_data().resources:
        status, css = get_status_label(resource)
        rows += f"""
        <tr>
            <td><a href="/resources/{resource.id}/">{escape(resource.name)}</a></td>
            <td>{escape(resource.kind)}</td>
            <td><a href="/domains/{resource.domain.id}/">{escape(resource.domain.name)}</a></td>
            <td>{badge(status, css)}</td>
        </tr>
        """

    if rows:
        body = f"""
        <div class="table-responsive">
            <table class="table table-hover table-dark">
                <thead>
                    <tr><th>Ресурс</th><th>Тип</th><th>Домен</th><th>Статус</th></tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """
    else:
        body = '<p class="text-muted">Ресурсов пока нет.</p>'

    return HttpResponse(page("Ресурсы", f"<h1>Ресурсы</h1>{body}"))


def resource_detail(request, resource_id):
    """Страница /resources/<id>/: карточка ресурса или 404."""
    resource = find_resource_by_id(load_data().resources, resource_id)

    if resource is None:
        return not_found_page("Ресурс не найден", "/resources/", "← к списку ресурсов")

    status, css = get_status_label(resource)
    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{escape(resource.name)}</h5>
            <p class="card-text"><strong>ID:</strong> {resource.id}</p>
            <p class="card-text"><strong>Тип:</strong> {escape(resource.kind)}</p>
            <p class="card-text">
                <strong>Домен:</strong>
                <a href="/domains/{resource.domain.id}/">{escape(resource.domain.name)}</a>
            </p>
            <p class="card-text">Статус: {badge(status, css)}</p>
            <a href="/resources/" class="btn btn-outline-secondary">← к списку ресурсов</a>
        </div>
    </div>
    """
    return HttpResponse(page(resource.name, content))
