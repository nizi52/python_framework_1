"""Маршруты приложения rentals."""

from django.urls import path

from . import views

app_name = "rentals"

urlpatterns = [
    path("", views.rental_list, name="list"),
    path("create/", views.rental_create, name="create"),
    path("<int:rental_id>/", views.rental_detail, name="detail"),
    path("<int:rental_id>/edit/", views.rental_update, name="update"),
    path("<int:rental_id>/cancel/", views.rental_cancel, name="cancel"),
]
