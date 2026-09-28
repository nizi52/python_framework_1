"""Функции для работы со сроком регистрации доменов."""

from datetime import date


def is_domain_active(registration_end: date) -> bool:
    """Проверить, активен ли домен на текущую дату."""
    return registration_end >= date.today()


def get_domain_status(is_active: bool) -> str:
    """Вернуть текстовый статус домена (функция из ПР1)."""
    if is_active:
        return "Домен активен"
    return "Домен истёк"


def renew_domain(
    domains: dict[int, dict], domain_id: int, new_end_date: date
) -> bool:
    """Продлить регистрацию домена, установив новый срок действия.

    Возвращает True, если домен найден и обновлён, иначе False.
    """
    if domain_id not in domains:
        return False
    domains[domain_id]["registration_end"] = new_end_date
    return True


def cancel_domain(domains: dict[int, dict], domain_id: int) -> bool:
    """Удалить домен из реестра. Возвращает True, если домен был удалён."""
    if domain_id not in domains:
        return False
    del domains[domain_id]
    return True


def sort_domains_by_expiration(domains: dict[int, dict]) -> list[dict]:
    """Вернуть домены, отсортированные по сроку окончания регистрации."""
    return sorted(domains.values(), key=lambda item: item["registration_end"])


def domain_statistics(domains: dict[int, dict]) -> dict:
    """Собрать статистику по реестру: количество активных и истёкших
    доменов и среднее число дней до окончания срока среди активных.
    """
    total = len(domains)
    active_count = sum(
        1 for item in domains.values() if is_domain_active(item["registration_end"])
    )
    expired_count = total - active_count

    days_left = [
        (item["registration_end"] - date.today()).days
        for item in domains.values()
        if is_domain_active(item["registration_end"])
    ]
    average_days_left = sum(days_left) / len(days_left) if days_left else 0

    return {
        "total": total,
        "active": active_count,
        "expired": expired_count,
        "average_days_left": round(average_days_left, 1),
    }
