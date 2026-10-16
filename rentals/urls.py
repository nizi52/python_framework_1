"""Маршруты приложения rentals."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.rentals, name="rentals"),
    path("<int:rental_id>/", views.rental_detail, name="rental_detail"),
]
