"""Класс Rental и функции для работы с арендой доменов."""

from datetime import date
from typing import List, Optional

from .domains import Domain
from .users import User


class Rental:
    """Аренда домена пользователем на определённый срок."""

    def __init__(
        self,
        rental_id: int,
        user: User,
        domain: Domain,
        start_date: date,
        end_date: date,
    ) -> None:
        """Создать объект аренды."""
        self.id = rental_id
        self.user = user
        self.domain = domain
        self.start_date = start_date
        self.end_date = end_date
        self.is_cancelled = False

    def is_active(self) -> bool:
        """Проверить, действует ли аренда на текущую дату."""
        today = date.today()
        return not self.is_cancelled and self.start_date <= today <= self.end_date

    def cancel(self) -> None:
        """Отменить аренду (запись сохраняется в истории)."""
        self.is_cancelled = True

    def __str__(self) -> str:
        """Вернуть строковое представление аренды."""
        status = "действует" if self.is_active() else "не действует"
        return (
            f"{self.domain.name} | арендатор: {self.user.name} | "
            f"{self.start_date} – {self.end_date} | {status}"
        )


def create_rental(
    rentals: List[Rental],
    user: User,
    domain: Domain,
    start_date: date,
    end_date: date,
) -> Rental:
    """Создать объект Rental и добавить его в коллекцию."""
    new_id = max((rental.id for rental in rentals), default=0) + 1
    rental = Rental(new_id, user, domain, start_date, end_date)
    rentals.append(rental)
    return rental


def find_rental_by_id(rentals: List[Rental], rental_id: int) -> Optional[Rental]:
    """Найти аренду по идентификатору."""
    for rental in rentals:
        if rental.id == rental_id:
            return rental
    return None


def cancel_rental(rentals: List[Rental], rental_id: int) -> bool:
    """Найти аренду по id и отменить её."""
    rental = find_rental_by_id(rentals, rental_id)
    if rental is None:
        return False
    rental.cancel()
    return True


def get_rental_status(rental: Rental) -> str:
    """Вернуть текстовый статус аренды."""
    if rental.is_cancelled:
        return "отменена"
    if rental.is_active():
        return "действует"
    return "завершена"


def show_rentals(rentals: List[Rental]) -> None:
    """Вывести список аренд."""
    if not rentals:
        print("Аренд нет.")
        return
    for rental in rentals:
        print(f"[{rental.id}] {rental}")
