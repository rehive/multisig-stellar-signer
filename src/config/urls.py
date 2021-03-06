from django.urls import include, path, re_path
from django.contrib import admin
from django.conf import settings

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework import permissions

from . import views


admin.autodiscover()

schema_view = get_schema_view(
   openapi.Info(
      title="Stellar Signer Service API",
      default_version='v1',
      description="Start by clicking Authorize and adding the header: "
       "Token <your-api-key>."
   ),
   #validators=['flex', 'ssv'],
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=None),
        name='schema-json'
    ),
    re_path(
        r'^swagger/$',
        schema_view.with_ui('swagger', cache_timeout=None),
        name='schema-swagger-ui'
    ),
    re_path(
        r'^$',
        schema_view.with_ui('redoc', cache_timeout=None),
        name='schema-redoc'
    ),

    # Views
    re_path(
        r'^api/',
        include(
            ('service_stellar_signer.urls',
            'service_stellar_signer'),
            namespace='service_stellar_signer'
        )
    ),
]
