from django.contrib import admin

from rentals.models import Rental


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ("domain", "user", "start_date", "end_date", "is_cancelled")
    list_filter = ("is_cancelled",)
