"""Маршруты приложения domains."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.domains, name="domains"),
    path("<int:domain_id>/", views.domain_detail, name="domain_detail"),
]
