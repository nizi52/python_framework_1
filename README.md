# Система учета доменных имен

## Назначение

Приложение для учёта доменных имён, их владельцев и организаций, а также
контроля сроков регистрации. Консольная версия приложения (ПР3) дополнена
веб-интерфейсом на Django (ПР5), страницы которого с ПР6 формируются
шаблонами Django. С ПР7 данные хранятся в базе SQLite, а с ПР9 страницы получают
их через Django ORM: модели, миграции, связи между таблицами. В ПР10 настроена
административная панель Django, статус аренды хранится полем с вариантами выбора,
у страниц доменов появились адреса по slug.

Приложение позволяет:
* просматривать списки доменов, организаций, ресурсов и аренд в браузере;
* искать домены по названию, организации и владельцу и сортировать их (ПР9);
* фильтровать список аренд по статусу (ПР10), дате, домену и арендатору, сортировать
  его и листать по страницам (ПР9);
* управлять доменами, арендами, пользователями, организациями и ресурсами в
  административной панели `/admin/` (ПР10);
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
* SQLite – хранение данных; модуль `sqlite3` и SQL-запросы использовались в ПР7,
  с ПР9 доступ к данным в веб-интерфейсе идёт через Django ORM;
* Django ORM и миграции – модели, связи `ForeignKey`, запросы (ПР9);
* Django Admin – административная панель (ПР10);
* Django Debug Toolbar – анализ SQL-запросов при разработке (ПР10);
* Unidecode – транслитерация названий при формировании slug (ПР10);
* HTML и шаблоны Django (Django Template Language) – разметка веб-страниц;
* CSS и Bootstrap 5.3 – оформление страниц;
* JavaScript – подсветка текущего раздела и быстрый поиск по таблицам;
* pytest и pytest-django – автоматизированные тесты;
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
и `end_date` – срок аренды, `is_cancelled` – признак отмены (в консольной версии и
JSON; в модели Django с ПР10 вместо него поле `status`).
Методы: `is_active()` (аренда действует на текущую дату), `cancel()` (отмена с
сохранением истории), `__str__()`.

## Страницы веб-интерфейса

| Адрес | Имя маршрута | View-функция | Шаблон |
|---|---|---|---|
| `/` | `homepage:index` | `index()` | `homepage/index.html` |
| `/domains/?q=...&sort=...` | `domains:list` | `domain_list()` | `domains/domain_list.html` |
| `/domains/<slug:slug>/` | `domains:detail` | `domain_detail()` | `domains/domain_detail.html` |
| `/domains/<int:domain_id>/` | `domains:detail_by_id` | `domain_detail_by_id()` | перенаправление 301 на адрес по slug |
| `/organizations/` | `organizations:list` | `organization_list()` | `organizations/organization_list.html` |
| `/organizations/<int:organization_id>/` | `organizations:detail` | `organization_detail()` | `organizations/organization_detail.html` |
| `/resources/` | `resources:list` | `resource_list()` | `resources/resource_list.html` |
| `/resources/<int:resource_id>/` | `resources:detail` | `resource_detail()` | `resources/resource_detail.html` |
| `/rentals/?status=...&date=...&domain=<id>&user=<id>&sort=...&page=N` | `rentals:list` | `rental_list()` | `rentals/rental_list.html` |
| `/rentals/<int:rental_id>/` | `rentals:detail` | `rental_detail()` | `rentals/rental_detail.html` |
| `/domains/available/?date=ГГГГ-ММ-ДД` | `domains:available` | `available_domains()` | `domains/available.html` |
| `/domains/expiring/?days=N` | `domains:expiring` | `expiring_domains()` | `domains/expiring.html` |
| `/statistics/` | `homepage:statistics` | `statistics()` | `homepage/statistics.html` |
| `/admin/` | `admin:index` | Django Admin | шаблоны `django.contrib.admin` |

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
* быстрый поиск по таблицам доменов, ресурсов и аренд (JavaScript, ПР6);
* поиск и сортировка доменов, фильтрация, сортировка и пагинация аренд, свободные
  и истекающие домены, статистика (Django ORM, ПР9).

### Отложено до следующих работ

Эти операции реализованы в ПР3 и работают в консольной версии. В веб-интерфейсе
они появятся, когда будут добавлены формы и POST-запросы:

