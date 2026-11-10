from django.contrib import admin

from rentals.admin import UserRentalInline
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email")
    list_display_links = ("name",)
    search_fields = ("name", "email")
    ordering = ("name",)
    list_per_page = 20
    readonly_fields = ("id",)
    inlines = (UserRentalInline,)
