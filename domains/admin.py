from django.contrib import admin

from domains.models import Domain


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "owner", "registration_end", "is_removed")
    list_filter = ("is_removed", "organization")
    search_fields = ("name",)