* добавление домена, пользователя, организации, ресурса и аренды;
* поиск домена и пользователя;
* фильтрация доменов по организации;
* продление и удаление домена, отмена аренды (методы `renew()`, `remove()`, `cancel()`
  есть у моделей Django, но через веб-интерфейс пока недоступны).

## База данных SQLite (ПР7)

С ПР7 веб-интерфейс работает с реляционной базой `data/domainreg.sqlite`.
JSON-файлы каталога `data/` сохранены: из них база заполняется скриптом импорта,
и с ними по-прежнему работает консольная версия `main.py`. На этапе ПР7 запросы
выполнялись библиотекой `sqlite3`. С ПР9 файл `data/domainreg.sqlite` остаётся
исходной базой (источником данных для переноса), а страницы работают с базой Django
`db.sqlite3` через ORM (раздел «Django ORM и модели (ПР9)»).

### Структура базы

| Таблица | Поля | Ключи |
|---|---|---|
| `users` | `id INTEGER`, `name TEXT`, `email TEXT` (уникальный) | PK `id` |
| `organizations` | `id INTEGER`, `name TEXT` | PK `id` |
| `domains` | `id INTEGER`, `name TEXT` (уникальный), `organization_id INTEGER`, `owner_id INTEGER`, `registration_end TEXT` (ГГГГ-ММ-ДД), `is_removed INTEGER` (0/1) | PK `id`; FK `organization_id → organizations.id`, `owner_id → users.id` |
| `resources` | `id INTEGER`, `name TEXT`, `kind TEXT`, `domain_id INTEGER` | PK `id`; FK `domain_id → domains.id` |
| `rentals` | `id INTEGER`, `user_id INTEGER`, `domain_id INTEGER`, `start_date TEXT`, `end_date TEXT`, `is_cancelled INTEGER` (0/1) | PK `id`; FK `user_id → users.id`, `domain_id → domains.id`; CHECK `start_date <= end_date` |

Связи: организация и пользователь могут иметь несколько доменов; у домена может
быть несколько ресурсов и аренд; каждая аренда относится к одному домену и
одному пользователю. Даты хранятся строками ГГГГ-ММ-ДД – их можно сравнивать
и сортировать средствами SQL, логические признаки – числами 0/1.

### Файлы

* `sql/schema.sql` – создание таблиц (`CREATE TABLE IF NOT EXISTS`, PRIMARY KEY,
  FOREIGN KEY, NOT NULL, DEFAULT, UNIQUE, CHECK);
* `sql/queries.sql` – 18 SQL-запросов проекта с комментариями: выборка и
  сортировка, `WHERE` (в том числе `BETWEEN`, `LIKE`), `JOIN`, подзапрос `NOT IN`,
  агрегатные функции `COUNT`, `MIN`, `MAX`, `AVG`, `GROUP BY`, `HAVING`,
  `LIMIT`/`OFFSET`, `CASE`;
* `db/database.py` – подключение: `get_connection()` включает
  `PRAGMA foreign_keys = ON` и `row_factory = sqlite3.Row`, функции
  `fetch_all()` / `fetch_one()` выполняют запрос с параметрами `?`;
* `db/import_json.py` – перенос данных из JSON в таблицы (`executemany`,
  транзакция с `commit()` / `rollback()`), запуск повторно безопасен;
* `data/domainreg.sqlite` – файл базы данных.

### Создание и заполнение базы

Из корня проекта:
```text
python -m db.import_json
```
Скрипт создаёт таблицы по `sql/schema.sql`, очищает их и переносит данные из
JSON. После изменения JSON-файлов (например, через консольную версию) импорт
нужно запустить повторно.

Проверка запросов в SQLite CLI:
```text
sqlite3 data/domainreg.sqlite
.read sql/queries.sql
.exit
```

### Страницы ПР7 (SQL-запросы; с ПР9 те же страницы работают через ORM)

* «Домены» – список доменов с организацией, владельцем и статусом (`JOIN`,
  статус вычисляется `CASE`), карточка домена с ресурсами и арендами;
* «Свободные для аренды» – поиск доменов, свободных на выбранную дату
  (подзапрос `NOT IN`, дата передаётся параметром `?`);
