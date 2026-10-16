"""Точка запуска приложения «Система учета доменных имен»."""

from typing import List

from models import Domain, Organization, Rental, Resource, User
from models.domains import (
    add_domain,
    domain_statistics,
    find_domain,
    find_domain_by_id,
    remove_domain,
    renew_domain,
    show_domains,
)
from models.organizations import add_organization, find_organization_by_id, show_organizations
from models.rentals import cancel_rental, create_rental, show_rentals
from models.resources import add_resource, show_resources
from models.users import add_user, find_user_by_id, show_users
from storage import (
    load_domains,
    load_organizations,
    load_rentals,
    load_resources,
    load_users,
    save_domains,
    save_organizations,
    save_rentals,
    save_resources,
    save_users,
)
from utils import input_date, input_int, input_nonempty

DOMAINS_FILE = "data/domains.json"
USERS_FILE = "data/users.json"
ORGANIZATIONS_FILE = "data/organizations.json"
RESOURCES_FILE = "data/resources.json"
RENTALS_FILE = "data/rentals.json"


def create_new_domain(
    domains: List[Domain], users: List[User], organizations: List[Organization]
) -> None:
    """Пользовательский сценарий добавления домена с владельцем и организацией."""
    user_id = input_int("id владельца (пользователя): ")
    owner = find_user_by_id(users, user_id)
    if owner is None:
        print("Пользователь с таким id не найден. Сначала добавьте его (пункт 4).")
        return

    organization_id = input_int("id организации: ")
    organization = find_organization_by_id(organizations, organization_id)
    if organization is None:
        print("Организация с таким id не найдена. Сначала добавьте её (пункт 10).")
        return

    name = input_nonempty("Название домена: ")
    registration_end = input_date("Срок действия (ДД.ММ.ГГГГ): ")

    domain = add_domain(domains, name, organization, registration_end, owner)
    print(f"Домен добавлен, id = {domain.id}")


def create_new_resource(resources: List[Resource], domains: List[Domain]) -> None:
    """Пользовательский сценарий добавления ресурса к домену."""
    domain = find_domain_by_id(domains, input_int("id домена: "))
    if domain is None:
        print("Домен с таким id не найден.")
        return
    name = input_nonempty("Название ресурса: ")
    kind = input_nonempty("Тип ресурса (хостинг, SSL, почта, DNS): ")
    resource = add_resource(resources, name, kind, domain)
    print(f"Ресурс добавлен, id = {resource.id}")


def create_new_rental(rentals: List[Rental], users: List[User], domains: List[Domain]) -> None:
    """Пользовательский сценарий оформления аренды домена."""
    user = find_user_by_id(users, input_int("id арендатора (пользователя): "))
    if user is None:
        print("Пользователь с таким id не найден.")
        return
    domain = find_domain_by_id(domains, input_int("id домена: "))
    if domain is None:
        print("Домен с таким id не найден.")
        return
    start_date = input_date("Начало аренды (ДД.ММ.ГГГГ): ")
    end_date = input_date("Окончание аренды (ДД.ММ.ГГГГ): ")
    if end_date < start_date:
        print("Окончание аренды не может быть раньше начала.")
        return
    rental = create_rental(rentals, user, domain, start_date, end_date)
    print(f"Аренда оформлена, id = {rental.id}")


def show_statistics(domains: List[Domain]) -> None:
    """Вывести статистику по реестру доменов."""
    stats = domain_statistics(domains)
    print(f"Всего доменов: {stats['total']}")
    print(f"Активных: {stats['active']}")
    print(f"Истёкших: {stats['expired']}")
    print(f"Среднее число дней до окончания (активные): {stats['average_days_left']}")


def main() -> None:
    """Точка запуска: загрузка данных, цикл меню, сохранение изменений."""
    users = load_users(USERS_FILE)
    organizations = load_organizations(ORGANIZATIONS_FILE)
    domains = load_domains(DOMAINS_FILE, users, organizations)
    resources = load_resources(RESOURCES_FILE, domains)
    rentals = load_rentals(RENTALS_FILE, users, domains)

    menu = """
=== Система учета доменных имен ===
1. Показать домены
2. Найти домен
3. Показать пользователей
4. Добавить пользователя
5. Добавить домен
6. Продлить домен
7. Удалить домен
8. Статистика
9. Показать организации
10. Добавить организацию
11. Показать ресурсы
12. Добавить ресурс
13. Показать аренды
14. Оформить аренду
15. Отменить аренду
0. Выход
"""

    while True:
        print(menu)
        choice = input("Выберите действие: ")

        if choice == "1":
            show_domains(domains)
        elif choice == "2":
            query = input_nonempty("Название или организация: ")
            show_domains(find_domain(domains, query))
        elif choice == "3":
            show_users(users)
        elif choice == "4":
            name = input_nonempty("Имя пользователя: ")
            email = input_nonempty("Email: ")
            user = add_user(users, name, email)
            save_users(USERS_FILE, users)
            print(f"Пользователь добавлен, id = {user.id}")
        elif choice == "5":
            create_new_domain(domains, users, organizations)
            save_domains(DOMAINS_FILE, domains)
        elif choice == "6":
            domain_id = input_int("id домена: ")
            new_end_date = input_date("Новый срок действия (ДД.ММ.ГГГГ): ")
            if renew_domain(domains, domain_id, new_end_date):
                save_domains(DOMAINS_FILE, domains)
                print("Срок регистрации обновлён.")
            else:
                print("Домен с таким id не найден.")
        elif choice == "7":
            domain_id = input_int("id домена: ")
            if remove_domain(domains, domain_id):
                save_domains(DOMAINS_FILE, domains)
                print("Домен удалён из активного использования.")
            else:
                print("Домен с таким id не найден.")
        elif choice == "8":
            show_statistics(domains)
        elif choice == "9":
            show_organizations(organizations)
        elif choice == "10":
            organization = add_organization(organizations, input_nonempty("Название: "))
            save_organizations(ORGANIZATIONS_FILE, organizations)
            print(f"Организация добавлена, id = {organization.id}")
        elif choice == "11":
            show_resources(resources)
        elif choice == "12":
            create_new_resource(resources, domains)
            save_resources(RESOURCES_FILE, resources)
        elif choice == "13":
            show_rentals(rentals)
        elif choice == "14":
            create_new_rental(rentals, users, domains)
            save_rentals(RENTALS_FILE, rentals)
        elif choice == "15":
            if cancel_rental(rentals, input_int("id аренды: ")):
                save_rentals(RENTALS_FILE, rentals)
                print("Аренда отменена.")
            else:
                print("Аренда с таким id не найдена.")
        elif choice == "0":
            print("Завершение работы.")
            break
        else:
            print("Некорректный выбор, попробуйте снова.")


if __name__ == "__main__":
    main()
