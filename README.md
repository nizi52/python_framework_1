# Система учета доменных имен

## Назначение

Приложение для учёта доменных имён, их владельцев и организаций, а также
контроля сроков регистрации. Консольная версия приложения (ПР3) дополнена
веб-интерфейсом на Django (ПР5), страницы которого с ПР6 формируются
шаблонами Django.

Приложение позволяет:
* просматривать списки доменов, организаций, ресурсов и аренд в браузере;
* просматривать информацию о конкретном домене, организации, ресурсе и аренде;
* проверять статус домена (активен / истёк / удалён) на текущую дату;
* добавлять пользователей, организации, домены, ресурсы, оформлять и отменять
  аренду, продлевать и удалять домены (консольная версия);
* искать домены по названию и организации (консольная версия);
* получать статистику по реестру (консольная версия);
* хранить данные между запусками приложения.

## Используемые технологии

* Python 3.11+;
* Django 5.2 – веб-фреймворк;
* HTML и шаблоны Django (Django Template Language) – разметка веб-страниц;
* CSS и Bootstrap 5.3 – оформление страниц;
* JavaScript – подсветка текущего раздела и быстрый поиск по таблицам;
* pytest – автоматизированные тесты;
* flake8 – проверка качества кода;
* black – форматирование кода.

## Целевая аудитория

Администраторы доменов, IT-специалисты и небольшие организации, которым
необходимо централизованно отслеживать принадлежность и сроки действия своих
доменных имён.

## Предметная область

Пользователь может владеть несколькими доменами. Каждый домен закреплён за
организацией, имеет владельца (пользователя) и срок действия регистрации.
К домену привязываются ресурсы (хостинг, SSL, почта, DNS), а сам домен может
сдаваться пользователям в аренду на определённый срок.
Удалённый из активного использования домен не удаляется из истории – он
помечается неактивным.

## Основные сущности

### Domain – домен

Объект `Domain` представляет доменное имя.

Основные атрибуты:
* `id` – уникальный идентификатор домена;
* `name` – название домена;
* `organization` – объект `Organization`, организация, за которой закреплён домен;
* `registration_end` – срок действия регистрации;
* `owner` – объект `User`, владелец домена;
* `is_removed` – признак исключения из активного использования.

Основные методы:
* `is_active()` – проверка активности домена на текущую дату;
* `renew()` – продление срока регистрации;
* `remove()` – «мягкое» удаление (история сохраняется);
* `__str__()` – строковое представление домена.

### User – пользователь

Объект `User` представляет владельца доменов.

Основные атрибуты:
* `id` – уникальный идентификатор пользователя;
* `name` – имя пользователя;
* `email` – адрес электронной почты.

Основные методы:
* `__str__()` – строковое представление пользователя;
* `from_data()` – создание объекта `User` из набора данных.

### Organization – организация

Атрибуты: `id`, `name`. Методы: `__str__()`, `from_data()`.

### Resource – ресурс домена

Атрибуты: `id`, `name`, `kind` (тип: хостинг, SSL, почта, DNS), `domain` –
объект `Domain`. Методы: `is_active()` (ресурс активен, пока активен домен),
`__str__()`.

### Rental – аренда домена

Атрибуты: `id`, `user` – арендатор, `domain` – арендуемый домен, `start_date`
и `end_date` – срок аренды, `is_cancelled` – признак отмены.
Методы: `is_active()` (аренда действует на текущую дату), `cancel()` (отмена с
сохранением истории), `__str__()`.

## Страницы веб-интерфейса

