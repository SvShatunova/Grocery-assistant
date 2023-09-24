from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Абстрактная модель пользователя."""
    email = models.EmailField(
        'email address',
        max_length=100,
        unique=True,
    )
    username = models.CharField(
        max_length=50
    )
    first_name = models.CharField(
        'Имя',
        max_length=40
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=40
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Модель подписки."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribe',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор'
    )
    created = models.DateField(
        auto_now_add=True,
        verbose_name='Дата подписки'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        models.UniqueConstraint(fields=['user', 'author'],
                                name='unique_ff')

    def __str__(self):
        return f'Пользователь {self.user} подписался на автора {self.author}'
