"""Представления приложения homepage: главная, статистика и страницы 404.

С ПР9 веб-страницы получают данные через Django ORM (модели приложений проекта).
Загрузка JSON средствами ПР3 (load_data) сохранена для консольной версии.
"""

from datetime import timedelta

from django.conf import settings
from django.db.models import Avg, Count, ExpressionWrapper, F, DurationField, Max, Min, Q
from django.shortcuts import render
from django.utils import timezone

from domains.models import Domain
from organizations.models import Organization
from rentals.models import Rental
from resources.models import Resource
from storage import Registry, load_registry


def load_data() -> Registry:
    """Загрузить все данные ПР3 из каталога data/ (JSON -> объекты)."""
    return load_registry(settings.BASE_DIR / "data")


def not_found(request, title: str, back_url: str, back_text: str):
    """Страница «объект не найден» с кодом 404 и ссылкой назад к списку."""
    context = {"title": title, "back_url": back_url, "back_text": back_text}
    return render(request, "not_found.html", context, status=404)


def index(request):
    """Главная страница: описание приложения, разделы и сводка из базы данных."""
    today = timezone.localdate()
    counts = Domain.objects.aggregate(
        domains=Count("id"),
        active_domains=Count("id", filter=Q(is_removed=False, registration_end__gte=today)),
    )
    counts["organizations"] = Organization.objects.count()
    counts["resources"] = Resource.objects.count()
    counts["rentals"] = Rental.objects.not_cancelled().count()
    sections = [
        {"title": "Домены", "url": "domains:list", "count": counts["domains"]},
        {"title": "Организации", "url": "organizations:list", "count": counts["organizations"]},
        {"title": "Ресурсы", "url": "resources:list", "count": counts["resources"]},
        {"title": "Аренда", "url": "rentals:list", "count": counts["rentals"]},
    ]
    context = {"title": "Система учета доменных имен", "sections": sections, "counts": counts}
    return render(request, "homepage/index.html", context)


def statistics(request):
    """Страница /statistics/: показатели реестра (aggregate, annotate, values, фильтр групп)."""
    today = timezone.localdate()
    in_force = Q(is_removed=False, registration_end__gte=today)
    summary = Domain.objects.aggregate(
        domains_total=Count("id"),
        domains_active=Count("id", filter=in_force),
        nearest_end=Min("registration_end", filter=in_force),
        latest_end=Max("registration_end"),
    )

    avg_duration = Rental.objects.not_cancelled().aggregate(
        avg=Avg(ExpressionWrapper(F("end_date") - F("start_date"), output_field=DurationField()))
    )["avg"]
    avg_rental = {"avg_days": round(avg_duration / timedelta(days=1), 1) if avg_duration else None}

    by_organization = Organization.objects.annotate(domains_count=Count("domains")).order_by(
        "-domains_count", "name"
    )
    rentals_by_domain = (
        Domain.objects.annotate(
            rentals_count=Count("rentals", filter=Q(rentals__is_cancelled=False))
        )
        .order_by("-rentals_count", "name")
        .values("id", "name", "rentals_count")
    )
    resources_by_kind = (
        Resource.objects.order_by()
        .values("kind")
        .annotate(resources_count=Count("id"))
        .order_by("-resources_count", "kind")
    )
    try:
        min_resources = max(1, int(request.GET.get("min_resources", 2)))
    except ValueError:
        min_resources = 2
    rich_domains = (
        Domain.objects.annotate(resources_count=Count("resources"))
        .filter(resources_count__gte=min_resources)
        .order_by("-resources_count", "name")
        .values("id", "name", "resources_count")
    )
    context = {
        "title": "Статистика реестра",
        "summary": summary,
        "avg_rental": avg_rental,
        "by_organization": by_organization,
        "rentals_by_domain": rentals_by_domain,
        "resources_by_kind": resources_by_kind,
        "rich_domains": rich_domains,
        "min_resources": min_resources,
    }
    return render(request, "homepage/statistics.html", context)


def page_not_found(request, exception):
    """Собственная страница 404 для любого адреса без маршрута."""
    return render(request, "404.html", {"title": "404 – страница не найдена"}, status=404)