* «Истекающие» – домены, срок регистрации которых заканчивается в ближайшие
  N дней (`BETWEEN`, параметр `?`);
* «Организации» – число доменов у каждой организации (`LEFT JOIN`, `GROUP BY`);
* «Ресурсы», «Аренда» – списки и карточки (`JOIN` двух и трёх таблиц);
* «Статистика» – сводные показатели (`COUNT`, `SUM`, `MIN`, `MAX`, `AVG`),
  группировки по организациям, доменам и типам ресурсов, фильтр групп `HAVING`.

Все значения, которые приходят от пользователя (дата, число дней, минимум
ресурсов), передаются в запрос только параметрами `?` – подстановка значений
f-строками в текст SQL не используется.

## Django ORM и модели (ПР9)

В ПР9 слой доступа к данным переведён с SQL-запросов `sqlite3` на Django ORM.
Предметная область, маршруты, шаблоны и пользовательские сценарии ПР1–ПР7 сохранены.

### Какая база используется

| Файл | Роль |
|---|---|
| `data/domainreg.sqlite` | исходная база ПР7: только источник данных для переноса, не изменяется |
| `db.sqlite3` | база Django (`DATABASES` в `settings.py`): таблицы создаются миграциями, страницы читают данные из неё |

Выбрана стратегия «таблицы, управляемые Django, и перенос данных»: миграции
применяются к `db.sqlite3`, данные переносятся из `data/domainreg.sqlite`
с сохранением идентификаторов и связей.

### Модели

| Модель | Приложение | Поля | Связи |
|---|---|---|---|
| `User` | `users` | `name`, `email` (уникальный) | обратные: `owned_domains`, `rentals` |
| `Organization` | `organizations` | `name` | обратная: `domains` |
| `Domain` | `domains` | `name` (уникальный), `registration_end` (`DateField`), `is_removed` | `organization` → `Organization` (`PROTECT`, `related_name="domains"`), `owner` → `User` (`PROTECT`, `related_name="owned_domains"`) |
| `Resource` | `resources` | `name`, `kind` | `domain` → `Domain` (`PROTECT`, `related_name="resources"`) |
| `Rental` | `rentals` | `start_date`, `end_date` (`DateField`), `is_cancelled`; ограничение `start_date <= end_date` | `user` → `User` (`PROTECT`, `related_name="rentals"`), `domain` → `Domain` (`PROTECT`, `related_name="rentals"`) |

Первичный ключ `id` Django создаёт автоматически. `on_delete=PROTECT` запрещает
удалять организацию, пользователя или домен, пока на них ссылаются другие записи, -
история не теряется. Модель `users.User` описывает человека из реестра доменов и не
связана со встроенной моделью аутентификации Django.

Методы моделей: `Domain.get_status()`, `is_active()`, `renew()`, `remove()`;
`Rental.cancel()`, `duration_days`; `Resource.is_available()`. Запросы моделей
вынесены в `QuerySet`-методы: `Domain.objects.in_registry()`, `with_status()`,
`as_rows()`, `Rental.objects.not_cancelled()`, `active_on(day)` и аналогичные.
Статус домена, аренды и ресурса на дату вычисляется в базе выражением
`Case`/`When`.

### Миграции и перенос данных

Из корня проекта:
```text
python db/inspect_source_db.py
python manage.py makemigrations
python manage.py showmigrations
python manage.py migrate
python db/import_sqlite_to_orm.py
```
* `db/inspect_source_db.py` - осмотр исходной базы: таблицы, столбцы, число записей,
  проверка ссылок и формата дат, база только читается;
* `db/import_sqlite_to_orm.py` - перенос одной транзакцией в порядке зависимостей
  (пользователи, организации, домены, ресурсы, аренды) через `update_or_create(pk=...)`;
  запуск повторно безопасен, исходная база не изменяется;
* файлы миграций (`*/migrations/0001_initial.py`) хранятся в репозитории.

Команда `python manage.py migrate` применяется к `db.sqlite3` и не затрагивает
`data/domainreg.sqlite`. Файл `db.sqlite3` указан в `.gitignore`, но уже находится под
контролем версий (был добавлен в прошлых коммитах), поэтому после переноса данных он
отображается в `git status` как изменённый.

