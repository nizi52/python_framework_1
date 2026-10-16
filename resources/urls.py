"""Маршруты приложения resources."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.resources, name="resources"),
    path("<int:resource_id>/", views.resource_detail, name="resource_detail"),
]
