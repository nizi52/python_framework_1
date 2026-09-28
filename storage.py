"""Загрузка и сохранение реестра доменов в JSON-файле."""

import json
from datetime import date


def load_domains(filename: str) -> dict[int, dict]:
    """Загрузить домены из JSON-файла.

    Если файл отсутствует или повреждён, возвращается пустой реестр —
    программа не должна аварийно завершаться из-за проблем с файлом.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            raw_domains = json.load(file)
    except FileNotFoundError:
        print(f"Файл {filename} не найден, будет создан новый реестр.")
        return {}
    except json.JSONDecodeError:
        print(f"Файл {filename} повреждён, будет создан новый реестр.")
        return {}

    domains: dict[int, dict] = {}
    for item in raw_domains:
        item["registration_end"] = date.fromisoformat(item["registration_end"])
        domains[item["id"]] = item
    return domains


def save_domains(filename: str, domains: dict[int, dict]) -> None:
    """Сохранить домены в JSON-файл."""
    raw_domains = []
    for item in domains.values():
        raw_item = dict(item)
        raw_item["registration_end"] = raw_item["registration_end"].isoformat()
        raw_domains.append(raw_item)

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(raw_domains, file, ensure_ascii=False, indent=2)
