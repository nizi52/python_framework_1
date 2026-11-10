"""Корневая маршрутизация проекта: подключает маршруты приложений."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("domains/", include("domains.urls")),
    path("organizations/", include("organizations.urls")),
    path("resources/", include("resources.urls")),
    path("rentals/", include("rentals.urls")),
]

if settings.ENABLE_DEBUG_TOOLBAR:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()

handler404 = "homepage.views.page_not_found"
