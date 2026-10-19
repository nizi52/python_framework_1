"""Общая подготовка тестов: отдельная временная база SQLite и настройки Django.

Переменная DOMAINREG_DB задаётся до импорта db.database, поэтому тесты
работают с копией данных и не изменяют рабочую базу data/domainreg.sqlite.
"""

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

TEST_DB = Path(tempfile.gettempdir()) / "domainreg_test.sqlite"
os.environ["DOMAINREG_DB"] = str(TEST_DB)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "domainreg.settings")

from db import import_json  # noqa: E402

if TEST_DB.exists():
    TEST_DB.unlink()
import_json.main()
