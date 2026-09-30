"""Класс User и функции для работы с коллекцией пользователей."""

from typing import List, Optional


class User:
    """Пользователь системы — владелец доменов."""

    def __init__(self, user_id: int, name: str, email: str) -> None:
        """Создать объект пользователя."""
        self.id = user_id
        self.name = name
        self.email = email

    def __str__(self) -> str:
        """Вернуть строковое представление пользователя."""
        return f"{self.name} <{self.email}>"

    @classmethod
    def from_data(cls, data: dict) -> "User":
        """Создать пользователя из словаря данных (например, из JSON)."""
        return cls(data["id"], data["name"], data["email"])


def add_user(users: List[User], name: str, email: str) -> User:
    """Создать объект User и добавить его в коллекцию."""
    new_id = max((user.id for user in users), default=0) + 1
    user = User(new_id, name, email)
    users.append(user)
    return user


def find_user(users: List[User], query: str) -> List[User]:
    """Найти пользователей по подстроке в имени или email."""
    query_lower = query.lower()
    return [
        user
        for user in users
        if query_lower in user.name.lower() or query_lower in user.email.lower()
    ]


def find_user_by_id(users: List[User], user_id: int) -> Optional[User]:
    """Найти пользователя по идентификатору."""
    for user in users:
        if user.id == user_id:
            return user
    return None


def show_users(users: List[User]) -> None:
    """Вывести список пользователей."""
    if not users:
        print("Пользователей нет.")
        return
    for user in users:
        print(f"[{user.id}] {user}")
