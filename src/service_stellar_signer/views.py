from collections import OrderedDict
from logging import getLogger

from rest_framework import status, filters, exceptions
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authentication import TokenAuthentication
from drf_rehive_extras.generics import *

from service_stellar_signer.serializers import (
    AdminTransactionSerializer, AdminWalletSerializer
)
from service_stellar_signer.models import Wallet, APIUser


logger = getLogger('django')


"""
Admin Endpoints
"""

class AdminTransactionView(CreateAPIView):
    allowed_methods = ('POST',)
    serializer_class = AdminTransactionSerializer
    # authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,) 


class AdminWalletView(CreateAPIView, RetrieveAPIView):
    allowed_methods = ('POST', 'GET',)
    serializer_class = AdminWalletSerializer
    # authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,) 

    def get_object(self):
        api_user = APIUser.objects.get(
            user=self.request.user
        )
        try:
            wallet = Wallet.objects.get(
                user=api_user
            )
        except Wallet.DoesNotExist:
            raise exceptions.NotFound()

        return wallet