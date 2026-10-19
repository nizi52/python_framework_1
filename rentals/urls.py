"""Маршруты приложения rentals."""

from django.urls import path

from . import views

app_name = "rentals"

urlpatterns = [
    path("", views.rental_list, name="list"),
    path("<int:rental_id>/", views.rental_detail, name="detail"),
]
