import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models import User  # noqa: E402
from models.users import add_user, find_user  # noqa: E402


def test_user_creation():
    user = User(1, "Иванов И.И.", "ivanov@example.com")
    assert user.id == 1
    assert user.name == "Иванов И.И."
    assert user.email == "ivanov@example.com"


def test_user_str_contains_email():
    user = User(1, "Иванов И.И.", "ivanov@example.com")
    assert "ivanov@example.com" in str(user)


def test_user_from_data():
    data = {"id": 5, "name": "Петров П.П.", "email": "petrov@example.com"}
    user = User.from_data(data)
    assert user.id == 5
    assert user.name == "Петров П.П."
    assert user.email == "petrov@example.com"


def test_add_user():
    users = []
    add_user(users, "Сидорова А.А.", "sidorova@example.com")
    assert len(users) == 1
    assert users[0].name == "Сидорова А.А."


def test_find_user():
    users = []
    add_user(users, "Сидорова А.А.", "sidorova@example.com")
    assert find_user(users, "сидорова")
    assert find_user(users, "example.com")
