from django.db import models
from django.db.models import Q, F
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser

from . import constants


class CustomUser(AbstractUser):
    email = models.EmailField(
        unique=True,
        max_length=constants.EMAIL_MAX_LENGTH,
        verbose_name='Электронная почта'
    )
    username = models.CharField(
        unique=True,
        max_length=constants.USERNAME_MAX_LENGTH,
        verbose_name='Логин',
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
        )]
    )
    first_name = models.CharField(
        max_length=constants.FIRST_AND_LAST_NAMES_MAX_LENGTH,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=constants.FIRST_AND_LAST_NAMES_MAX_LENGTH,
        verbose_name='Фамилия'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    subscribe = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscribe'],
                name="unique_user_subscribe"
            ),
            models.CheckConstraint(
                check=~Q(user=F('subscribe')),
                name='prevent_self_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user.username} -> {self.subscribe.username}'
