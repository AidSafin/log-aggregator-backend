import http

from django.contrib.auth import authenticate, get_user_model

from core.pagination import DefaultPagination
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from users.authentication import UserTokenAuthentication
from users.models import UserToken
from users.permissions import UsersPermissions
from users.serializers import (
    CreateUserSerializer,
    LoginSerializer,
    TokenSerializer,
    UserSerializer,
)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects
    serializer_class = UserSerializer

    permission_classes = (UsersPermissions,)
    authentication_classes = (UserTokenAuthentication,)

    filter_backends = (filters.DjangoFilterBackend, OrderingFilter, SearchFilter)
    pagination_class = DefaultPagination
    search_fields = ('=id', 'email', 'first_name', 'last_name', 'patronymic')
    ordering_fields = ('id', 'email', 'first_name', 'last_name', 'patronymic', 'date_joined')
    ordering = ('id',)

    @swagger_auto_schema(
        request_body=CreateUserSerializer,
        responses={
            '201': UserSerializer,
            '400': 'Validation error',
        },
    )
    def create(self, request, *args, **kwargs):
        """Создание пользователя.

        Только для администраторов.
        """
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=http.HTTPStatus.CREATED)

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            '200': TokenSerializer,
            '400': 'Validation error',
            '401': 'Authentication failed',
        })
    @action(
        methods=['post'],
        detail=False,
        url_path='login',
        url_name='login',
        serializer_class=LoginSerializer,
    )
    def login(self, request, *args, **kwargs):
        """Авторизация.

        Полученный токен добавить в заголовок:
        HTTP_AUTHORIZATION: Token <TOKEN>

        Raises:
            AuthenticationFailed: email or password invalid
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(email=serializer.data['email'], password=serializer.data['password'])

        if not user:
            raise AuthenticationFailed()

        user_token, created = UserToken.objects.get_or_create(user=user)
        if not created:
            user_token.refresh_token()

        serializer = TokenSerializer(data={
            'token': user_token.key,
            'user_id': user_token.user.pk,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
