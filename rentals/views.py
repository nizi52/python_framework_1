"""Представления приложения rentals: список и страница аренды домена."""

from django.http import HttpResponse
from django.utils.html import escape

from homepage.views import DATE_FORMAT, badge, load_data, not_found_page, page
from models import Rental
from models.rentals import find_rental_by_id, get_rental_status

STATUS_BADGES = {
    "действует": "bg-success",
    "завершена": "bg-secondary",
    "отменена": "bg-danger",
}


def status_badge(rental: Rental) -> str:
    """Вернуть бейдж статуса аренды (текст — из get_rental_status() ПР3)."""
    status = get_rental_status(rental)
    return badge(status, STATUS_BADGES[status])


def rentals(request):
    """Страница /rentals/: таблица аренд доменов."""
    rows = ""
    for rental in load_data().rentals:
        rows += f"""
        <tr>
            <td><a href="/rentals/{rental.id}/">№{rental.id}</a></td>
            <td><a href="/domains/{rental.domain.id}/">{escape(rental.domain.name)}</a></td>
            <td>{escape(rental.user.name)}</td>
            <td>{rental.start_date.strftime(DATE_FORMAT)}</td>
            <td>{rental.end_date.strftime(DATE_FORMAT)}</td>
            <td>{status_badge(rental)}</td>
        </tr>
        """

    if rows:
        body = f"""
        <div class="table-responsive">
            <table class="table table-hover table-dark">
                <thead>
                    <tr>
                        <th>Аренда</th><th>Домен</th><th>Арендатор</th>
                        <th>Начало</th><th>Срок до</th><th>Статус</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """
    else:
        body = '<p class="text-muted">Аренд пока нет.</p>'

    return HttpResponse(page("Аренда", f"<h1>Аренда доменов</h1>{body}"))


def rental_detail(request, rental_id):
    """Страница /rentals/<id>/: карточка аренды или 404."""
    rental = find_rental_by_id(load_data().rentals, rental_id)

    if rental is None:
        return not_found_page("Аренда не найдена", "/rentals/", "← к списку аренд")

    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">Аренда №{rental.id}</h5>
            <p class="card-text">
                <strong>Домен:</strong>
                <a href="/domains/{rental.domain.id}/">{escape(rental.domain.name)}</a>
            </p>
            <p class="card-text">
                <strong>Арендатор:</strong> {escape(rental.user.name)}
                ({escape(rental.user.email)})
            </p>
            <p class="card-text">
                <strong>Период:</strong>
                {rental.start_date.strftime(DATE_FORMAT)} – {rental.end_date.strftime(DATE_FORMAT)}
            </p>
            <p class="card-text">Статус: {status_badge(rental)}</p>
            <a href="/rentals/" class="btn btn-outline-secondary">← к списку аренд</a>
        </div>
    </div>
    """
    return HttpResponse(page(f"Аренда №{rental.id}", content))
