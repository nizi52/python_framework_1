"""Проверка веб-страниц Django: шаблоны (ПР6) и данные через Django ORM (ПР9).

Тесты работают с отдельной тестовой базой pytest-django: данные в неё переносит
фикстура orm_data (db/import_sqlite_to_orm.py), рабочая база db.sqlite3 не затрагивается.
"""

from datetime import date, timedelta

import pytest
from django.urls import reverse

from domains.models import Domain
from rentals.models import Rental
from users.models import User

pytestmark = pytest.mark.usefixtures("orm_data")


def test_index_uses_base_template(client):
    response = client.get(reverse("homepage:index"))
    names = [t.name for t in response.templates]
    assert response.status_code == 200
    assert "homepage/index.html" in names
    assert "base.html" in names
    assert "includes/nav.html" in names
    assert response.context["counts"]["domains"] == 6
    assert response.context["counts"]["rentals"] == 4  # пятая аренда отменена


def test_list_pages_render_from_orm(client):
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


def test_detail_pages_and_named_urls(client):
    assert Domain.objects.get(pk=1).get_absolute_url() == "/domains/example-ru-1/"
    response = client.get(reverse("domains:detail", args=["example-ru-1"]))
    assert response.status_code == 200
    domain = response.context["domain"]
    assert domain.name == "example.ru"
    assert domain.organization.name == 'ООО "Ромашка"'
    assert len(response.context["resources"]) == 2
    for url_name in ("organizations:detail", "resources:detail", "rentals:detail"):
        assert client.get(reverse(url_name, args=[1])).status_code == 200


@pytest.mark.parametrize(
    "url_name", ["domains:detail", "organizations:detail", "resources:detail", "rentals:detail"]
)
def test_missing_object_returns_404_template(client, url_name):
    response = client.get(reverse(url_name, args=[999]))
    assert response.status_code == 404
    assert "not_found.html" in [t.name for t in response.templates]


def test_unknown_url_returns_404_page(client):
    response = client.get("/no-such-page/")
    assert response.status_code == 404
    assert "404.html" in [t.name for t in response.templates]


def test_available_domains_by_date(client):
    url = reverse("domains:available")
    assert list(client.get(url).context["rows"]) == []
    names = [row["name"] for row in client.get(url, {"date": "2026-11-15"}).context["rows"]]
    assert "mirea-team.ru" in names  # действует, аренда начнётся только 01.12
    assert "blog-ivanov.ru" not in names  # сдан в аренду до 30.11
    assert "example.ru" not in names  # сдан в аренду до 31.12
    assert "archive.example.org" not in names  # исключён из реестра


def test_cancelled_rental_does_not_block_domain(client):
    # shop.example.com: аренда №3 отменена, поэтому в её период домен свободен
    response = client.get(reverse("domains:available"), {"date": "2026-06-01"})
    assert "shop.example.com" in [row["name"] for row in response.context["rows"]]


def test_available_domains_bad_date(client):
    response = client.get(reverse("domains:available"), {"date": "завтра"})
    assert response.status_code == 200
    assert response.context["error"]


def test_parameter_is_not_injected(client):
    response = client.get(reverse("domains:available"), {"date": "2026-11-15' OR '1'='1"})
    assert response.status_code == 200
    assert list(response.context["rows"]) == []


def test_expiring_page(client):
    response = client.get(reverse("domains:expiring"), {"days": "3650"})
    assert response.status_code == 200
    rows = response.context["rows"]
    assert rows and all(row["days_left"] >= 0 for row in rows)
    assert [r["registration_end"] for r in rows] == sorted(r["registration_end"] for r in rows)
    # некорректное и слишком большое значение приводятся к допустимому
    assert client.get(reverse("domains:expiring"), {"days": "abc"}).context["days"] == 90
    assert client.get(reverse("domains:expiring"), {"days": "999999"}).context["days"] == 3650


