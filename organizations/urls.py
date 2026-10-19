"""Маршруты приложения organizations."""

from django.urls import path

from . import views

app_name = "organizations"

urlpatterns = [
    path("", views.organization_list, name="list"),
    path("<int:organization_id>/", views.organization_detail, name="detail"),
]
