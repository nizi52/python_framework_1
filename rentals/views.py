"""Представления приложения rentals: список и страница аренды домена."""

from django.shortcuts import render
from django.urls import reverse

from homepage.views import load_data, not_found
from models import Rental
from models.rentals import find_rental_by_id, get_rental_status

STATUS_BADGES = {
    "действует": "bg-success",
    "завершена": "bg-secondary",
    "отменена": "bg-danger",
}


def with_status(rental: Rental) -> dict:
    """Упаковать аренду вместе со статусом (текст — из get_rental_status() ПР3)."""
    status = get_rental_status(rental)
    return {"rental": rental, "status": status, "css": STATUS_BADGES[status]}


def rental_list(request):
    """Страница /rentals/: таблица аренд доменов."""
    rows = [with_status(rental) for rental in load_data().rentals]
    return render(request, "rentals/rental_list.html", {"title": "Аренда", "rows": rows})


def rental_detail(request, rental_id):
    """Страница /rentals/<id>/: карточка аренды или 404."""
    rental = find_rental_by_id(load_data().rentals, rental_id)

    if rental is None:
        return not_found(
            request, "Аренда не найдена", reverse("rentals:list"), "← к списку аренд"
        )

    context = {"title": f"Аренда №{rental.id}", "item": with_status(rental)}
    return render(request, "rentals/rental_detail.html", context)
