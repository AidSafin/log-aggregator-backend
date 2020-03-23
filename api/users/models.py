from django.contrib.auth.models import AbstractUser
from django.db import models

from users.utils import generate_token


class SiteUser(AbstractUser):
    email = models.EmailField('Email адрес', unique=True)
    username = models.CharField('Username', max_length=150, null=True, blank=True, default=None)
    patronymic = models.CharField('Отчество', max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # createsuperuser command will require these fields

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.get_full_name()


class UserToken(models.Model):
    user = models.OneToOneField(
        'SiteUser',
        related_name='token',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    key = models.CharField('Ключ', max_length=40, default=generate_token)
    created = models.DateTimeField('Дата создания', auto_now_add=True)
    updated = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        db_table = 'users_user_token'
        verbose_name = 'Токен'
        verbose_name_plural = 'Токены'

    def refresh_token(self):
        self.key = generate_token()
        self.save(update_fields=('key',))

    def __str__(self):
        return '{owner} {key}'.format(owner=self.user.get_full_name(), key=self.key)
