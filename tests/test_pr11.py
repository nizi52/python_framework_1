"""ПР11: формы фильтрации, создания, изменения и отмены аренды, загрузка скриншота домена."""

from datetime import date, timedelta
from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from domains.models import Domain
from organizations.models import Organization
from rentals.forms import RentalFilterForm, RentalForm
from rentals.models import Rental
from users.models import User

pytestmark = pytest.mark.usefixtures("orm_data")


def make_png():
    buffer = BytesIO()
    Image.new("RGB", (4, 4), "white").save(buffer, "PNG")
    return buffer.getvalue()


@pytest.fixture
def free_domain():
    return Domain.objects.create(
        name="free-domain.ru",
        organization=Organization.objects.first(),
        owner=User.objects.first(),
        registration_end=date(2099, 12, 31),
    )


def future(days):
    return timezone.localdate() + timedelta(days=days)


def rental_data(domain, start, end, user=1):
    return {"domain": domain.pk, "user": user, "start_date": start, "end_date": end}


def test_filter_form_converts_and_validates_values():
    form = RentalFilterForm({"date": "2026-11-15", "domain": "1", "sort": "end"})
    assert form.is_valid()
    assert form.cleaned_data["date"] == date(2026, 11, 15)
    assert form.cleaned_data["domain"].name == "example.ru"
    bad = RentalFilterForm({"domain": "999", "sort": "id; DROP TABLE"})
    assert not bad.is_valid()
    assert set(bad.errors) == {"domain", "sort"}


def test_rental_list_shows_filter_form_errors(client):
    response = client.get(reverse("rentals:list"), {"date": "завтра", "domain": "1"})
    assert response.status_code == 200
    assert "Укажите дату в формате ГГГГ-ММ-ДД." in response.content.decode()
    assert [row["id"] for row in response.context["rows"]] == [1]  # фильтр по домену применён


def test_create_form_page(client):
    response = client.get(reverse("rentals:create"))
    assert response.status_code == 200
    assert "csrfmiddlewaretoken" in response.content.decode()
    assert response.context["form"].initial["start_date"] == timezone.localdate()


def test_create_rental(client, free_domain):
    data = rental_data(free_domain, future(1), future(30))
    response = client.post(reverse("rentals:create"), data)
    rental = Rental.objects.get(domain=free_domain)
    assert response.status_code == 302
    assert response.url == reverse("rentals:detail", args=[rental.pk])
    assert rental.status == Rental.Status.ACTIVE


def test_create_rejects_past_start_date(client, free_domain):
    response = client.post(
        reverse("rentals:create"), rental_data(free_domain, future(-1), future(10))
    )
    assert response.status_code == 200
    assert "start_date" in response.context["form"].errors
    assert not Rental.objects.filter(domain=free_domain).exists()


def test_create_rejects_end_before_start(client, free_domain):
    response = client.post(
        reverse("rentals:create"), rental_data(free_domain, future(10), future(5))
    )
    assert "end_date" in response.context["form"].errors


def test_create_rejects_period_after_registration_end(client):
    domain = Domain.objects.get(name="example.ru")  # регистрация до 31.12.2026
    form = RentalForm(rental_data(domain, date(2026, 12, 20), date(2027, 1, 20)))
    assert not form.is_valid()
    assert "end_date" in form.errors


def test_create_rejects_overlap_with_active_rental(client, free_domain):
    Rental.objects.create(
        domain=free_domain, user_id=2, start_date=future(10), end_date=future(20)
    )
    response = client.post(
        reverse("rentals:create"), rental_data(free_domain, future(15), future(25))
    )
    form = response.context["form"]
    assert form.non_field_errors() == ["Домен уже сдан в аренду на часть выбранного периода."]
    assert "уже сдан в аренду" in response.content.decode()


