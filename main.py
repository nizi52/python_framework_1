from datetime import date

domain_name = "example.ru"
owner = "Иванов И.И."
organization = 'ООО "Ромашка"'
registration_end = date(2026, 12, 31)


def add_domain(domain_name, owner, organization, registration_end):
    return f"Домен {domain_name} зарегистрирован на {organization}, ответственный: {owner}, срок до {registration_end}"


def get_domain_status(registration_end):
    today = date.today()
    if registration_end >= today:
        return "Домен активен"
    else:
        return "Домен истёк"


def days_until_expiration(registration_end):
    today = date.today()
    delta = registration_end - today
    return delta.days


print(add_domain(domain_name, owner, organization, registration_end))
print(get_domain_status(registration_end))
print(f"Дней до окончания регистрации: {days_until_expiration(registration_end)}")