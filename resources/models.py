"""Модель ресурса домена: хостинг, SSL, почта, DNS."""

from django.db import models
from django.db.models import Case, F, Value, When
from django.utils import timezone

from domains.models import STATUS_ACTIVE


class ResourceQuerySet(models.QuerySet):
    def with_status(self, today=None):
        """Добавить поле status.

        Ресурс доступен, пока активен домен, к которому он привязан (логика ПР3).
        """
        today = today or timezone.localdate()
        return self.annotate(
            status=Case(
                When(
                    domain__is_removed=False,
                    domain__registration_end__gte=today,
                    then=Value("активен"),
                ),
                default=Value("неактивен"),
                output_field=models.CharField(),
            ),
        )

    def as_rows(self, today=None):
        return self.with_status(today).values(
            "id", "name", "kind", "domain_id", "status", domain_name=F("domain__name")
        )


class Resource(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    kind = models.CharField(max_length=50, verbose_name="Тип ресурса")
    domain = models.ForeignKey(
        "domains.Domain",
        on_delete=models.PROTECT,
        related_name="resources",
        verbose_name="Домен",
    )

    objects = ResourceQuerySet.as_manager()

    class Meta:
        ordering = ["domain__name", "kind"]
        verbose_name = "Ресурс"
        verbose_name_plural = "Ресурсы"

    def __str__(self):
        return f"{self.name} ({self.domain})"

    def is_available(self, today=None):
        return self.domain.get_status(today) == STATUS_ACTIVE