def test_cancelled_rental_does_not_block_new_one(client, free_domain):
    Rental.objects.create(
        domain=free_domain,
        user_id=2,
        start_date=future(10),
        end_date=future(20),
        status=Rental.Status.CANCELLED,
    )
    form = RentalForm(rental_data(free_domain, future(15), future(25)))
    assert form.is_valid(), form.errors


def test_removed_domain_is_not_offered():
    choices = RentalForm().fields["domain"].queryset
    assert not choices.filter(name="archive.example.org").exists()


def test_update_rental_does_not_conflict_with_itself(client, free_domain):
    rental = Rental.objects.create(
        domain=free_domain, user_id=1, start_date=future(10), end_date=future(20)
    )
    response = client.post(
        reverse("rentals:update", args=[rental.pk]),
        rental_data(free_domain, future(10), future(40), user=2),
    )
    assert response.status_code == 302
    rental.refresh_from_db()
    assert (rental.end_date, rental.user_id) == (future(40), 2)


def test_update_running_rental_keeps_past_start(client):
    rental = Rental.objects.get(pk=1)  # example.ru, началась 01.01.2026
    data = rental_data(rental.domain, "2026-01-01", "2026-12-30", user=rental.user_id)
    response = client.post(reverse("rentals:update", args=[1]), data)
    assert response.status_code == 302
    assert Rental.objects.get(pk=1).end_date == date(2026, 12, 30)


def test_update_form_is_prefilled(client):
    response = client.get(reverse("rentals:update", args=[1]))
    assert response.status_code == 200
    assert response.context["form"].instance.pk == 1
    assert 'value="2026-01-01"' in response.content.decode()


def test_update_missing_rental_returns_404(client):
    response = client.get(reverse("rentals:update", args=[999]))
    assert response.status_code == 404
    assert "not_found.html" in [t.name for t in response.templates]


def test_cancel_requires_post(client):
    assert client.get(reverse("rentals:cancel", args=[1])).status_code == 405
    assert Rental.objects.get(pk=1).status == Rental.Status.ACTIVE


def test_cancel_rental_frees_domain(client):
    response = client.post(reverse("rentals:cancel", args=[1]))
    assert response.status_code == 302
    assert Rental.objects.get(pk=1).status == Rental.Status.CANCELLED
    active_ids = [row["id"] for row in client.get(reverse("rentals:list")).context["rows"]]
    assert 1 not in active_ids
    free = client.get(reverse("domains:available"), {"date": "2026-11-15"}).context["rows"]
    assert "example.ru" in [row["name"] for row in free]


def test_cancel_only_active_rental(client):
    assert client.post(reverse("rentals:cancel", args=[3])).status_code == 404  # уже отменена
    assert client.post(reverse("rentals:cancel", args=[999])).status_code == 404


def test_csrf_token_is_required(free_domain):
    from django.test import Client

    strict = Client(enforce_csrf_checks=True)
    response = strict.post(
        reverse("rentals:create"), rental_data(free_domain, future(1), future(5))
    )
    assert response.status_code == 403


def test_screenshot_upload_and_display(client, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    url = reverse("domains:screenshot", args=["example-ru-1"])
    assert client.get(url).status_code == 200
    image = SimpleUploadedFile("site.png", make_png(), content_type="image/png")
    response = client.post(url, {"screenshot": image})
    assert response.status_code == 302
    domain = Domain.objects.get(pk=1)
    assert domain.screenshot.name.startswith("domains/")
    assert (tmp_path / domain.screenshot.name).exists()
    assert domain.screenshot.url in client.get(domain.get_absolute_url()).content.decode()


def test_screenshot_rejects_non_image(client, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    fake = SimpleUploadedFile("site.png", b"not an image", content_type="image/png")
    response = client.post(
        reverse("domains:screenshot", args=["example-ru-1"]), {"screenshot": fake}
    )
    assert response.status_code == 200
    assert "screenshot" in response.context["form"].errors
    assert not Domain.objects.get(pk=1).screenshot
