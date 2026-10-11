"""Представления приложения homepage: общий HTML-каркас, главная и 404."""

from django.http import HttpResponse
from django.utils.html import escape


def page(title, content):
    """Собрать HTML-страницу: кодировка, заголовок, Bootstrap, навигация."""
    bootstrap = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3" "/dist/css/bootstrap.min.css"
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(title)}</title>
    <link rel="stylesheet" href="{bootstrap}">
</head>
<body>
    <nav class="nav">
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
