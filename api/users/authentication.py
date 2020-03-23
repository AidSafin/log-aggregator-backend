from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from rest_framework.authentication import TokenAuthentication
from users.models import UserToken


class EmailAuthBackend(ModelBackend):
    """Авторизация по email."""

    user_class = get_user_model()

    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get('email')
        get_kwargs = {}

        if email is not None:
            get_kwargs['email'] = email
        elif username is not None:
            get_kwargs['username'] = username

        try:
            user = self.user_class.objects.get(**get_kwargs)
        except self.user_class.DoesNotExist:
            return None

        if user.check_password(password):
            return user


class UserTokenAuthentication(TokenAuthentication):
    """
    Аутентификация по токену.

    Использует кастомную модель для нужд бизнес-логики.
    """

    model = UserToken