def test_domain_search_is_case_insensitive_for_cyrillic(client):
    url = reverse("domains:list")
    names = {row["name"] for row in client.get(url, {"q": "ромашка"}).context["rows"]}
    assert names == {"example.ru", "old-project.ru", "blog-ivanov.ru"}
    by_owner = {row["name"] for row in client.get(url, {"q": "ПЕТРОВ"}).context["rows"]}
    # совпадение с организацией «ИП Петров» и с владельцем «Петров П.П.»
    assert by_owner == {"shop.example.com", "mirea-team.ru", "archive.example.org"}
    by_name = {row["name"] for row in client.get(url, {"q": "MIREA"}).context["rows"]}
    assert by_name == {"mirea-team.ru"}


def test_domain_search_empty_result(client):
    response = client.get(reverse("domains:list"), {"q": "несуществующее"})
    assert response.status_code == 200
    assert list(response.context["rows"]) == []
    assert "не найдено" in response.content.decode()


def test_domain_search_percent_is_not_wildcard(client):
    response = client.get(reverse("domains:list"), {"q": "%"})
    assert list(response.context["rows"]) == []


def test_domain_sorting_uses_whitelist(client):
    url = reverse("domains:list")
    by_end = [r["registration_end"] for r in client.get(url, {"sort": "end"}).context["rows"]]
    assert by_end == sorted(by_end)
    by_org_rows = client.get(url, {"sort": "organization"}).context["rows"]
    by_org = [r["organization_name"] for r in by_org_rows]
    assert by_org == sorted(by_org)
    by_owner = [r["owner_name"] for r in client.get(url, {"sort": "owner"}).context["rows"]]
    assert by_owner == sorted(by_owner)
    # произвольное значение не попадает в order_by: используется сортировка по названию
    response = client.get(url, {"sort": "id; DROP TABLE domains_domain"})
    assert response.status_code == 200
    assert response.context["sort"] == "name"
    names = [r["name"] for r in response.context["rows"]]
    assert names == sorted(names)


def test_rentals_hide_cancelled_by_default(client):
    url = reverse("rentals:list")
    assert len(client.get(url).context["rows"]) == 4
    assert len(client.get(url, {"all": "1"}).context["rows"]) == 5


def test_rentals_filters(client):
    url = reverse("rentals:list")
    on_date = client.get(url, {"date": "2026-11-15"}).context["rows"]
    assert {row["id"] for row in on_date} == {1, 4}
    by_domain = client.get(url, {"domain": "1"}).context["rows"]
    assert [row["id"] for row in by_domain] == [1]
    by_user = client.get(url, {"user": "3", "all": "1"}).context["rows"]
    assert {row["id"] for row in by_user} == {3, 5}
    combined = client.get(url, {"user": "3", "domain": "4"}).context["rows"]
    assert [row["id"] for row in combined] == [5]


def test_rentals_bad_parameters_do_not_break_page(client):
    url = reverse("rentals:list")
    response = client.get(url, {"date": "31.12.2026", "domain": "abc", "user": "-1", "sort": "x"})
    assert response.status_code == 200
    assert response.context["error"]
    assert len(response.context["rows"]) == 4  # некорректные фильтры игнорируются


def test_rentals_sorting(client):
    url = reverse("rentals:list")
    by_domain = [r["domain_name"] for r in client.get(url, {"sort": "domain"}).context["rows"]]
    assert by_domain == sorted(by_domain)
    by_end = [r["end_date"] for r in client.get(url, {"sort": "end"}).context["rows"]]
    assert by_end == sorted(by_end)


def make_extra_rentals(count):
    user = User.objects.get(pk=1)
    domain = Domain.objects.get(pk=1)
    start = date(2030, 1, 1)
    Rental.objects.bulk_create(
        Rental(
            user=user,
            domain=domain,
            start_date=start + timedelta(days=10 * i),
            end_date=start + timedelta(days=10 * i + 5),
        )
        for i in range(count)
    )


