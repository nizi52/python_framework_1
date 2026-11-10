"""ПР10: статусы аренды, slug домена, вычисляемое поле, контекстный процессор и админка."""

from datetime import date

import pytest
from django.conf import settings
from django.urls import reverse

from domains.models import Domain
from organizations.models import Organization
from rentals.models import Rental
from users.models import User

pytestmark = pytest.mark.usefixtures("orm_data")

DAY = date(2026, 11, 15)  # аренда №1 домена example.ru действует в этот день


def available_names(client, day=DAY):
    response = client.get(reverse("domains:available"), {"date": day.isoformat()})
    return {row["name"] for row in response.context["rows"]}


def test_rental_status_methods():
    Rental.objects.filter(pk=2).update(status=Rental.Status.COMPLETED)
    assert set(Rental.objects.active().values_list("pk", flat=True)) == {1, 4, 5}
    assert set(Rental.objects.cancelled().values_list("pk", flat=True)) == {3}
    assert set(Rental.objects.completed().values_list("pk", flat=True)) == {2}
    assert set(Rental.objects.for_date(DAY).values_list("pk", flat=True)) == {1, 3, 4}


@pytest.mark.parametrize(
    "status, blocks",
    [
        (Rental.Status.ACTIVE, True),
        (Rental.Status.CANCELLED, False),
        (Rental.Status.COMPLETED, False),
    ],
)
def test_only_active_rental_blocks_domain(client, status, blocks):
    Rental.objects.filter(pk=1).update(status=status)
    assert ("example.ru" not in available_names(client)) == blocks


def test_rental_list_status_filter(client):
    Rental.objects.filter(pk=2).update(status=Rental.Status.COMPLETED)
    url = reverse("rentals:list")
    assert {row["id"] for row in client.get(url).context["rows"]} == {1, 4, 5}
    completed = client.get(url, {"status": "completed"}).context["rows"]
    assert [row["id"] for row in completed] == [2]
    cancelled = client.get(url, {"status": "cancelled"}).context["rows"]
    assert [row["id"] for row in cancelled] == [3]
    assert len(client.get(url, {"status": "all"}).context["rows"]) == 5
    assert client.get(url, {"status": "x"}).context["status"] == ""


def test_statistics_counts_each_status(client):
    Rental.objects.filter(pk=2).update(status=Rental.Status.COMPLETED)
    stats = client.get(reverse("homepage:statistics")).context["rentals_by_status"]
    assert stats == {"total": 5, "active": 3, "cancelled": 1, "completed": 1}


def test_existing_domains_have_unique_slugs():
    slugs = list(Domain.objects.values_list("slug", flat=True))
    assert all(slugs) and len(slugs) == len(set(slugs))
    assert Domain.objects.get(pk=1).slug == "example-ru-1"


def test_new_domain_gets_slug_and_url():
    domain = Domain.objects.create(
        name="новый-сайт.рф",
        organization=Organization.objects.first(),
        owner=User.objects.first(),
        registration_end=date(2027, 1, 1),
    )
    assert domain.slug == f"novyi-sait-rf-{domain.pk}"
    assert domain.get_absolute_url() == f"/domains/{domain.slug}/"

    domain.name = "renamed.ru"
    domain.save()
    assert (
        Domain.objects.get(pk=domain.pk).slug == f"novyi-sait-rf-{domain.pk}"
    )  # адрес не меняется


def test_domain_detail_by_slug_and_404(client):
    response = client.get("/domains/example-ru-1/")
    assert response.status_code == 200
    assert response.context["domain"].name == "example.ru"
    missing = client.get("/domains/no-such-domain/")
    assert missing.status_code == 404
    assert "not_found.html" in [t.name for t in missing.templates]


def test_old_id_url_redirects_to_slug(client):
    response = client.get("/domains/1/")
    assert response.status_code == 301
    assert response.url == "/domains/example-ru-1/"


def test_generated_zone_field_is_recalculated():
    domain = Domain.objects.get(pk=1)
    assert domain.is_ru_zone  # example.ru
    domain.name = "example.com"
    domain.save()
    domain.refresh_from_db()
    assert not domain.is_ru_zone


def test_context_processor_in_every_page(client):
    for url in (reverse("homepage:index"), reverse("rentals:list")):
        response = client.get(url)
        assert response.context["app_title"] == "Система учета доменных имен"
        assert "доменов в реестре: 5" in response.content.decode()  # шестой домен исключён


def test_debug_toolbar_is_disabled_in_tests():
    assert not settings.ENABLE_DEBUG_TOOLBAR
    assert "debug_toolbar" not in settings.INSTALLED_APPS


@pytest.fixture
def admin_client_ru(admin_client):
    admin_client.defaults["HTTP_ACCEPT_LANGUAGE"] = "ru"
    return admin_client


def test_admin_index_lists_models_in_russian(admin_client_ru):
    html = admin_client_ru.get("/admin/").content.decode()
    for text in ("Домены", "Аренда доменов", "Пользователи реестра", "Организации", "Ресурсы"):
        assert text in html


@pytest.mark.parametrize(
    "model", ["domains/domain", "rentals/rental", "users/user", "organizations/organization"]
)
def test_admin_changelists_open(admin_client_ru, model):
    assert admin_client_ru.get(f"/admin/{model}/").status_code == 200


def test_admin_domain_search_filter_and_annotation(admin_client_ru):
    url = "/admin/domains/domain/"
    found = admin_client_ru.get(url, {"q": "mirea"}).context["cl"].result_list
    assert [d.name for d in found] == ["mirea-team.ru"]
    removed = admin_client_ru.get(url, {"is_removed__exact": "1"}).context["cl"].result_list
    assert [d.name for d in removed] == ["archive.example.org"]
    rows = {d.name: d.active_rentals for d in admin_client_ru.get(url).context["cl"].result_list}
    assert rows["example.ru"] == 1
    assert rows["shop.example.com"] == 0  # аренда отменена


def test_admin_rental_search_and_status_filter(admin_client_ru):
    url = "/admin/rentals/rental/"
    by_domain = admin_client_ru.get(url, {"q": "example.ru"}).context["cl"].result_list
    assert {r.pk for r in by_domain} == {1}
    cancelled = admin_client_ru.get(url, {"status__exact": "cancelled"}).context["cl"].result_list
    assert [r.pk for r in cancelled] == [3]


def test_admin_change_pages_show_related_rentals(admin_client_ru):
    domain_page = admin_client_ru.get("/admin/domains/domain/1/change/")
    assert domain_page.status_code == 200
    formsets = {f.opts.__class__.__name__ for f in domain_page.context["inline_admin_formsets"]}
    assert formsets == {"ResourceInline", "DomainRentalInline"}
    assert domain_page.context["has_absolute_url"]  # ссылка «Смотреть на сайте»
    user_page = admin_client_ru.get("/admin/users/user/1/change/")
    assert user_page.status_code == 200
    assert len(user_page.context["inline_admin_formsets"]) == 1


def test_admin_actions_change_status(admin_client_ru):
    url = "/admin/rentals/rental/"
    admin_client_ru.post(url, {"action": "cancel_rentals", "_selected_action": ["1", "4"]})
    assert set(Rental.objects.cancelled().values_list("pk", flat=True)) == {1, 3, 4}
    admin_client_ru.post(url, {"action": "restore_rentals", "_selected_action": ["1"]})
    assert Rental.objects.get(pk=1).status == Rental.Status.ACTIVE
