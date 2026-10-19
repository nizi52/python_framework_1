"""Представления приложения rentals: список и страница аренды домена (SQLite, ПР7)."""

from django.shortcuts import render
from django.urls import reverse

from db.database import fetch_all, fetch_one
from domains.views import RENTAL_STATUS
from homepage.views import not_found

RENTAL_QUERY = f"""
    SELECT rentals.id,
           domains.id AS domain_id,
           domains.name AS domain_name,
           users.name AS user_name,
           users.email AS user_email,
           strftime('%d.%m.%Y', rentals.start_date) AS start_display,
           strftime('%d.%m.%Y', rentals.end_date) AS end_display,
           CAST(julianday(rentals.end_date) - julianday(rentals.start_date) AS INTEGER)
               AS duration_days,
           {RENTAL_STATUS} AS status
    FROM rentals
    JOIN domains ON rentals.domain_id = domains.id
    JOIN users ON rentals.user_id = users.id
"""


def rental_list(request):
    """Страница /rentals/: аренды доменов (JOIN трёх таблиц).

    По умолчанию показываются только неотменённые аренды; ?all=1 – все записи.
    """
    show_all = request.GET.get("all") == "1"
    query = RENTAL_QUERY
    if not show_all:
        query += " WHERE rentals.is_cancelled = 0"
    rows = fetch_all(query + " ORDER BY rentals.start_date")
    context = {"title": "Аренда", "rows": rows, "show_all": show_all}
    return render(request, "rentals/rental_list.html", context)


def rental_detail(request, rental_id):
    """Страница /rentals/<id>/: карточка аренды или 404."""
    rental = fetch_one(RENTAL_QUERY + " WHERE rentals.id = ?", [rental_id])
    if rental is None:
        return not_found(
            request, "Аренда не найдена", reverse("rentals:list"), "← к списку аренд"
        )
    context = {"title": f"Аренда №{rental['id']}", "rental": rental}
    return render(request, "rentals/rental_detail.html", context)
