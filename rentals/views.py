"""Представления приложения rentals: список аренд и страница аренды (Django ORM).

Список поддерживает фильтры (статус, дата, домен, арендатор), выбор
сортировки и постраничный вывод. Параметры берутся из строки запроса и проверяются.
"""

from django.core.paginator import Paginator
from django.shortcuts import render
from django.urls import reverse

from domains.models import Domain
from domains.views import parse_date
from homepage.views import not_found
from rentals.models import Rental
from users.models import User

PAGE_SIZE = 5

# Допустимые значения параметра sort -> поля сортировки (в том числе по связанной модели).
RENTAL_SORT_FIELDS = {
    "start": "start_date",
    "end": "end_date",
    "domain": "domain__name",
    "user": "user__name",
}


def rental_list(request):
    """Страница /rentals/: аренды доменов с фильтрами, сортировкой и пагинацией.

    Параметры: status=all|cancelled|completed (по умолчанию только активные; all=1 из ПР9
    означает status=all), date=ГГГГ-ММ-ДД (аренды, действующие в этот день),
    domain=<id>, user=<id>, sort=start|end|domain|user, page=N.
    """
    status = request.GET.get("status", "")
    if request.GET.get("all") == "1":
        status = "all"
    raw_date = request.GET.get("date", "").strip()
    domain_id = request.GET.get("domain", "").strip()
    user_id = request.GET.get("user", "").strip()
    sort = request.GET.get("sort", "start")
    if sort not in RENTAL_SORT_FIELDS:
        sort = "start"
    error = None

    rentals = Rental.objects.all()
    if status in (Rental.Status.CANCELLED, Rental.Status.COMPLETED):
        rentals = rentals.filter(status=status)
    elif status != "all":
        status = ""
        rentals = rentals.active()
    if raw_date:
        selected = parse_date(raw_date)
        if selected is None:
            error = "Укажите дату в формате ГГГГ-ММ-ДД."
        else:
            rentals = rentals.for_date(selected)
    if domain_id.isdigit():
        rentals = rentals.filter(domain_id=int(domain_id))
    if user_id.isdigit():
        rentals = rentals.filter(user_id=int(user_id))

    rows = rentals.order_by(RENTAL_SORT_FIELDS[sort], "id").as_rows()
    page_obj = Paginator(rows, PAGE_SIZE).get_page(request.GET.get("page"))
    context = {
        "title": "Аренда",
        "rows": page_obj,
        "page_obj": page_obj,
        "status": status,
        "raw_date": raw_date,
        "selected_domain": domain_id,
        "selected_user": user_id,
        "sort": sort,
        "domains": Domain.objects.order_by("name"),
        "users": User.objects.order_by("name"),
        "error": error,
    }
    return render(request, "rentals/rental_list.html", context)


def rental_detail(request, rental_id):
    """Страница /rentals/<id>/: карточка аренды или 404."""
    try:
        rental = Rental.objects.select_related("domain", "user").with_state().get(pk=rental_id)
    except Rental.DoesNotExist:
        return not_found(request, "Аренда не найдена", reverse("rentals:list"), "← к списку аренд")
    context = {"title": f"Аренда №{rental.id}", "rental": rental}
    return render(request, "rentals/rental_detail.html", context)
