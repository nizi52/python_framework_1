"""Проверка веб-страниц Django: шаблоны, контекст, именованные URL (ПР6)."""

import os
import sys
from pathlib import Path

import django
from django.test.utils import setup_test_environment

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "domainreg.settings")
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


def test_list_pages_render_from_templates():
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
    assert response.context["item"]["domain"].name == "example.ru"
    for url_name in ("organizations:detail", "resources:detail", "rentals:detail"):
        assert client.get(reverse(url_name, args=[1])).status_code == 200


def test_missing_object_returns_404_template():
    response = client.get(reverse("domains:detail", args=[999]))
    assert response.status_code == 404
    assert "not_found.html" in [t.name for t in response.templates]


def test_static_files_are_linked():
    html = client.get(reverse("homepage:index")).content.decode()
    assert "/static/css/style.css" in html
    assert "/static/js/main.js" in html
    assert "/static/img/logo.svg" in html
