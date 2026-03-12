"""
models.py — расширение профиля пользователя

Django имеет встроенную модель User (auth.User).
Мы добавляем к ней дополнительные поля через OneToOneField.
"""
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Профиль пользователя — расширяет стандартную модель User.
    Связь OneToOne: один User = один UserProfile.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Пользователь"
    )
    avatar = models.URLField(
    blank=True,
    null=True,
    verbose_name="Ссылка на аватар"
    )
    bio = models.TextField(
        blank=True,
        verbose_name="О себе"
    )
    website = models.URLField(
        blank=True,
        verbose_name="Сайт"
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"Профиль: {self.user.username}"
