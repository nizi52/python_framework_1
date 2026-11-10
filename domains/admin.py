from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html

from domains.models import Domain
from rentals.admin import DomainRentalInline
from rentals.models import Rental
from resources.models import Resource


class ResourceInline(admin.TabularInline):
    model = Resource
    fields = ("name", "kind")
    extra = 0
    show_change_link = True


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "organization",
        "owner",
        "registration_end",
        "is_removed",
        "is_ru_zone",
        "active_rentals_count",
        "site_link",
    )
    list_display_links = ("name",)
    list_editable = ("registration_end",)
    search_fields = ("name", "organization__name", "owner__name")
    list_filter = ("is_removed", "is_ru_zone", "organization")
    ordering = ("name",)
    list_per_page = 20
    readonly_fields = ("id", "slug", "is_ru_zone")
    list_select_related = ("organization", "owner")
    autocomplete_fields = ("organization", "owner")
    inlines = (ResourceInline, DomainRentalInline)
    view_on_site = True

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(
                active_rentals=Count("rentals", filter=Q(rentals__status=Rental.Status.ACTIVE))
            )
        )

    @admin.display(description="Активных аренд", ordering="active_rentals")
    def active_rentals_count(self, obj):
        return obj.active_rentals

    @admin.display(description="Страница на сайте")
    def site_link(self, obj):
        return format_html('<a href="{}" target="_blank">Открыть</a>', obj.get_absolute_url())