### Параметры запросов страниц

* `/domains/?q=...&sort=...` - `q`: подстрока в названии домена, организации или имени
  владельца без учёта регистра (в том числе для кириллицы); `sort`: `name`, `end`,
  `organization`, `owner` (неизвестное значение заменяется на `name`);
* `/rentals/?...` - `status` (с ПР10: по умолчанию активные, `completed`, `cancelled`, `all`;
  `all=1` из ПР9 работает как `status=all`), `date=ГГГГ-ММ-ДД` (аренды, действующие
  в этот день), `domain=<id>`, `user=<id>`, `sort=start`, `end`, `domain` или `user`,
  `page=N` (по 5 записей на странице); некорректные значения игнорируются, для даты
  выводится сообщение; ссылки навигации сохраняют фильтры и сортировку
  (`{% querystring %}`);
* `/domains/available/?date=...`, `/domains/expiring/?days=N`,
  `/statistics/?min_resources=N` - как в ПР7, но через ORM.

Поле сортировки выбирается только из заданного в коде словаря, значения от
пользователя в `order_by()` напрямую не передаются.

### ORM-выражения проекта

| № | Вид | Выражение | Где используется |
|---|---|---|---|
| 1 | получение набора | `Domain.objects.all()...as_rows()` | `domain_list` |
| 2 | получение набора | `Resource.objects.order_by("domain__name", "kind").as_rows()` | `resource_list` |
| 3 | один объект | `Domain.objects.select_related(...).with_status().get(pk=...)`, `DoesNotExist` → 404 | детальные страницы |
| 4 | фильтр, несколько условий | `Domain.objects.in_registry().filter(registration_end__gte=day)` | `available_domains` |
| 5 | фильтр, несколько условий | `Rental.objects.filter(start_date__lte=day, end_date__gte=day)` | `rental_list`, `active_on()` |
| 6 | фильтр по связанной модели | `filter(Q(organization__name__uicontains=q) \| Q(owner__name__uicontains=q))` | `domain_list` |
| 7 | фильтр по внешнему ключу | `Domain.objects.filter(organization=organization)`, `filter(domain_id=...)` | `organization_detail`, `rental_list` |
| 8 | исключение | `.exclude(pk__in=Rental.objects.active_on(day).values("domain_id"))` | `available_domains` |
| 9 | поиск по строке | `name__uicontains=q` | `domain_list` |
| 10 | поиск по нескольким полям | `Q(...) \| Q(...) \| Q(...)` | `domain_list` |
| 11 | диапазон дат | `registration_end__range=(today, today + timedelta(days=n))` | `expiring_domains` |
| 12 | сортировка по полям | `order_by("registration_end", "name")` | `expiring_domains` |
| 13 | сортировка по выбору, по связанному полю | `order_by(SORT_FIELDS[sort], "id")`, `organization__name`, `domain__name` | `domain_list`, `rental_list` |
| 14 | связи | `select_related("organization", "owner")`, `select_related("domain", "user")` | детальные страницы |
| 15 | связи | `Organization.objects.prefetch_related("domains")` | `organization_list` |
| 16 | обратные связи | `domain.resources.order_by("kind")`, `domain.rentals.select_related("user")` | `domain_detail` |
| 17 | `aggregate` | `Domain.objects.aggregate(Count, Min(filter=...), Max)` | `statistics`, `index` |
| 18 | `aggregate` | `Rental.objects.not_cancelled().aggregate(Avg(F("end_date") - F("start_date")))` | `statistics` |
| 19 | `annotate` | `Organization.objects.annotate(domains_count=Count("domains"))` (организации без доменов не пропадают) | `organization_list`, `statistics` |
| 20 | `annotate` с условием | `Count("rentals", filter=Q(rentals__status=Rental.Status.ACTIVE))` | `statistics` |
| 21 | группировка | `Resource.objects.values("kind").annotate(Count("id"))` | `statistics` |
| 22 | фильтр групп | `annotate(resources_count=Count("resources")).filter(resources_count__gte=n)` | `statistics` |
| 23 | `values` с выражениями | `values(..., organization_name=F("organization__name"))` | `as_rows()` |
| 24 | `annotate` с `Case`/`When` | статус домена, аренды, ресурса на дату | `with_status()` |
| 25 | пагинация | `Paginator(rows, 5).get_page(request.GET.get("page"))` | `rental_list` |

