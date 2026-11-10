"""Общие данные для всех шаблонов сайта."""

from domains.models import Domain

APP_TITLE = "Система учета доменных имен"


def registry_context(request):
    # Метод count передаётся без вызова: запрос выполнится, только если шаблон выведет значение.
    return {
        "app_title": APP_TITLE,
        "registry_domains_count": Domain.objects.in_registry().count,
    }
