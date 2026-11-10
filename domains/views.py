"""Представления приложения domains: домены, свободные и истекающие домены.

С ПР9 данные берутся через Django ORM из моделей (domains.models.Domain и
связанных), а не SQL-запросами sqlite3. Значения от пользователя (поиск,
сортировка, дата, число дней) проверяются: поле сортировки выбирается из
заранее заданного словаря, дата и число разбираются с обработкой ошибок.
"""

from datetime import date, timedelta

from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from domains.models import Domain
from homepage.views import not_found
from rentals.models import Rental

# Допустимые значения параметра sort -> поля сортировки (в том числе по связанной модели).
DOMAIN_SORT_FIELDS = {
    "name": "name",
    "end": "registration_end",
    "organization": "organization__name",
    "owner": "owner__name",
}


def domain_list(request):
    """Страница /domains/?q=...&sort=...: домены с организацией, владельцем и статусом.

    Параметр q ищет подстроку без учёта регистра (в том числе кириллицу, lookup
    uicontains из homepage.search) в названии домена, организации и имени владельца,
    параметр sort выбирает порядок (name, end, organization, owner).
    """
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "name")
    if sort not in DOMAIN_SORT_FIELDS:
        sort = "name"

    domains = Domain.objects.all()
    if query:
        domains = domains.filter(
            Q(name__uicontains=query)
            | Q(organization__name__uicontains=query)
            | Q(owner__name__uicontains=query)
        )
    rows = domains.order_by(DOMAIN_SORT_FIELDS[sort], "id").as_rows()
    context = {
        "title": "Домены",
        "rows": rows,
        "query": query,
        "sort": sort,
    }
    return render(request, "domains/domain_list.html", context)


def domain_not_found(request):
    return not_found(request, "Домен не найден", reverse("domains:list"), "← к списку доменов")


def domain_detail(request, slug):
    """Страница /domains/<slug>/: карточка домена, его ресурсы и аренды, или 404."""
    try:
        domain = (
            Domain.objects.select_related("organization", "owner").with_status().get(slug=slug)
        )
    except Domain.DoesNotExist:
        return domain_not_found(request)

    context = {
        "title": domain.name,
        "domain": domain,
        "resources": domain.resources.order_by("kind"),
        "rentals": domain.rentals.select_related("user").with_state(),
    }
    return render(request, "domains/domain_detail.html", context)


def domain_detail_by_id(request, domain_id):
    """Адрес /domains/<id>/ из ПР5–ПР9: постоянное перенаправление на страницу по slug."""
    domain = Domain.objects.filter(pk=domain_id).only("slug").first()
    if domain is None:
        return domain_not_found(request)
    return redirect(domain, permanent=True)


def parse_date(value):
    """Преобразовать строку YYYY-MM-DD в дату; при ошибке вернуть None."""
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def available_domains(request):
    """Страница /domains/available/?date=YYYY-MM-DD: домены, свободные для аренды.

    Домен свободен, если он в реестре, его регистрация действует на эту дату
    и на эту дату у него нет неотменённой аренды. Отменённые аренды домен не блокируют.
    """
    raw_date = request.GET.get("date", "")
    selected = parse_date(raw_date)
    rows = []
    error = ""
    if raw_date and selected is None:
        error = "Укажите дату в формате ГГГГ-ММ-ДД."
    elif selected is not None:
        busy_domain_ids = Rental.objects.active_on(selected).values("domain_id")
        rows = (
            Domain.objects.in_registry()
            .filter(registration_end__gte=selected)
            .exclude(pk__in=busy_domain_ids)
            .order_by("name")
            .as_rows()
        )
    context = {
        "title": "Свободные домены",
        "rows": rows,
        "selected": selected,
        "raw_date": raw_date,
        "error": error,
    }
    return render(request, "domains/available.html", context)


def expiring_domains(request):
    """Страница /domains/expiring/?days=N: домены, срок которых истекает в ближайшие N дней."""
    try:
        days = int(request.GET.get("days", 90))
    except ValueError:
        days = 90
    days = max(1, min(days, 3650))

    today = timezone.localdate()
    rows = list(
        Domain.objects.in_registry()
        .filter(registration_end__range=(today, today + timedelta(days=days)))
        .order_by("registration_end", "name")
        .as_rows(today)
    )
    for row in rows:
        row["days_left"] = (row["registration_end"] - today).days
    context = {"title": "Истекающие домены", "rows": rows, "days": days}
    return render(request, "domains/expiring.html", context)
