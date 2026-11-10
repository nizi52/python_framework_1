"""Модель домена и запросы к ней.

Статус домена на дату вычисляется на стороне базы данных (Case/When), чтобы
списки получали его одним запросом; для отдельного объекта есть метод get_status().
"""

from uuid import uuid4

from django.db import models
from django.db.models import Case, F, Q, Value, When
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from unidecode import unidecode

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
            "slug",
            "organization_id",
            "status",
            organization_name=F("organization__name"),
            owner_name=F("owner__name"),
        )


def make_domain_slug(name, pk):
    """Slug из названия и id домена, точки заменяются дефисами: example.ru, 1 -> example-ru-1."""
    base_slug = slugify(unidecode(name.replace(".", "-"))) or "domain"
    return f"{base_slug}-{pk}"


class Domain(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Доменное имя")
    slug = models.SlugField(
        max_length=280,
        unique=True,
        editable=False,
        verbose_name="URL-идентификатор",
    )
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
    registration_end = models.DateField(
        verbose_name="Регистрация действует до",
        help_text="Последний оплаченный день. После этой даты домен считается истёкшим.",
    )
    is_removed = models.BooleanField(default=False, verbose_name="Исключён из реестра")
    screenshot = models.ImageField(
        upload_to="domains/",
        blank=True,
        null=True,
        verbose_name="Скриншот сайта",
    )
    is_ru_zone = models.GeneratedField(
        expression=Case(
            When(Q(name__endswith=".ru") | Q(name__endswith=".рф"), then=Value(True)),
            default=Value(False),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="Национальная зона (.ru, .рф)",
    )

    objects = DomainQuerySet.as_manager()

    class Meta:
        ordering = ["name"]
        verbose_name = "Домен"
        verbose_name_plural = "Домены"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.slug:
            return super().save(*args, **kwargs)
        if self.pk:
            self.slug = make_domain_slug(self.name, self.pk)
            return super().save(*args, **kwargs)
        # У нового домена ещё нет id: сохраняем с временным slug, затем дописываем id.
        self.slug = f"new-{uuid4().hex}"
        super().save(*args, **kwargs)
        self.slug = make_domain_slug(self.name, self.pk)
        super().save(update_fields=["slug"])

    def get_absolute_url(self):
        return reverse("domains:detail", kwargs={"slug": self.slug})

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
