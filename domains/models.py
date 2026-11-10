"""Модель домена и запросы к ней.

Статус домена на дату вычисляется на стороне базы данных (Case/When), чтобы
списки получали его одним запросом; для отдельного объекта есть метод get_status().
"""

from django.db import models
from django.db.models import Case, F, Value, When
from django.utils import timezone

from organizations.models import Organization
from users.models import User

STATUS_REMOVED = "удалён"
STATUS_ACTIVE = "активен"
STATUS_EXPIRED = "истёк"


class DomainQuerySet(models.QuerySet):
    def in_registry(self):
        """Домены, не исключённые из реестра."""
        return self.filter(is_removed=False)

    def with_status(self, today=None):
        """Добавить поле status: статус домена на указанную дату."""
        today = today or timezone.localdate()
        return self.annotate(
            status=Case(
                When(is_removed=True, then=Value(STATUS_REMOVED)),
                When(registration_end__gte=today, then=Value(STATUS_ACTIVE)),
                default=Value(STATUS_EXPIRED),
                output_field=models.CharField(),
            ),
        )

    def as_rows(self, today=None):
        """Строки для таблиц: словари с названиями организации и владельца вместо id."""
        return self.with_status(today).values(
            "id",
            "name",
            "registration_end",
            "organization_id",
            "status",
            organization_name=F("organization__name"),
            owner_name=F("owner__name"),
        )


class Domain(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Доменное имя")
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="domains",
        verbose_name="Организация",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="owned_domains",
        verbose_name="Владелец",
    )
    registration_end = models.DateField(verbose_name="Регистрация действует до")
    is_removed = models.BooleanField(default=False, verbose_name="Исключён из реестра")

    objects = DomainQuerySet.as_manager()

    class Meta:
        ordering = ["name"]
        verbose_name = "Домен"
        verbose_name_plural = "Домены"

    def __str__(self):
        return self.name

    def get_status(self, today=None):
        """Статус домена на дату: удалён, активен или истёк."""
        today = today or timezone.localdate()
        if self.is_removed:
            return STATUS_REMOVED
        return STATUS_ACTIVE if self.registration_end >= today else STATUS_EXPIRED

    def is_active(self, today=None):
        return self.get_status(today) == STATUS_ACTIVE

    def renew(self, new_end):
        """Продлить регистрацию: новая дата должна быть позже текущей."""
        if new_end <= self.registration_end:
            raise ValueError("Новая дата должна быть позже текущей даты окончания.")
        self.registration_end = new_end
        self.save(update_fields=["registration_end"])

    def remove(self):
        """«Мягкое» удаление: домен остаётся в базе, но считается неактивным."""
        self.is_removed = True
        self.save(update_fields=["is_removed"])
