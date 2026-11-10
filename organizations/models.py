"""Модель организации, за которой закрепляются домены."""

from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")

    class Meta:
        ordering = ["name"]
        verbose_name = "Организация"
        verbose_name_plural = "Организации"

    def __str__(self):
        return self.name
