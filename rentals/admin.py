from django.contrib import admin, messages

from rentals.models import Rental


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ("id", "domain", "user", "start_date", "end_date", "status")
    list_display_links = ("id",)
    search_fields = ("domain__name", "user__name", "user__email")
    list_filter = ("status", "start_date")
    ordering = ("-start_date",)
    list_per_page = 20
    readonly_fields = ("id",)
    list_select_related = ("domain", "user")
    date_hierarchy = "start_date"
    autocomplete_fields = ("domain", "user")
    actions = ("cancel_rentals", "restore_rentals")

    @admin.action(description="Отменить выбранные аренды")
    def cancel_rentals(self, request, queryset):
        updated = queryset.exclude(status=Rental.Status.CANCELLED).update(
            status=Rental.Status.CANCELLED
        )
        self.message_user(request, f"Отменено аренд: {updated}.", messages.SUCCESS)

    @admin.action(description="Вернуть выбранные аренды в активные")
    def restore_rentals(self, request, queryset):
        # Проверки пересечения периодов здесь нет: это действие только меняет статус.
        updated = queryset.exclude(status=Rental.Status.ACTIVE).update(status=Rental.Status.ACTIVE)
        self.message_user(request, f"Возвращено в активные: {updated}.", messages.SUCCESS)


class DomainRentalInline(admin.TabularInline):
    """Аренды в карточке домена."""

    model = Rental
    fields = ("user", "start_date", "end_date", "status")
    autocomplete_fields = ("user",)
    extra = 0
    can_delete = False
    show_change_link = True


class UserRentalInline(admin.TabularInline):
    """Аренды в карточке пользователя."""

    model = Rental
    fields = ("domain", "start_date", "end_date", "status")
    autocomplete_fields = ("domain",)
    extra = 0
    can_delete = False
    show_change_link = True
