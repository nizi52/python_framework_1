"""Маршруты приложения domains."""

from django.urls import path

from . import views

app_name = "domains"

urlpatterns = [
    path("", views.domain_list, name="list"),
    path("<int:domain_id>/", views.domain_detail, name="detail"),
]