Прямых SQL-запросов в `views.py` больше нет (это проверяет тест). Файл
`sql/queries.sql` и пакет `db/` сохранены как материалы ПР7 и источник данных для
переноса.

## Административная панель и ORM (ПР10)

Пример Roomly из методички перенесён на предметную область так: помещение (Room) –
домен (`Domain`), бронирование (Booking) – аренда (`Rental`), пользователь – `User`.

### Django Admin

Адрес `/admin/`. Вход под суперпользователем Django (`python manage.py createsuperuser`).
Названия приложений русские (`verbose_name` в `apps.py`), у моделей и полей –
`verbose_name`.

| Модель | Настройки |
|---|---|
| `Domain` | столбцы с организацией, владельцем, датой, признаками и числом активных аренд (`annotate`); поиск по названию, организации, владельцу; фильтры по исключению, зоне, организации; `list_editable` для даты окончания; `readonly_fields` (`id`, `slug`, `is_ru_zone`); `autocomplete_fields`; `list_select_related`; встроенные формы ресурсов и аренд; ссылки «Смотреть на сайте» и «Страница на сайте» (`get_absolute_url()`) |
| `Rental` | поиск по домену, арендатору и его почте; фильтры по статусу и дате начала; `date_hierarchy`; `autocomplete_fields`; `list_select_related`; действия «Отменить выбранные аренды» и «Вернуть в активные» |
| `User` | поиск по имени и почте, аренды пользователя во встроенной форме |
| `Organization`, `Resource` | столбцы, поиск, сортировка, у ресурсов фильтр по типу |

Админ-панель не проверяет бизнес-правила: при создании аренды или возврате её в
активные пересечение с другими арендами домена не проверяется.

### Статус аренды (TextChoices)

Булево поле `Rental.is_cancelled` заменено полем `status`: `active` (активна),
`cancelled` (отменена), `completed` (завершена). Миграции `rentals`: `0002` добавляет
поле, `0003` переносит данные (отменённые – `cancelled`, остальные – `active`), `0004`
удаляет `is_cancelled`. Статус `completed` по прошедшей дате автоматически не ставится,
его задаёт администратор.

Методы `RentalQuerySet`: `active()`, `cancelled()`, `completed()`, `not_cancelled()`,
`for_date(day)`, `active_on(day)` (только активные аренды на дату: они и блокируют домен),
`with_state()` – состояние на дату для страниц (запланирована, действует, завершена,
отменена).

### Slug, get_absolute_url и GeneratedField у домена

* `slug` – из названия домена и id: точки заменяются дефисами, кириллица
  транслитерируется (`example.ru`, id 1 → `example-ru-1`). Миграции `domains`: `0002`
  добавляет поле, `0003` заполняет его, `0004` делает уникальным. Новому домену slug
  задаётся в `save()` и при переименовании не меняется;
* `get_absolute_url()` – адрес `/domains/<slug>/`, используется в шаблонах и админке;
  старые адреса `/domains/<id>/` перенаправляют на новые;
* `is_ru_zone` – `GeneratedField` (миграция `0005`): домен в зоне `.ru` или `.рф`,
  значение вычисляет SQLite и хранит в таблице.

### Контекстный процессор

`homepage/context_processors.py` – `registry_context()` передаёт во все шаблоны
`app_title` и `registry_domains_count` (число доменов в реестре, выводится в подвале).
Запрос подсчёта выполняется только там, где значение выводится.

### Django Debug Toolbar

Подключается в `settings.py` и `urls.py` только при `DEBUG = True` и не подключается при
запуске тестов (`ENABLE_DEBUG_TOOLBAR`). Панель видна на страницах при открытии сайта с
`127.0.0.1` (`INTERNAL_IPS`). Результаты проверки:

| Страница | SQL-запросов | Что выполняется |
|---|---|---|
| `/rentals/` | 5 | подсчёт для пагинации, домены и арендаторы для фильтров, аренды одной выборкой с `JOIN` (`values()` и `F()`), число доменов в подвале |
| `/rentals/<id>/` | 2 | аренда с доменом и арендатором (`select_related`), число доменов в подвале |
| `/domains/<slug>/` | 4 | домен с организацией и владельцем, ресурсы, аренды с арендаторами, число доменов |

