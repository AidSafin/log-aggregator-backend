from django.urls import include, path

from rest_framework.routers import DefaultRouter
from users import views

router = DefaultRouter(trailing_slash=True)

router.register('users', views.UsersViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]
