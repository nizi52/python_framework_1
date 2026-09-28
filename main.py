"""Точка запуска приложения «Система учета доменных имен»."""

from domains import add_domain, find_domain
from registrations import (
    cancel_domain,
    domain_statistics,
    get_domain_status,
    is_domain_active,
    renew_domain,
    sort_domains_by_expiration,
)
from storage import load_domains, save_domains
from utils import input_date, input_int, input_nonempty

DATA_FILE = "data/domains.json"


def show_domains(domains: dict[int, dict]) -> None:
    """Вывести список доменов, отсортированный по сроку регистрации."""
    if not domains:
        print("Реестр пуст.")
        return
    for item in sort_domains_by_expiration(domains):
        status = get_domain_status(is_domain_active(item["registration_end"]))
        print(
            f"[{item['id']}] {item['name']} | владелец: {item['owner']} | "
            f"организация: {item['organization']} | "
            f"до {item['registration_end']} | {status}"
        )


def show_statistics(domains: dict[int, dict]) -> None:
    """Вывести статистику по реестру доменов."""
    stats = domain_statistics(domains)
    print(f"Всего доменов: {stats['total']}")
    print(f"Активных: {stats['active']}")
    print(f"Истёкших: {stats['expired']}")
    print(f"Среднее число дней до окончания (активные): {stats['average_days_left']}")


def main() -> None:
    """Точка запуска: цикл меню и вызов функций проекта."""
    domains = load_domains(DATA_FILE)

    menu = """
=== Система учета доменных имен ===
1. Показать домены
2. Найти домен
3. Добавить домен
4. Продлить домен
5. Удалить домен
6. Статистика
0. Выход
"""

    while True:
        print(menu)
        choice = input("Выберите действие: ")

        if choice == "1":
            show_domains(domains)
        elif choice == "2":
            query = input_nonempty("Название или организация: ")
            found = find_domain(domains, query)
            show_domains(found)
        elif choice == "3":
            name = input_nonempty("Название домена: ")
            owner = input_nonempty("Владелец: ")
            organization = input_nonempty("Организация: ")
            registration_end = input_date("Срок действия (ДД.ММ.ГГГГ): ")
            new_id = add_domain(domains, name, owner, organization, registration_end)
            save_domains(DATA_FILE, domains)
            print(f"Домен добавлен, id = {new_id}")
        elif choice == "4":
            domain_id = input_int("id домена: ")
            new_end_date = input_date("Новый срок действия (ДД.ММ.ГГГГ): ")
            if renew_domain(domains, domain_id, new_end_date):
                save_domains(DATA_FILE, domains)
                print("Срок регистрации обновлён.")
            else:
                print("Домен с таким id не найден.")
        elif choice == "5":
            domain_id = input_int("id домена: ")
            if cancel_domain(domains, domain_id):
                save_domains(DATA_FILE, domains)
                print("Домен удалён.")
            else:
                print("Домен с таким id не найден.")
        elif choice == "6":
            show_statistics(domains)
        elif choice == "0":
            print("Завершение работы.")
            break
        else:
            print("Некорректный выбор, попробуйте снова.")


if __name__ == "__main__":
    main()
