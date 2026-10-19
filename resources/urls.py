"""Маршруты приложения resources."""

from django.urls import path

from . import views

app_name = "resources"

urlpatterns = [
    path("", views.resource_list, name="list"),
    path("<int:resource_id>/", views.resource_detail, name="detail"),
]