| Адрес | Имя маршрута | View-функция | Шаблон |
|---|---|---|---|
| `/` | `homepage:index` | `index()` | `homepage/index.html` |
| `/domains/` | `domains:list` | `domain_list()` | `domains/domain_list.html` |
| `/domains/<int:domain_id>/` | `domains:detail` | `domain_detail()` | `domains/domain_detail.html` |
| `/organizations/` | `organizations:list` | `organization_list()` | `organizations/organization_list.html` |
| `/organizations/<int:organization_id>/` | `organizations:detail` | `organization_detail()` | `organizations/organization_detail.html` |
| `/resources/` | `resources:list` | `resource_list()` | `resources/resource_list.html` |
| `/resources/<int:resource_id>/` | `resources:detail` | `resource_detail()` | `resources/resource_detail.html` |
| `/rentals/` | `rentals:list` | `rental_list()` | `rentals/rental_list.html` |
| `/rentals/<int:rental_id>/` | `rentals:detail` | `rental_detail()` | `rentals/rental_detail.html` |

Если объект с указанным идентификатором не найден, страница возвращает код
статуса 404 и шаблон `not_found.html`. Для любого адреса, которому не нашлось
маршрута, работает собственная страница 404 (`handler404` → `page_not_found()`,
шаблон `404.html`).

## Шаблоны Django (ПР6)

HTML больше не формируется в Python: функция `page()` и f-строки с разметкой
удалены, view-функции готовят словарь контекста и вызывают `render()`.

* `templates/base.html` – базовый шаблон: `<head>`, Bootstrap, собственный CSS,
  навигация, подвал, JavaScript и блоки `{% block title %}`, `{% block content %}`;
* все страницы наследуют его через `{% extends "base.html" %}`;
* `templates/includes/` – включаемые шаблоны (`{% include %}`):
  `nav.html` (навигация), `footer.html` (подвал), `badge.html` (бейдж статуса),
  `table_filter.html` (поле быстрого поиска по таблице);
* в шаблонах используются `{% for %}` с `{% empty %}`, `{% if %}`, `{% with %}`
  и обработка пустых списков;
* ссылки строятся через `{% url %}` по именам маршрутов с пространствами имён
  (`app_name` в `urls.py` каждого приложения): `{% url 'domains:detail' row.domain.id %}`;
* фильтры шаблонов: `date` (формат дат), `length` (количество записей),
  `default`, `lower`, `upper`, `timeuntil` (сколько осталось до окончания
  регистрации), тег `{% now %}`;
* статические файлы (`{% load static %}`): `static/css/style.css` – оформление
  (цвета вынесены из Python в CSS), `static/img/logo.svg` – логотип в навигации,
  `static/js/main.js` – подсветка текущего раздела и фильтрация строк таблицы.

Каталоги шаблонов и статики подключены в `settings.py`:
`TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]`, `STATICFILES_DIRS = [BASE_DIR / "static"]`.

## Основные операции

### Используется в веб-интерфейсе (ПР5–ПР6)

* просмотр списка доменов;
* просмотр информации о домене, его владельце, организации, ресурсах и аренде;
* проверка статуса домена на текущую дату;
* быстрый поиск по таблицам доменов, ресурсов и аренд (JavaScript, ПР6).

### Отложено до следующих работ

Эти операции реализованы в ПР3 и работают в консольной версии. В веб-интерфейсе
они появятся, когда будут добавлены формы и POST-запросы:

* добавление домена, пользователя, организации, ресурса и аренды;
* поиск домена и пользователя;
* фильтрация доменов по организации;
* сортировка доменов по сроку регистрации;
* продление и удаление домена, отмена аренды;
* статистика по реестру.

## Хранение данных

Данные приложения хранятся в JSON-файлах:
* `data/domains.json`;
* `data/users.json`;
* `data/organizations.json`;
* `data/resources.json`;
* `data/rentals.json`.

При загрузке данные из JSON преобразуются в объекты `Domain` и `User`, при
сохранении объекты преобразуются в данные JSON. Для связи домена с владельцем
в `domains.json` используются идентификаторы `owner_id` и `organization_id`,
в `resources.json` – `domain_id`, в `rentals.json` – `user_id` и `domain_id`.

## Структура проекта