### Поиск по кириллице

Встроенный `icontains` в SQLite не учитывает регистр кириллицы, поэтому добавлен
lookup `uicontains` (`homepage/search.py`): в соединение SQLite регистрируется
функция `UNICODE_LOWER` (`str.casefold`), символы `%` и `_` в запросе экранируются.

## Хранение данных

Исходные данные приложения хранятся в JSON-файлах:
* `data/domains.json`;
* `data/users.json`;
* `data/organizations.json`;
* `data/resources.json`;
* `data/rentals.json`.

Консольная версия работает с JSON напрямую: при загрузке данные преобразуются в
объекты `Domain`, `User` и др., при сохранении – обратно в JSON. Для связей
используются идентификаторы `owner_id`, `organization_id`, `domain_id`,
`user_id`. Веб-интерфейс с ПР7 читает данные из SQLite (см. выше).

## Структура проекта

```text
domain_registry/
│
├── README.md
├── requirements.txt
├── db.sqlite3          (база Django, ПР9)
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
│   ├── search.py        (lookup uicontains для кириллицы)
│   ├── context_processors.py  (общие данные шаблонов, ПР10)
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
├── organizations/   (аналогичная структура, migrations/0001_initial.py)
├── resources/       (аналогичная структура, migrations/0001_initial.py)
├── rentals/         (аналогичная структура, migrations/0001_initial.py)
├── users/           (models.py, admin.py, migrations/0001_initial.py)
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
│   ├── rentals.json
│   └── domainreg.sqlite
│
├── db/
│   ├── __init__.py
│   ├── database.py
│   ├── import_json.py
│   ├── inspect_source_db.py
│   └── import_sqlite_to_orm.py
│
├── sql/
│   ├── schema.sql
│   └── queries.sql
│
├── templates/
│   ├── base.html
│   ├── 404.html
│   ├── not_found.html
│   ├── includes/        (nav, footer, badge, table_filter, domain_table, domain_actions)
│   ├── homepage/        (index.html, statistics.html)
│   ├── domains/         (domain_list, domain_detail, available, expiring)
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
    ├── conftest.py
    ├── test_database.py
    ├── test_views.py
    ├── test_models.py
    ├── test_import.py
    ├── test_pr10.py
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
* `settings.py` – настройки проекта (приложения, язык, часовой пояс, база `db.sqlite3`);
* `urls.py` – маршрутизация верхнего уровня и обработчик 404;
* `asgi.py`, `wsgi.py` – точки взаимодействия с сервером.

### `homepage/`

Django-приложение, отвечающее за главную страницу:
* `views.py` – вспомогательные `load_data()` и `not_found()` (ответ 404 по шаблону
  `not_found.html`), view-функции `index()`, `statistics()` (aggregate/annotate) и
  `page_not_found()`;
* `search.py` – функция `UNICODE_LOWER` и lookup `uicontains` для поиска по кириллице;
* `urls.py` – маршрут главной страницы (`app_name = "homepage"`).

Общий вид всех страниц задаётся базовым шаблоном `templates/base.html`.

### `domains/`

Django-приложение, отвечающее за домены:
* `models.py` – модель `Domain` и `DomainQuerySet`;
* `views.py` – `domain_list()` (поиск, сортировка), `domain_detail()`,
  `available_domains()`, `expiring_domains()`, `parse_date()`;
* `urls.py` – маршруты приложения (`app_name = "domains"`);
* `admin.py` – регистрация модели в админ-панели.

### `organizations/`, `resources/`, `rentals/`

Django-приложения для организаций, ресурсов и аренды. В каждом: `models.py` – модель
и её `QuerySet`, `views.py` – view-функции списка и страницы объекта (у аренды список
с фильтрами, сортировкой и пагинацией), `urls.py` – маршруты приложения,
`admin.py` – регистрация модели, `migrations/` – миграции.

### `users/`

Приложение для пользователей реестра: `models.py` – модель `User` (имя, уникальный
email), `admin.py`, `migrations/`. Это не встроенная модель аутентификации Django.

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
`Rental`, база данных (`test_database.py`: таблицы, внешние ключи, перенос данных, файл
запросов), модели Django (`test_models.py`: связи, ограничения, `PROTECT`, CRUD, методы),
перенос данных (`test_import.py`), ПР10 (`test_pr10.py`: статусы аренд, slug, вычисляемое
поле, контекстный процессор, админ-панель) и веб-страницы (`test_views.py`: шаблоны, данные из ORM,
поиск, фильтры, сортировка, пагинация, статистика, 404). `conftest.py` создаёт временную
исходную базу SQLite, а pytest-django отдельную тестовую базу Django; рабочие
`data/domainreg.sqlite` и `db.sqlite3` не изменяются.

## Запуск приложения

Установка зависимостей:
```text
pip install -r requirements.txt
```

Веб-версия (Django), порядок после клонирования репозитория:
```text
python manage.py migrate
python db/import_sqlite_to_orm.py
python manage.py createsuperuser
python manage.py runserver
```
`createsuperuser` нужен для входа в админ-панель `/admin/`. `migrate` создаёт таблицы в `db.sqlite3`, `import_sqlite_to_orm.py` переносит в них
данные из исходной базы `data/domainreg.sqlite`. Если исходную базу нужно пересоздать
из JSON (например, после правки файлов в `data/`), сначала выполняется
`python -m db.import_json`.

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
python manage.py check
python manage.py makemigrations --check
pytest -v
```
Тесты используют отдельные базы (временная исходная SQLite и тестовая база
pytest-django), рабочие базы не изменяются.

