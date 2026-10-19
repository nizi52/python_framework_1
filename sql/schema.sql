-- ==========================================
-- Система учета доменных имен: структура базы данных (ПР7)
-- ==========================================

PRAGMA foreign_keys = ON;

-- Пользователи: владельцы доменов и арендаторы
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

-- Организации, за которыми закрепляются домены
CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

-- Домены: связь с организацией и владельцем
CREATE TABLE IF NOT EXISTS domains (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    organization_id INTEGER NOT NULL,
    owner_id INTEGER NOT NULL,
    registration_end TEXT NOT NULL,          -- дата в формате YYYY-MM-DD
    is_removed INTEGER NOT NULL DEFAULT 0,   -- 0 – в реестре, 1 – исключён
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

-- Ресурсы домена: хостинг, SSL, почта, DNS
CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,
    domain_id INTEGER NOT NULL,
    FOREIGN KEY (domain_id) REFERENCES domains(id)
);

-- Аренда домена пользователем на период
CREATE TABLE IF NOT EXISTS rentals (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    domain_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,                -- YYYY-MM-DD
    end_date TEXT NOT NULL,                  -- YYYY-MM-DD
    is_cancelled INTEGER NOT NULL DEFAULT 0, -- 0 – действует, 1 – отменена
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (domain_id) REFERENCES domains(id),
    CHECK (start_date <= end_date)
);
