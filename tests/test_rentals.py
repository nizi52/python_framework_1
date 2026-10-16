import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models import Domain, Organization, Rental, User  # noqa: E402
from models.rentals import (  # noqa: E402
    cancel_rental,
    create_rental,
    find_rental_by_id,
    get_rental_status,
)

USER = User(1, "Иванов И.И.", "ivanov@example.com")
DOMAIN = Domain(1, "example.ru", Organization(1, "ООО Ромашка"), date(2030, 1, 1), USER)
TODAY = date.today()


def test_rental_active_within_period():
    rental = Rental(1, USER, DOMAIN, TODAY - timedelta(days=1), TODAY + timedelta(days=5))
    assert rental.is_active()
    assert get_rental_status(rental) == "действует"


def test_rental_finished_and_not_started():
    finished = Rental(1, USER, DOMAIN, TODAY - timedelta(days=10), TODAY - timedelta(days=1))
    future = Rental(2, USER, DOMAIN, TODAY + timedelta(days=1), TODAY + timedelta(days=5))
    assert not finished.is_active()
    assert get_rental_status(finished) == "завершена"
    assert not future.is_active()


def test_cancel_keeps_history():
    rentals = []
    create_rental(rentals, USER, DOMAIN, TODAY, TODAY + timedelta(days=5))
    assert cancel_rental(rentals, 1)
    assert rentals[0].is_cancelled
    assert get_rental_status(rentals[0]) == "отменена"
    assert not cancel_rental(rentals, 99)


def test_create_and_find_rental():
    rentals = []
    create_rental(rentals, USER, DOMAIN, TODAY, TODAY + timedelta(days=5))
    create_rental(rentals, USER, DOMAIN, TODAY, TODAY + timedelta(days=9))
    assert [r.id for r in rentals] == [1, 2]
    assert find_rental_by_id(rentals, 2).end_date == TODAY + timedelta(days=9)
    assert find_rental_by_id(rentals, 99) is None
