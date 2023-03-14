from collections import OrderedDict
from logging import getLogger

from rest_framework import status, filters, exceptions
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authentication import TokenAuthentication
from drf_rehive_extras.generics import *

from service_stellar_signer.serializers import (
    AdminTransactionSerializer, AdminWalletSerializer, StatusSerializer
)
from service_stellar_signer.models import Wallet, APIUser


logger = getLogger('django')


"""
Admin Endpoints
"""

class AdminTransactionView(CreateAPIView):
    allowed_methods = ('POST',)
    serializer_class = AdminTransactionSerializer
    permission_classes = (IsAuthenticated,) 


class AdminWalletView(CreateAPIView, RetrieveAPIView):
    allowed_methods = ('POST', 'GET',)
    serializer_class = AdminWalletSerializer
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


class StatusView(GenericAPIView):
    allowed_methods = ('GET',)
    serializer_class = StatusSerializer
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer({})
        return Response({'status': 'success', 'data': serializer.data})
