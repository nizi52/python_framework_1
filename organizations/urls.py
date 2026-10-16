"""Маршруты приложения organizations."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.organizations, name="organizations"),
    path("<int:organization_id>/", views.organization_detail, name="organization_detail"),
]
