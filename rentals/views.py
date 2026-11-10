"""Представления приложения rentals: список, карточка, создание, изменение и отмена аренды.

Список поддерживает фильтры (статус, дата, домен, арендатор), выбор сортировки и
постраничный вывод. С ПР11 GET-параметры фильтров проверяет форма RentalFilterForm,
а аренды создаются и изменяются через ModelForm RentalForm.
"""

from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from homepage.views import not_found
from rentals.forms import RentalFilterForm, RentalForm
from rentals.models import Rental

PAGE_SIZE = 5

# Допустимые значения параметра sort -> поля сортировки (в том числе по связанной модели).
RENTAL_SORT_FIELDS = {
    "start": "start_date",
    "end": "end_date",
    "domain": "domain__name",
    "user": "user__name",
}


def rental_not_found(request):
    return not_found(request, "Аренда не найдена", reverse("rentals:list"), "← к списку аренд")


def rental_list(request):
    """Страница /rentals/: аренды доменов с фильтрами, сортировкой и пагинацией.

    Параметры: status=all|cancelled|completed (по умолчанию только активные; all=1 из ПР9
    означает status=all), date=ГГГГ-ММ-ДД (аренды, действующие в этот день),
    domain=<id>, user=<id>, sort=start|end|domain|user, page=N.
    """
    params = request.GET.copy()
    if params.get("all") == "1":
        params["status"] = "all"
    form = RentalFilterForm(params)
    # Неверные значения попадают в form.errors, а фильтры с верными значениями применяются.
    form.is_valid()
    filters = form.cleaned_data

    status = filters.get("status", "")
    rentals = Rental.objects.all()
    if status in (Rental.Status.CANCELLED, Rental.Status.COMPLETED):
        rentals = rentals.filter(status=status)
    elif status != "all":
        rentals = rentals.active()
    if filters.get("date"):
        rentals = rentals.for_date(filters["date"])
    if filters.get("domain"):
        rentals = rentals.filter(domain=filters["domain"])
    if filters.get("user"):
        rentals = rentals.filter(user=filters["user"])
    sort = filters.get("sort") or "start"

    rows = rentals.order_by(RENTAL_SORT_FIELDS[sort], "id").as_rows()
    page_obj = Paginator(rows, PAGE_SIZE).get_page(request.GET.get("page"))
    context = {
        "title": "Аренда",
        "form": form,
        "rows": page_obj,
        "page_obj": page_obj,
        "status": status,
        "sort": sort,
    }
    return render(request, "rentals/rental_list.html", context)


def rental_detail(request, rental_id):
    """Страница /rentals/<id>/: карточка аренды или 404."""
    try:
        rental = Rental.objects.select_related("domain", "user").with_state().get(pk=rental_id)
    except Rental.DoesNotExist:
        return rental_not_found(request)
    context = {"title": f"Аренда №{rental.id}", "rental": rental}
    return render(request, "rentals/rental_detail.html", context)


def rental_create(request):
    """Страница /rentals/create/: новая аренда. Сохраняется только после проверки формы."""
    if request.method == "POST":
        form = RentalForm(request.POST)
        if form.is_valid():
            rental = form.save()
            return redirect("rentals:detail", rental_id=rental.pk)
    else:
        form = RentalForm(initial={"start_date": timezone.localdate()})
    context = {"title": "Новая аренда", "form": form}
    return render(request, "rentals/rental_form.html", context)


def rental_update(request, rental_id):
    """Страница /rentals/<id>/edit/: изменение домена, арендатора и срока аренды."""
    rental = Rental.objects.filter(pk=rental_id).first()
    if rental is None:
        return rental_not_found(request)
    if request.method == "POST":
        form = RentalForm(request.POST, instance=rental)
        if form.is_valid():
            form.save()
            return redirect("rentals:detail", rental_id=rental.pk)
    else:
        form = RentalForm(instance=rental)
    context = {"title": f"Аренда №{rental.pk}: изменение", "form": form, "rental": rental}
    return render(request, "rentals/rental_form.html", context)


@require_POST
def rental_cancel(request, rental_id):
    """POST /rentals/<id>/cancel/: отмена активной аренды. Запись остаётся в базе."""
    rental = Rental.objects.active().filter(pk=rental_id).first()
    if rental is None:
        return rental_not_found(request)
    rental.cancel()
    return redirect("rentals:detail", rental_id=rental.pk)
