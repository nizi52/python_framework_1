"""Представления приложения homepage: общий HTML-каркас, главная и 404."""

from django.http import HttpResponse
from django.utils.html import escape

STYLES = """
    <style>
        body {
            background-color: #631e29;
            color: #ebdecd;
        }
        .nav {
            --bs-nav-link-color: #1B1C1D;
            --bs-nav-link-hover-color: #ebdecd;
        }
        .card {
            --bs-card-bg: #304059;
            --bs-card-color: #ebdecd;
            --bs-card-border-color: #304059;
        }
        a {
            color: #ebdecd;
        }
        a:hover {
            color: #b04530;
        }
        .table-dark {
            --bs-table-bg: #304059;
            --bs-table-color: #ebdecd;
        }
        .text-danger {
            color: #ebdecd !important;
        }
    </style>"""


def page(title, content):
    """Собрать HTML-страницу: кодировка, заголовок, Bootstrap, навигация."""
    bootstrap = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3" "/dist/css/bootstrap.min.css"
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(title)}</title>
    <link rel="stylesheet" href="{bootstrap}">{STYLES}
</head>
<body>
    <nav class="nav" style="justify-content:center;">
        <a class="nav-link" href="/">Главная</a>
        <a class="nav-link" href="/domains/">Домены</a>
    </nav>
    <main class="container">{content}</main>
</body>
</html>"""


def index(request):
    """Главная страница: описание приложения и ссылки на разделы."""
    content = """
    <h1 class="display-4">Система учета доменных имен</h1>
    <p class="lead">Учёт доменов, их владельцев и сроков регистрации.</p>
    <p>Основные разделы:</p>
    <a href="/domains/" class="btn btn-primary">Домены</a>
    """
    return HttpResponse(page("Система учета доменных имен", content))


def page_not_found(request, exception):
    """Собственная страница 404 для любого адреса без маршрута."""
    content = """
    <h1 class="text-danger">404 – страница не найдена</h1>
    <p>Проверьте адрес или вернитесь на главную.</p>
    <a href="/" class="btn btn-primary">На главную</a>
    """
    return HttpResponse(
        page("404 – страница не найдена", content),
        status=404,
    )
