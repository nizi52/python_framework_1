"""Регистронезависимый поиск подстроки для кириллицы в SQLite.

Встроенный lookup icontains в SQLite различает регистр у не-латинских букв
(LIKE сравнивает без учёта регистра только символы ASCII), поэтому запрос «ромашка»
не находит «Ромашка». Здесь регистрируется SQL-функция UNICODE_LOWER (str.casefold)
и lookup uicontains для текстовых полей: Model.objects.filter(name__uicontains="ромашка").
"""

from django.db.backends.signals import connection_created
from django.db.models import CharField, Lookup


@CharField.register_lookup
class UnicodeIContains(Lookup):
    lookup_name = "uicontains"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        _, rhs_params = self.process_rhs(compiler, connection)
        value = str(rhs_params[0]).casefold()
        value = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        return f"UNICODE_LOWER({lhs}) LIKE %s ESCAPE '\\'", [*lhs_params, f"%{value}%"]


def _unicode_lower(value):
    return value.casefold() if isinstance(value, str) else value


def register_sqlite_functions(sender, connection, **kwargs):
    """Сделать UNICODE_LOWER доступной в каждом новом соединении SQLite."""
    if connection.vendor == "sqlite":
        connection.connection.create_function(
            "UNICODE_LOWER", 1, _unicode_lower, deterministic=True
        )


connection_created.connect(register_sqlite_functions)
