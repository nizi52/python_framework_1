from django.apps import AppConfig


class HomepageConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "homepage"

    def ready(self):
        # Подключает lookup uicontains и функцию UNICODE_LOWER для поиска по кириллице.
        from homepage import search  # noqa: F401
