"""Представления приложения homepage: главная, статистика и страницы 404.

С ПР7 веб-страницы получают данные из базы SQLite (пакет db/). Загрузка JSON
средствами ПР3 (load_data) сохранена для консольной версии и тестов.
"""

from django.conf import settings
from django.shortcuts import render

from db.database import fetch_all, fetch_one
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
    counts = fetch_one(
        """
        SELECT
            (SELECT COUNT(*) FROM domains) AS domains,
            (SELECT COUNT(*) FROM domains
              WHERE is_removed = 0 AND registration_end >= date('now', 'localtime'))
              AS active_domains,
            (SELECT COUNT(*) FROM organizations) AS organizations,
            (SELECT COUNT(*) FROM resources) AS resources,
            (SELECT COUNT(*) FROM rentals WHERE is_cancelled = 0) AS rentals
        """
    )
    sections = [
        {"title": "Домены", "url": "domains:list", "count": counts["domains"]},
        {"title": "Организации", "url": "organizations:list", "count": counts["organizations"]},
        {"title": "Ресурсы", "url": "resources:list", "count": counts["resources"]},
        {"title": "Аренда", "url": "rentals:list", "count": counts["rentals"]},
    ]
    context = {"title": "Система учета доменных имен", "sections": sections, "counts": counts}
    return render(request, "homepage/index.html", context)


def statistics(request):
    """Страница /statistics/: показатели реестра (агрегатные функции, GROUP BY, HAVING)."""
    summary = fetch_one(
        """
        SELECT COUNT(*) AS domains_total,
               SUM(CASE WHEN is_removed = 0
                         AND registration_end >= date('now', 'localtime') THEN 1 ELSE 0 END)
                   AS domains_active,
               MIN(CASE WHEN is_removed = 0
                         AND registration_end >= date('now', 'localtime')
                        THEN registration_end END) AS nearest_end,
               MAX(registration_end) AS latest_end
        FROM domains
        """
    )
    avg_rental = fetch_one(
        """
        SELECT ROUND(AVG(julianday(end_date) - julianday(start_date)), 1) AS avg_days
        FROM rentals
        WHERE is_cancelled = 0
        """
    )
    by_organization = fetch_all(
        """
        SELECT organizations.name AS organization_name,
               COUNT(domains.id) AS domains_count
        FROM organizations
        LEFT JOIN domains ON domains.organization_id = organizations.id
        GROUP BY organizations.id, organizations.name
        ORDER BY domains_count DESC, organizations.name
        """
    )
    rentals_by_domain = fetch_all(
        """
        SELECT domains.id AS domain_id,
               domains.name AS domain_name,
               COUNT(rentals.id) AS rentals_count
        FROM domains
        LEFT JOIN rentals ON rentals.domain_id = domains.id
                         AND rentals.is_cancelled = 0
        GROUP BY domains.id, domains.name
        ORDER BY rentals_count DESC, domains.name
        """
    )
    resources_by_kind = fetch_all(
        """
        SELECT kind, COUNT(*) AS resources_count
        FROM resources
        GROUP BY kind
        ORDER BY resources_count DESC, kind
        """
    )
    try:
        min_resources = max(1, int(request.GET.get("min_resources", 2)))
    except ValueError:
        min_resources = 2
    rich_domains = fetch_all(
        """
        SELECT domains.id AS domain_id,
               domains.name AS domain_name,
               COUNT(resources.id) AS resources_count
        FROM domains
        JOIN resources ON resources.domain_id = domains.id
        GROUP BY domains.id, domains.name
        HAVING COUNT(resources.id) >= ?
        ORDER BY resources_count DESC
        """,
        [min_resources],
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
