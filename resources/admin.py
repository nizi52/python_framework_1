from django.contrib import admin

from resources.models import Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "kind", "domain")
    list_display_links = ("name",)
    search_fields = ("name", "domain__name")
    list_filter = ("kind",)
    ordering = ("domain__name", "kind")
    list_per_page = 20
    list_select_related = ("domain",)
    autocomplete_fields = ("domain",)