```text
domain_registry/
│
├── README.md
├── requirements.txt
├── setup.cfg
├── pyproject.toml
├── manage.py
├── main.py
├── storage.py
├── utils.py
│
├── domainreg/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── homepage/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── domains/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── organizations/   (аналогичная структура)
├── resources/       (аналогичная структура)
├── rentals/         (аналогичная структура)
│
├── models/
│   ├── __init__.py
│   ├── domains.py
│   ├── organizations.py
│   ├── resources.py
│   ├── rentals.py
│   └── users.py
│
├── data/
│   ├── domains.json
│   ├── users.json
│   ├── organizations.json
│   ├── resources.json
│   └── rentals.json
│
├── templates/
│   ├── base.html
│   ├── 404.html
│   ├── not_found.html
│   ├── includes/        (nav, footer, badge, table_filter)
│   ├── homepage/index.html
│   ├── domains/         (domain_list.html, domain_detail.html)
│   ├── organizations/   (organization_list.html, organization_detail.html)
│   ├── resources/       (resource_list.html, resource_detail.html)
│   └── rentals/         (rental_list.html, rental_detail.html)
│
├── static/
│   ├── css/style.css
│   ├── img/logo.svg
│   └── js/main.js
│
└── tests/
    ├── test_views.py
    ├── test_domains.py
    ├── test_users.py
    ├── test_organizations.py
    ├── test_resources.py
    └── test_rentals.py
```

## Назначение модулей

### `main.py`

Консольная версия приложения (сохранена с ПР3): запуск, меню, ввод данных,
пользовательские сценарии.

### `domainreg/`

Пакет настроек Django-проекта:
* `settings.py` – настройки проекта (приложения, язык, часовой пояс);
* `urls.py` – маршрутизация верхнего уровня и обработчик 404;
* `asgi.py`, `wsgi.py` – точки взаимодействия с сервером.

### `homepage/`

Django-приложение, отвечающее за главную страницу:
* `views.py` – вспомогательные `load_data()` и `not_found()` (ответ 404 по шаблону
  `not_found.html`), view-функции `index()` и `page_not_found()`;
* `urls.py` – маршрут главной страницы (`app_name = "homepage"`).

Общий вид всех страниц задаётся базовым шаблоном `templates/base.html`.

### `domains/`

Django-приложение, отвечающее за домены:
* `views.py` – view-функции `domain_list()` и `domain_detail()`, `get_status_label()`;
* `urls.py` – маршруты приложения (`app_name = "domains"`, имена `list`, `detail`);
* `models.py` – Django-модели (заполняется в следующих работах).

### `organizations/`, `resources/`, `rentals/`

Django-приложения для организаций, ресурсов и аренды. В каждом: `views.py` –
view-функции списка и страницы объекта, `urls.py` – маршруты приложения,
`models.py` – Django-модели (заполняется в следующих работах).

Отдельное приложение для пользователей не создаётся: Django предоставляет
встроенную модель `User` (`django.contrib.auth`).

### `models/`

Классы предметной области и функции работы с ними (пакет ПР3):
* `domains.py` – класс `Domain` и функции работы с доменами;
* `users.py` – класс `User` и функции работы с пользователями;
* `organizations.py` – класс `Organization` и функции работы с организациями;
* `resources.py` – класс `Resource` и функции работы с ресурсами;
* `rentals.py` – класс `Rental` и функции работы с арендой.

### `storage.py`

Загрузка и сохранение данных: JSON → объекты Python и объекты Python → JSON.

### `utils.py`

Вспомогательные функции консольного ввода: `input_int()`, `input_date()`,
`input_nonempty()`.

### `tests/`

Автоматизированные тесты pytest: сущности `Domain`, `User`, `Organization`, `Resource`,
`Rental` и веб-страницы (`test_views.py`: шаблоны, контекст, именованные URL, статика, 404).

## Запуск приложения

Установка зависимостей:
```text
pip install -r requirements.txt
```

Веб-версия (Django):
```text
python manage.py migrate
python manage.py runserver
```

После запуска открыть в браузере адрес:
```text
http://127.0.0.1:8000/
```

Консольная версия (сохранена):
```text
python main.py
```

## Тестирование

```text
pytest -v
```

## Проверка качества кода

