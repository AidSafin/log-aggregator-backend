from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from core import settings
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

api_v1_urls = [
    path('', include('users.urls')),
    path('', include('log_aggregator.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_v1_urls)),
]

if settings.DEBUG:
    description = """N.B. documentation is auto-generated, so some sections may be wrong.
                      Ask developers if you have any issues."""
    docs_schema_view = get_schema_view(
        openapi.Info(
            title='log_aggregator API',
            default_version='v1',
            description=description,
            terms_of_service='',
            license=openapi.License(name='BSD License'),
        ),
        validators=['flex', 'ssv'],
        public=True,
        permission_classes=(permissions.AllowAny,),
    )
    cache_timeout = settings.SWAGGER_CACHE_TIMEOUT
    docs_urls = [
        path('swagger.json', docs_schema_view.without_ui(cache_timeout=cache_timeout), name='schema-swagger-json'),
        path('swagger/', docs_schema_view.with_ui('swagger', cache_timeout=cache_timeout), name='schema-swagger-ui'),
        path('redoc/', docs_schema_view.with_ui('redoc', cache_timeout=cache_timeout), name='schema-redoc-ui'),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns.append(path('docs/', include(docs_urls)))

if 'silk' in settings.INSTALLED_APPS:
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
