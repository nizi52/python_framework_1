"""Проверка веб-страниц Django: шаблоны (ПР6) и данные из SQLite (ПР7)."""

import django
from django.test.utils import setup_test_environment

django.setup()
setup_test_environment()

from django.test import Client  # noqa: E402
from django.urls import reverse  # noqa: E402

client = Client()


def test_index_uses_base_template():
    response = client.get(reverse("homepage:index"))
    names = [t.name for t in response.templates]
    assert response.status_code == 200
    assert "homepage/index.html" in names
    assert "base.html" in names
    assert "includes/nav.html" in names


def test_list_pages_render_from_sqlite():
    pages = {
        "domains:list": "domains/domain_list.html",
        "organizations:list": "organizations/organization_list.html",
        "resources:list": "resources/resource_list.html",
        "rentals:list": "rentals/rental_list.html",
    }
    for url_name, template in pages.items():
        response = client.get(reverse(url_name))
        assert response.status_code == 200, url_name
        assert template in [t.name for t in response.templates]
        assert len(response.context["rows"]) > 0


def test_detail_pages_and_named_urls():
    assert reverse("domains:detail", args=[1]) == "/domains/1/"
    response = client.get(reverse("domains:detail", args=[1]))
    assert response.status_code == 200
    assert response.context["domain"]["name"] == "example.ru"
    for url_name in ("organizations:detail", "resources:detail", "rentals:detail"):
        assert client.get(reverse(url_name, args=[1])).status_code == 200


def test_missing_object_returns_404_template():
    response = client.get(reverse("domains:detail", args=[999]))
    assert response.status_code == 404
    assert "not_found.html" in [t.name for t in response.templates]


def test_available_domains_by_date():
    url = reverse("domains:available")
    assert client.get(url).context["rows"] == []
    names = [row["name"] for row in client.get(url, {"date": "2026-11-15"}).context["rows"]]
    assert "mirea-team.ru" in names        # действует, аренда начнётся только 01.12
    assert "blog-ivanov.ru" not in names   # сдан в аренду до 30.11
    assert "example.ru" not in names       # сдан в аренду до 31.12
    assert "archive.example.org" not in names  # исключён из реестра


def test_available_domains_bad_date():
    response = client.get(reverse("domains:available"), {"date": "завтра"})
    assert response.status_code == 200
    assert response.context["error"]


def test_parameter_is_not_injected():
    response = client.get(reverse("domains:available"), {"date": "2026-11-15' OR '1'='1"})
    assert response.status_code == 200
    assert response.context["rows"] == []


def test_expiring_and_statistics_pages():
    response = client.get(reverse("domains:expiring"), {"days": "3650"})
    assert response.status_code == 200
    assert all(row["days_left"] >= 0 for row in response.context["rows"])

    stats = client.get(reverse("homepage:statistics"))
    assert stats.status_code == 200
    assert stats.context["summary"]["domains_total"] >= 1
    assert len(stats.context["by_organization"]) >= 1


def test_static_files_are_linked():
    html = client.get(reverse("homepage:index")).content.decode()
    assert "/static/css/style.css" in html
    assert "/static/js/main.js" in html
    assert "/static/img/logo.svg" in html
