"""Модель аренды домена пользователем на период."""

from django.db import models
from django.db.models import Case, F, Q, Value, When
from django.utils import timezone

from domains.models import Domain
from users.models import User

# Состояние аренды на дату для страниц: вычисляется из статуса и периода аренды.
STATE_CANCELLED = "отменена"
STATE_PLANNED = "запланирована"
STATE_ACTIVE = "действует"
STATE_FINISHED = "завершена"


class RentalQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=self.model.Status.ACTIVE)

    def cancelled(self):
        return self.filter(status=self.model.Status.CANCELLED)

    def completed(self):
        return self.filter(status=self.model.Status.COMPLETED)

    def not_cancelled(self):
        """Активные и завершённые аренды: отменённые не учитываются в статистике."""
        return self.exclude(status=self.model.Status.CANCELLED)

    def for_date(self, day):
        """Аренды, период которых включает указанную дату, независимо от статуса."""
        return self.filter(start_date__lte=day, end_date__gte=day)

    def active_on(self, day):
        """Активные аренды на дату: только они блокируют домен."""
        return self.active().for_date(day)

    def with_state(self, today=None):
        """Добавить поле state: состояние аренды на дату с учётом статуса и периода."""
        today = today or timezone.localdate()
        status = self.model.Status
        return self.annotate(
            state=Case(
                When(status=status.CANCELLED, then=Value(STATE_CANCELLED)),
                When(status=status.COMPLETED, then=Value(STATE_FINISHED)),
                When(start_date__gt=today, then=Value(STATE_PLANNED)),
                When(end_date__gte=today, then=Value(STATE_ACTIVE)),
                default=Value(STATE_FINISHED),
                output_field=models.CharField(),
            ),
        )

    def as_rows(self, today=None):
        return self.with_state(today).values(
            "id",
            "domain_id",
            "start_date",
            "end_date",
            "status",
            "state",
            domain_name=F("domain__name"),
            domain_slug=F("domain__slug"),
            user_name=F("user__name"),
        )


class Rental(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Активна"
        CANCELLED = "cancelled", "Отменена"
        COMPLETED = "completed", "Завершена"

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="rentals",
        verbose_name="Арендатор",
    )
    domain = models.ForeignKey(
        Domain,
        on_delete=models.PROTECT,
        related_name="rentals",
        verbose_name="Домен",
    )
    start_date = models.DateField(verbose_name="Начало аренды")
    end_date = models.DateField(verbose_name="Окончание аренды")
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус аренды",
    )

    objects = RentalQuerySet.as_manager()

    class Meta:
        ordering = ["start_date", "pk"]
        verbose_name = "Аренда"
        verbose_name_plural = "Аренды"
        constraints = [
            models.CheckConstraint(
                condition=Q(start_date__lte=F("end_date")),
                name="rental_start_not_after_end",
            ),
        ]

    def __str__(self):
        return f"{self.domain} – {self.user} ({self.start_date} – {self.end_date})"

    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days

    def cancel(self):
        """Отменить аренду: запись сохраняется, но перестаёт блокировать домен."""
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])