Соответствие PEP 8 проверяется `flake8`, форматирование выполняет `black`:
```text
flake8 .
black .
```

## Зависимости

Состав зависимостей в `requirements.txt`:
* `Django==5.2.*` – веб-фреймворк;
* `pytest` – автоматизированные тесты;
* `flake8` – проверка качества кода;
* `black` – форматирование кода.

## Git

Исходный код проекта хранится в Git-репозитории. Коммиты начинаются с
метки текущей работы: `PR5:`, `PR6:`. Проверка состояния репозитория:
```text
git status
```

## Текущее состояние и план развития

Реализовано (ПР5):
* Django-проект `domainreg` и пять Django-приложений (`homepage`, `domains`,
  `organizations`, `resources`, `rentals`);
* маршрутизация URL двух уровней, динамический URL с конвертером `<int:...>`;
* view-функции и страницы;
* отображение данных предметной области (домены и их владельцы);
* проверка статуса домена через логику ПР3 (`Domain.is_active()`);
* собственная страница 404;
* навигация между страницами;
* оформление Bootstrap 5.3.

Реализовано (ПР6):
* перевод всех страниц на шаблоны Django, базовый шаблон и наследование;
* блоки `{% block %}` и включаемые шаблоны `{% include %}`;
* передача данных из view в шаблон через контекст;
* циклы, условия и обработка пустых коллекций в шаблонах;
* пространства имён приложений и ссылки `{% url %}`;
* фильтры шаблонов;
* собственный CSS, изображение и JavaScript из каталога `static/`;
* отказ от функции `page()`; данные по-прежнему хранятся в JSON (ORM не внедрялся).

Планируется:
* перенос сущностей `Domain` и `User` в Django ORM;
* подключение базы данных;
* формы создания и редактирования доменов;
* использование отложенной логики ПР3 (добавление, поиск, сортировка,
  продление, удаление, статистика);
* реализация пользователей (регистрация, вход);
* разработка API;
* контейнеризация приложения;
* настройка CI/CD.

## Функции проекта

Сущность Domain – домен (ПР3):

| Имя функции | Файл | Назначение |
|---|---|---|
| `Domain` (класс) | `models/domains.py` | домен: id, name, organization, registration_end, owner, is_removed |
| `is_active()` | `models/domains.py` | активность домена на текущую дату; используется страницами |
| `renew()` / `remove()` | `models/domains.py` | продление срока / «мягкое» удаление |
| `add_domain()` | `models/domains.py` | создание объекта `Domain` и добавление в коллекцию |
| `find_domain()` | `models/domains.py` | поиск по названию и названию организации |
| `find_domain_by_id()` | `models/domains.py` | поиск по идентификатору; используется страницей домена |
| `filter_domains_by_organization()` | `models/domains.py` | отбор доменов по id организации; используется страницей организации |
| `sort_domains_by_expiration()` | `models/domains.py` | сортировка по сроку регистрации |
| `renew_domain()` / `remove_domain()` | `models/domains.py` | поиск домена по id и вызов `renew()` / `remove()` |
| `get_domain_status()` | `models/domains.py` | текстовый статус домена (функция из ПР1) |
| `domain_statistics()` | `models/domains.py` | статистика по реестру |
| `show_domains()` | `models/domains.py` | вывод доменов в консоль |

Сущность User – пользователь (ПР3):

| Имя функции | Файл | Назначение |
|---|---|---|
| `User` (класс) | `models/users.py` | пользователь: id, name, email |
| `from_data()` | `models/users.py` | создание `User` из набора данных JSON |
| `add_user()` | `models/users.py` | создание объекта `User` и добавление в коллекцию |
| `find_user()` | `models/users.py` | поиск по имени или email |
| `find_user_by_id()` | `models/users.py` | поиск по идентификатору; используется при загрузке доменов |
| `show_users()` | `models/users.py` | вывод пользователей в консоль |

Сущность Organization – организация:

