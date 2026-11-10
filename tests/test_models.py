"""Проверка моделей Django (ПР9): поля, связи, ограничения, CRUD и методы моделей."""

from datetime import date

import pytest
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from domains.models import Domain
from organizations.models import Organization
from rentals.models import Rental
from resources.models import Resource
from users.models import User

pytestmark = pytest.mark.usefixtures("orm_data")


def test_str_and_ordering():
    assert str(Organization.objects.get(pk=2)) == "ИП Петров"
    assert str(Domain.objects.get(pk=1)) == "example.ru"
    names = list(Domain.objects.values_list("name", flat=True))
    assert names == sorted(names)
    rental = Rental.objects.get(pk=1)
    assert "example.ru" in str(rental) and "2026-01-01" in str(rental)


def test_forward_and_reverse_relations():
    domain = Domain.objects.select_related("organization", "owner").get(pk=1)
    assert domain.organization.name == 'ООО "Ромашка"'
    assert domain.owner.name == "Иванов И.И."
    assert domain.organization_id == 1  # столбец внешнего ключа

    assert Organization.objects.get(pk=1).domains.count() == 3
    assert User.objects.get(pk=1).owned_domains.count() == 3
    assert domain.resources.count() == 2
    assert domain.rentals.count() == 1
    assert User.objects.get(pk=3).rentals.count() == 2


def test_unique_constraints():
    with pytest.raises(IntegrityError), transaction.atomic():
        Domain.objects.create(
            name="example.ru", organization_id=1, owner_id=1, registration_end=date(2030, 1, 1)
        )
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.create(name="Дубликат", email="dup@example.com")
        User.objects.create(name="Дубликат 2", email="dup@example.com")


def test_rental_dates_check_constraint():
    with pytest.raises(IntegrityError), transaction.atomic():
        Rental.objects.create(
            user_id=1, domain_id=1, start_date=date(2030, 2, 1), end_date=date(2030, 1, 1)
        )


def test_create_update_delete():
    org = Organization.objects.create(name="Новая организация")
    domain = Domain.objects.create(
        name="new-site.ru", organization=org, owner_id=1, registration_end=date(2030, 5, 1)
    )
    assert Domain.objects.filter(name="new-site.ru").exists()

    domain.name = "renamed-site.ru"
    domain.save()
    assert Domain.objects.get(pk=domain.pk).name == "renamed-site.ru"
    Domain.objects.filter(pk=domain.pk).update(is_removed=True)
    domain.refresh_from_db()
    assert domain.is_removed

    domain.delete()
    assert not Domain.objects.filter(pk=domain.pk).exists()
    org.delete()
    assert not Organization.objects.filter(pk=org.pk).exists()


def test_protect_keeps_history():
    with pytest.raises(ProtectedError):
        Organization.objects.get(pk=1).delete()
    with pytest.raises(ProtectedError):
        User.objects.get(pk=1).delete()
    with pytest.raises(ProtectedError):
        Domain.objects.get(pk=1).delete()  # есть ресурсы и аренда
    # запись без зависимых объектов удаляется свободно
    resource = Resource.objects.first()
    resource.delete()
    assert not Resource.objects.filter(pk=resource.pk).exists()


def test_domain_status_on_fixed_dates():
    domain = Domain.objects.get(pk=1)  # регистрация до 2026-12-31
    assert domain.get_status(date(2026, 6, 1)) == "активен"
    assert domain.is_active(date(2026, 12, 31))
    assert domain.get_status(date(2027, 1, 1)) == "истёк"
    removed = Domain.objects.get(pk=6)
    assert removed.get_status(date(2026, 6, 1)) == "удалён"
    assert not removed.is_active(date(2026, 6, 1))


def test_status_annotation_matches_method():
    day = date(2026, 11, 15)
    for domain in Domain.objects.with_status(day):
        assert domain.status == domain.get_status(day)


def test_domain_renew_and_remove():
    domain = Domain.objects.get(pk=1)
    with pytest.raises(ValueError):
        domain.renew(date(2026, 1, 1))
    domain.renew(date(2028, 1, 1))
    assert Domain.objects.get(pk=1).registration_end == date(2028, 1, 1)

    domain.remove()
    assert Domain.objects.get(pk=1).is_removed  # запись сохраняется, история не теряется


def test_rental_cancel_and_status():
    rental = Rental.objects.get(pk=4)  # 2026-09-01 – 2026-11-30
    assert rental.duration_days == 90
    assert Rental.objects.with_status(date(2026, 8, 1)).get(pk=4).status == "запланирована"
    assert Rental.objects.with_status(date(2026, 10, 1)).get(pk=4).status == "действует"
    assert Rental.objects.with_status(date(2027, 1, 1)).get(pk=4).status == "завершена"

    rental.cancel()
    assert Rental.objects.with_status(date(2026, 10, 1)).get(pk=4).status == "отменена"
    assert not Rental.objects.active_on(date(2026, 10, 1)).filter(pk=4).exists()


def test_resource_status_follows_domain():
    resource = Resource.objects.get(pk=1)  # домен example.ru
    assert Resource.objects.with_status(date(2026, 6, 1)).get(pk=1).status == "активен"
    assert Resource.objects.with_status(date(2027, 6, 1)).get(pk=1).status == "неактивен"
    assert resource.is_available(date(2026, 6, 1))
    assert not resource.is_available(date(2027, 6, 1))
