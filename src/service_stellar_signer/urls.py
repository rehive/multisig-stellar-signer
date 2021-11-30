from django.urls import include, path, re_path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = (
    # Admin
    re_path(r'^admin/transactions/$', views.AdminTransactionView.as_view(), name='admin-transactions'),
    re_path(r'^admin/wallet/$', views.AdminWalletView.as_view(), name='admin-wallet')
)

urlpatterns = format_suffix_patterns(urlpatterns)