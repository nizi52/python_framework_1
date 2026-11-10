"""Модель пользователя предметной области: владелец доменов и арендатор.

Это не встроенная модель аутентификации Django (django.contrib.auth.User):
она описывает человека из реестра доменов и не используется для входа в систему.
"""

from django.db import models


class User(models.Model):
    name = models.CharField(max_length=200, verbose_name="Имя")
    email = models.EmailField(unique=True, verbose_name="Электронная почта")

    class Meta:
        ordering = ["name"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.name
