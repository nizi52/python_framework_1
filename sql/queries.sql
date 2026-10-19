-- ==========================================
-- Система учета доменных имен: SQL-запросы проекта (ПР7)
-- Проверка в SQLite CLI:  sqlite3 data/domainreg.sqlite  ->  .read sql/queries.sql
-- Значения в WHERE заданы примером, в Django они передаются параметрами ?.
-- ==========================================

.headers on
.mode column

-- 1. [SELECT, ORDER BY] Список всех доменов по алфавиту
SELECT id, name, registration_end
FROM domains
ORDER BY name;

-- 2. [WHERE] Домены, срок регистрации которых ещё не истёк и которые не исключены из реестра
SELECT id, name, registration_end
FROM domains
WHERE is_removed = 0
  AND registration_end >= date('now', 'localtime')
ORDER BY registration_end;

-- 3. [WHERE, BETWEEN] Домены, у которых регистрация заканчивается в ближайшие 90 дней
--    (страница «Истекающие домены», в Django число дней передаётся параметром ?)
SELECT id, name, registration_end,
       CAST(julianday(registration_end) - julianday(date('now', 'localtime')) AS INTEGER)
           AS days_left
FROM domains
WHERE is_removed = 0
  AND registration_end BETWEEN date('now', 'localtime') AND date('now', 'localtime', '+90 days')
ORDER BY registration_end;

-- 4. [WHERE, LIKE] Поиск ресурсов по типу
SELECT id, name, kind
FROM resources
WHERE kind LIKE 'SSL%';

-- 5. [JOIN] Полная информация о доменах: организация и владелец вместо идентификаторов
SELECT domains.name AS domain_name,
       organizations.name AS organization_name,
       users.name AS owner_name,
       domains.registration_end
FROM domains
JOIN organizations ON domains.organization_id = organizations.id
JOIN users ON domains.owner_id = users.id
ORDER BY domains.name;

-- 6. [JOIN, WHERE] Действующие аренды: домен, арендатор и период
SELECT rentals.id,
       domains.name AS domain_name,
       users.name AS user_name,
       rentals.start_date,
       rentals.end_date
FROM rentals
JOIN domains ON rentals.domain_id = domains.id
JOIN users ON rentals.user_id = users.id
WHERE rentals.is_cancelled = 0
  AND date('now', 'localtime') BETWEEN rentals.start_date AND rentals.end_date
ORDER BY rentals.end_date;

-- 7. [JOIN] Ресурсы с названием домена, к которому они привязаны
SELECT resources.name AS resource_name,
       resources.kind,
       domains.name AS domain_name
FROM resources
JOIN domains ON resources.domain_id = domains.id
ORDER BY domains.name, resources.kind;

-- 8. [подзапрос NOT IN] Домены, свободные для аренды на выбранную дату
--    (страница «Свободные домены», в Django дата передаётся параметром ?)
SELECT id, name, registration_end
FROM domains
WHERE is_removed = 0
  AND registration_end >= '2026-11-15'
  AND id NOT IN (
      SELECT domain_id
      FROM rentals
      WHERE is_cancelled = 0
        AND '2026-11-15' BETWEEN start_date AND end_date
  )
ORDER BY name;

-- 9. [агрегатная функция COUNT] Общее количество доменов в реестре
SELECT COUNT(*) AS domains_total
FROM domains;

-- 10. [агрегатные функции MIN, MAX, COUNT] Ближайший и самый поздний срок регистрации
--     среди доменов в реестре
SELECT COUNT(*) AS domains_in_registry,
       MIN(registration_end) AS nearest_end,
       MAX(registration_end) AS latest_end
FROM domains
WHERE is_removed = 0;

-- 11. [агрегатная функция AVG] Средняя длительность аренды в днях (без отменённых)
SELECT ROUND(AVG(julianday(end_date) - julianday(start_date)), 1) AS avg_rental_days
FROM rentals
WHERE is_cancelled = 0;

-- 12. [GROUP BY, LEFT JOIN, COUNT] Количество доменов у каждой организации
--     (организации без доменов тоже попадают в выборку)
SELECT organizations.name AS organization_name,
       COUNT(domains.id) AS domains_count
FROM organizations
LEFT JOIN domains ON domains.organization_id = organizations.id
GROUP BY organizations.id, organizations.name
ORDER BY domains_count DESC;

-- 13. [GROUP BY, LEFT JOIN, COUNT] Количество аренд (без отменённых) по каждому домену
SELECT domains.name AS domain_name,
       COUNT(rentals.id) AS rentals_count
FROM domains
LEFT JOIN rentals ON rentals.domain_id = domains.id
                 AND rentals.is_cancelled = 0
GROUP BY domains.id, domains.name
ORDER BY rentals_count DESC, domains.name;

-- 14. [GROUP BY] Количество ресурсов каждого типа
SELECT kind, COUNT(*) AS resources_count
FROM resources
GROUP BY kind
ORDER BY resources_count DESC, kind;

-- 15. [GROUP BY, HAVING] Домены, к которым привязано больше одного ресурса
SELECT domains.name AS domain_name,
       COUNT(resources.id) AS resources_count
FROM domains
JOIN resources ON resources.domain_id = domains.id
GROUP BY domains.id, domains.name
HAVING COUNT(resources.id) > 1;

-- 16. [GROUP BY, HAVING] Организации, у которых больше одного домена
SELECT organizations.name AS organization_name,
       COUNT(domains.id) AS domains_count
FROM organizations
JOIN domains ON domains.organization_id = organizations.id
GROUP BY organizations.id, organizations.name
HAVING COUNT(domains.id) > 1;

-- 17. [ORDER BY, LIMIT, OFFSET] Три домена с самым ранним окончанием регистрации, начиная со второго
SELECT name, registration_end
FROM domains
ORDER BY registration_end
LIMIT 3 OFFSET 1;

-- 18. [CASE] Статус каждого домена на текущую дату
SELECT name,
       CASE
           WHEN is_removed = 1 THEN 'удалён'
           WHEN registration_end >= date('now', 'localtime') THEN 'активен'
           ELSE 'истёк'
       END AS status
FROM domains
ORDER BY name;