| Имя функции | Файл | Назначение |
|---|---|---|
| `Organization` (класс) | `models/organizations.py` | организация: id, name |
| `from_data()` | `models/organizations.py` | создание `Organization` из данных JSON |
| `add_organization()` / `find_organization()` | `models/organizations.py` | добавление / поиск по названию |
| `find_organization_by_id()` | `models/organizations.py` | поиск по id; используется при загрузке доменов и страницей организации |
| `show_organizations()` | `models/organizations.py` | вывод в консоль |

Сущность Resource – ресурс домена:

| Имя функции | Файл | Назначение |
|---|---|---|
| `Resource` (класс) | `models/resources.py` | ресурс: id, name, kind, domain |
| `is_active()` | `models/resources.py` | активность ресурса (по домену) |
| `add_resource()` | `models/resources.py` | создание ресурса и добавление в коллекцию |
| `find_resource_by_id()` | `models/resources.py` | поиск по id; используется страницей ресурса |
| `filter_resources_by_domain()` | `models/resources.py` | ресурсы домена; используется страницей домена |
| `show_resources()` | `models/resources.py` | вывод в консоль |

Сущность Rental – аренда домена:

| Имя функции | Файл | Назначение |
|---|---|---|
| `Rental` (класс) | `models/rentals.py` | аренда: id, user, domain, start_date, end_date, is_cancelled |
| `is_active()` / `cancel()` | `models/rentals.py` | действует ли аренда / отмена с сохранением истории |
| `create_rental()` | `models/rentals.py` | создание аренды и добавление в коллекцию |
| `find_rental_by_id()` | `models/rentals.py` | поиск по id; используется страницей аренды |
| `cancel_rental()` | `models/rentals.py` | поиск аренды по id и вызов `cancel()` |
| `get_rental_status()` | `models/rentals.py` | текстовый статус: действует / завершена / отменена |
| `show_rentals()` | `models/rentals.py` | вывод в консоль |

Хранение данных (`storage.py`, ПР3):

| Имя функции | Назначение |
|---|---|
| `load_users()` / `save_users()` | `data/users.json` ↔ объекты `User` |
| `load_organizations()` / `save_organizations()` | `data/organizations.json` ↔ объекты `Organization` |
| `load_domains()` / `save_domains()` | `data/domains.json` ↔ объекты `Domain` (связи по `owner_id`, `organization_id`) |
| `load_resources()` / `save_resources()` | `data/resources.json` ↔ объекты `Resource` |
| `load_rentals()` / `save_rentals()` | `data/rentals.json` ↔ объекты `Rental` |
| `load_registry()` | загрузка всех файлов и связывание объектов; используется веб-страницами |

Веб-слой (ПР5):

| Имя функции | Файл | Назначение |
|---|---|---|
| `page()` | `homepage/views.py` | единый HTML-каркас: кодировка, заголовок, Bootstrap 5.3, навигация |
| `index()` | `homepage/views.py` | главная страница `/` |
| `page_not_found()` | `homepage/views.py` | собственная страница 404 |
| `load_data()` | `homepage/views.py` | загрузка всех данных ПР3 (`load_registry()`) |
| `badge()` / `not_found_page()` | `homepage/views.py` | бейдж статуса / страница «не найдено» с кодом 404 |
| `get_status_label()` | `domains/views.py` | текст статуса и цвет бейджа Bootstrap |
| `domains()` | `domains/views.py` | страница `/domains/`: список доменов |
| `domain_detail()` | `domains/views.py` | страница `/domains/<int:domain_id>/`; если домен не найден – 404 |
| `organizations()` / `organization_detail()` | `organizations/views.py` | список организаций и страница организации |
| `resources()` / `resource_detail()` | `resources/views.py` | список ресурсов и страница ресурса |
| `rentals()` / `rental_detail()` | `rentals/views.py` | список аренд и страница аренды |

Функции сущностей и хранилища используются одновременно консольной и веб-версией
приложения: view-функции вызывают `load_domains()`, `load_users()` и
`find_domain_by_id()` вместо консольных сценариев `main.py`.
