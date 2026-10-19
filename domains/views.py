"""Представления приложения domains: домены, свободные и истекающие домены (ПР7).

С ПР7 данные берутся из базы SQLite (data/domainreg.sqlite) SQL-запросами.
Значения от пользователя передаются только параметрами ?, строки результата –
объекты sqlite3.Row (доступ к полям по имени: row["name"], {{ row.name }}).
"""

from datetime import date

from django.shortcuts import render
from django.urls import reverse

from db.database import fetch_all, fetch_one
from homepage.views import not_found

# Статус домена на текущую дату, вычисляется средствами SQL.
DOMAIN_STATUS = """
    CASE
        WHEN domains.is_removed = 1 THEN 'удалён'
        WHEN domains.registration_end >= date('now', 'localtime') THEN 'активен'
        ELSE 'истёк'
    END
"""

RENTAL_STATUS = """
    CASE
        WHEN rentals.is_cancelled = 1 THEN 'отменена'
        WHEN rentals.start_date > date('now', 'localtime') THEN 'запланирована'
        WHEN rentals.end_date >= date('now', 'localtime') THEN 'действует'
        ELSE 'завершена'
    END
"""

DOMAIN_COLUMNS = f"""
    domains.id,
    domains.name,
    domains.registration_end,
    strftime('%d.%m.%Y', domains.registration_end) AS registration_end_display,
    organizations.id AS organization_id,
    organizations.name AS organization_name,
    users.name AS owner_name,
    users.email AS owner_email,
    {DOMAIN_STATUS} AS status
"""

DOMAIN_JOINS = """
    FROM domains
    JOIN organizations ON domains.organization_id = organizations.id
    JOIN users ON domains.owner_id = users.id
"""


def domain_list(request):
    """Страница /domains/: все домены с организацией, владельцем и статусом (JOIN)."""
    rows = fetch_all(f"SELECT {DOMAIN_COLUMNS} {DOMAIN_JOINS} ORDER BY domains.name")
    return render(request, "domains/domain_list.html", {"title": "Домены", "rows": rows})


def domain_detail(request, domain_id):
    """Страница /domains/<id>/: карточка домена, его ресурсы и аренды, или 404."""
    domain = fetch_one(
        f"SELECT {DOMAIN_COLUMNS} {DOMAIN_JOINS} WHERE domains.id = ?", [domain_id]
    )
    if domain is None:
        return not_found(
            request, "Домен не найден", reverse("domains:list"), "← к списку доменов"
        )

    resources = fetch_all(
        "SELECT id, name, kind FROM resources WHERE domain_id = ? ORDER BY kind", [domain_id]
    )
    rentals = fetch_all(
        f"""
        SELECT rentals.id,
               users.name AS user_name,
               strftime('%d.%m.%Y', rentals.start_date) AS start_display,
               strftime('%d.%m.%Y', rentals.end_date) AS end_display,
               {RENTAL_STATUS} AS status
        FROM rentals
        JOIN users ON rentals.user_id = users.id
        WHERE rentals.domain_id = ?
        ORDER BY rentals.start_date
        """,
        [domain_id],
    )
    context = {
        "title": domain["name"],
        "domain": domain,
        "resources": resources,
        "rentals": rentals,
    }
    return render(request, "domains/domain_detail.html", context)


def parse_date(value):
    """Преобразовать строку YYYY-MM-DD в дату; при ошибке вернуть None."""
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def available_domains(request):
    """Страница /domains/available/?date=YYYY-MM-DD: домены, свободные для аренды.

    Домен свободен, если он в реестре, его регистрация действует на эту дату
    и на эту дату у него нет неотменённой аренды (подзапрос NOT IN).
    """
    raw_date = request.GET.get("date", "")
    selected = parse_date(raw_date)
    rows = []
    error = ""
    if raw_date and selected is None:
        error = "Укажите дату в формате ГГГГ-ММ-ДД."
    elif selected is not None:
        rows = fetch_all(
            f"""
            SELECT {DOMAIN_COLUMNS} {DOMAIN_JOINS}
            WHERE domains.is_removed = 0
              AND domains.registration_end >= ?
              AND domains.id NOT IN (
                  SELECT rentals.domain_id
                  FROM rentals
                  WHERE rentals.is_cancelled = 0
                    AND ? BETWEEN rentals.start_date AND rentals.end_date
              )
            ORDER BY domains.name
            """,
            [selected.isoformat(), selected.isoformat()],
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
    rows = fetch_all(
        f"""
        SELECT {DOMAIN_COLUMNS},
               CAST(julianday(domains.registration_end)
                    - julianday(date('now', 'localtime')) AS INTEGER) AS days_left
        {DOMAIN_JOINS}
        WHERE domains.is_removed = 0
          AND domains.registration_end
              BETWEEN date('now', 'localtime') AND date('now', 'localtime', ?)
        ORDER BY domains.registration_end
        """,
        [f"+{days} days"],
    )
    context = {"title": "Истекающие домены", "rows": rows, "days": days}
    return render(request, "domains/expiring.html", context)
