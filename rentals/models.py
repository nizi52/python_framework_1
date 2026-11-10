"""Модель аренды домена пользователем на период."""

from django.db import models
from django.db.models import Case, F, Q, Value, When
from django.utils import timezone

from domains.models import Domain
from users.models import User

STATUS_CANCELLED = "отменена"
STATUS_PLANNED = "запланирована"
STATUS_ACTIVE = "действует"
STATUS_FINISHED = "завершена"


class RentalQuerySet(models.QuerySet):
    def not_cancelled(self):
        return self.filter(is_cancelled=False)

    def active_on(self, day):
        """Неотменённые аренды, период которых включает указанную дату."""
        return self.not_cancelled().filter(start_date__lte=day, end_date__gte=day)

    def with_status(self, today=None):
        """Добавить поле status: статус аренды на указанную дату."""
        today = today or timezone.localdate()
        return self.annotate(
            status=Case(
                When(is_cancelled=True, then=Value(STATUS_CANCELLED)),
                When(start_date__gt=today, then=Value(STATUS_PLANNED)),
                When(end_date__gte=today, then=Value(STATUS_ACTIVE)),
                default=Value(STATUS_FINISHED),
                output_field=models.CharField(),
            ),
        )

    def as_rows(self, today=None):
        return self.with_status(today).values(
            "id",
            "domain_id",
            "start_date",
            "end_date",
            "status",
            domain_name=F("domain__name"),
            user_name=F("user__name"),
        )


class Rental(models.Model):
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
    is_cancelled = models.BooleanField(default=False, verbose_name="Аренда отменена")

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
        self.is_cancelled = True
        self.save(update_fields=["is_cancelled"])