def test_rentals_pagination_keeps_filters(client):
    make_extra_rentals(8)  # 4 неотменённые + 8 = 12 записей, по 5 на страницу
    url = reverse("rentals:list")
    first = client.get(url, {"sort": "domain"})
    assert first.context["page_obj"].paginator.num_pages == 3
    assert len(first.context["rows"]) == 5
    html = client.get(url, {"sort": "domain", "user": "1"}).content.decode()
    assert "page=2" in html and "sort=domain" in html and "user=1" in html

    assert client.get(url, {"page": "abc"}).context["page_obj"].number == 1
    assert client.get(url, {"page": "999"}).context["page_obj"].number == 3
    assert len(client.get(url, {"page": "3"}).context["rows"]) == 2


def test_rentals_pagination_hidden_for_short_list(client):
    html = client.get(reverse("rentals:list")).content.decode()
    assert "pagination" not in html


def test_statistics_page(client):
    stats = client.get(reverse("homepage:statistics"))
    assert stats.status_code == 200
    summary = stats.context["summary"]
    assert summary["domains_total"] == 6
    assert summary["latest_end"] == date(2027, 6, 30)
    assert stats.context["avg_rental"]["avg_days"] == 227.0  # (364 + 365 + 90 + 89) / 4
    by_org = {item.name: item.domains_count for item in stats.context["by_organization"]}
    assert by_org == {'ООО "Ромашка"': 3, "ИП Петров": 3, 'АО "ТехноСеть"': 0}


def test_statistics_counts_ignore_cancelled_rentals(client):
    by_domain = {
        row["name"]: row["rentals_count"]
        for row in client.get(reverse("homepage:statistics")).context["rentals_by_domain"]
    }
    assert by_domain["shop.example.com"] == 0  # единственная аренда отменена
    assert by_domain["example.ru"] == 1


def test_statistics_group_filter(client):
    url = reverse("homepage:statistics")
    rich = client.get(url, {"min_resources": "2"}).context["rich_domains"]
    assert [row["name"] for row in rich] == ["mirea-team.ru", "example.ru"]  # 3 и 2 ресурса
    assert all(row["resources_count"] >= 2 for row in rich)
    assert list(client.get(url, {"min_resources": "100"}).context["rich_domains"]) == []
    assert client.get(url, {"min_resources": "abc"}).context["min_resources"] == 2


def test_organization_without_domains_is_listed(client):
    response = client.get(reverse("organizations:list"))
    rows = {org.name: org.domains_count for org in response.context["rows"]}
    assert rows['АО "ТехноСеть"'] == 0
    assert "—" in response.content.decode()


def test_static_files_are_linked(client):
    html = client.get(reverse("homepage:index")).content.decode()
    assert "/static/css/style.css" in html
    assert "/static/js/main.js" in html
    assert "/static/img/logo.svg" in html


def test_views_do_not_use_raw_sql():
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    for app in ("homepage", "domains", "organizations", "resources", "rentals"):
        text = (root / app / "views.py").read_text(encoding="utf-8")
        assert "import sqlite3" not in text and "db.database" not in text, app
        assert "fetch_all" not in text and "fetch_one" not in text, app
        assert ".execute(" not in text and ".raw(" not in text, app


def test_organization_list_uses_three_queries(client, django_assert_num_queries):
    # организации с числом доменов и prefetch_related("domains"), без запроса на каждую строку;
    # третий запрос: число доменов в подвале (контекстный процессор, ПР10)
    with django_assert_num_queries(3):
        client.get(reverse("organizations:list"))


def test_domain_detail_uses_four_queries(client, django_assert_num_queries):
    # домен с организацией и владельцем (select_related), ресурсы, аренды с арендаторами,
    # число доменов в подвале (контекстный процессор)
    with django_assert_num_queries(4):
        client.get(reverse("domains:detail", args=["example-ru-1"]))
