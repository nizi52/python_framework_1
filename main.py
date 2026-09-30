"""Точка запуска приложения «Система учета доменных имен»."""

from typing import List

from models import Domain, User
from models.domains import (
    add_domain,
    domain_statistics,
    find_domain,
    remove_domain,
    renew_domain,
    show_domains,
)
from models.users import add_user, find_user_by_id, show_users
from storage import load_domains, load_users, save_domains, save_users
from utils import input_date, input_int, input_nonempty

DOMAINS_FILE = "data/domains.json"
USERS_FILE = "data/users.json"


def create_new_domain(domains: List[Domain], users: List[User]) -> None:
    """Пользовательский сценарий добавления домена с привязкой к владельцу."""
    user_id = input_int("id владельца (пользователя): ")
    owner = find_user_by_id(users, user_id)
    if owner is None:
        print("Пользователь с таким id не найден. Сначала добавьте его (пункт 4).")
        return

    name = input_nonempty("Название домена: ")
    organization = input_nonempty("Организация: ")
    registration_end = input_date("Срок действия (ДД.ММ.ГГГГ): ")

    domain = add_domain(domains, name, organization, registration_end, owner)
    print(f"Домен добавлен, id = {domain.id}")


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
    domains = load_domains(DOMAINS_FILE, users)

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
            create_new_domain(domains, users)
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
        elif choice == "0":
            print("Завершение работы.")
            break
        else:
            print("Некорректный выбор, попробуйте снова.")


if __name__ == "__main__":
    main()