## Проверка качества кода

Соответствие PEP 8 проверяется `flake8`, форматирование выполняет `black`:
```text
flake8 .
black .
```
Каталоги `migrations` исключены из проверки `flake8` (`setup.cfg`).

## Зависимости

Состав зависимостей в `requirements.txt`:
* `Django==5.2.*` – веб-фреймворк;
* `django-debug-toolbar` – панель отладки SQL-запросов (ПР10);
* `Unidecode` – транслитерация для slug (ПР10, нужна и для миграций);
* `pytest` и `pytest-django` – автоматизированные тесты;
* `flake8` – проверка качества кода;
* `black` – форматирование кода.

## Git

Исходный код проекта хранится в Git-репозитории. Коммиты начинаются с
метки текущей работы: `PR5:`, `PR6:`, `PR7:`, `PR9:`, `PR10:`. Проверка состояния репозитория:
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

Реализовано (ПР7):
* спроектирована реляционная структура базы: 5 таблиц, первичные и внешние ключи;
* таблицы создаются SQL-скриптом `sql/schema.sql`;
* данные перенесены из JSON в SQLite скриптом `db/import_json.py`;
* 18 SQL-запросов предметной области в `sql/queries.sql`;
* все страницы веб-интерфейса получают данные из SQLite (`sqlite3.Row`,
  параметры `?`);
* новые страницы: свободные для аренды домены на дату, истекающие домены,
  статистика реестра.

Реализовано (ПР9):
* модели `User`, `Organization`, `Domain`, `Resource`, `Rental` с внешними ключами
  (`on_delete`, `related_name`), приложение `users`;
* миграции для всех моделей, база Django `db.sqlite3`;
* скрипты осмотра исходной базы и переноса данных с сохранением идентификаторов;
* все страницы работают через ORM, SQL-запросы из представлений удалены;
* поиск и сортировка доменов, фильтрация, сортировка и пагинация аренд;
* статистика через `aggregate()` и `annotate()`;
* регистронезависимый поиск по кириллице (lookup `uicontains`);
* тесты моделей, переноса данных и страниц (pytest-django).

Реализовано (ПР10):
* административная панель для всех моделей: столбцы, поиск, фильтры, сортировка,
  встроенные формы, массовые действия, русские названия;
* статус аренды через `TextChoices` с миграцией данных, методы `QuerySet` по статусу и дате;
* `slug`, `get_absolute_url()` и `GeneratedField` у домена;
* контекстный процессор, Django Debug Toolbar, проверка числа SQL-запросов;
* статистика аренд по статусам, фильтр списка аренд по статусу;
* тесты ПР10 (`tests/test_pr10.py`).

Планируется:
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
