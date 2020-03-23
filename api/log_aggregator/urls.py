from django.urls import include, path

from log_aggregator import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=True)

router.register('logs/apache', views.ApacheLogViewSet, basename='apache_logs')

urlpatterns = [
    path('', include(router.urls)),
]
