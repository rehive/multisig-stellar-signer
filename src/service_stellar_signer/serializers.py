import uuid

from rehive import Rehive, APIException
from rest_framework import serializers
from django.db import transaction
from drf_rehive_extras.serializers import BaseModelSerializer
from rest_framework.exceptions import APIException
from django.core.exceptions import ObjectDoesNotExist

from service_stellar_signer.models import Keypair, Transaction, Wallet, APIUser
from service_stellar_signer.status_checker import StatusChecker

from drf_rehive_extras.fields import TimestampField, EnumField
from service_stellar_signer.enums import TransactionStatus


class StatusSerializer(serializers.Serializer):
    diagnostics = serializers.SerializerMethodField()

    def get_diagnostics(self, instance):
        print('running this')
        sc = StatusChecker()
        return sc.return_full_diagnostic_dict()


class AdminWalletSerializer(BaseModelSerializer):
    public_key = serializers.CharField(source='keypair.public_key', read_only=True)

    class Meta:
        model = Wallet
        fields = (
            'id',
            'setup',
            'external_public_key',
            'public_key',
            'backup_public_key',
            'block_transactions',
        )
        read_only = (
            'id',
            'setup',
            'backup_public_key',
            'public_key'
        )

    def create(self, validated_data):
        user = APIUser.objects.get(
            user=self.context['request'].user
        )
        try:
            Wallet.objects.get(
                user=user
            )
            raise serializers.ValidationError(
                'A wallet has already been created.'
            )
        except Wallet.DoesNotExist:
            pass

        backup_public_key = user.config.get().backup_public_key
        if not backup_public_key:
            raise serializers.ValidationError(
                'No backup key setup.'
            )
        
        try:
            keypair = Keypair.objects.get(
                user=user
            )
        except Keypair.DoesNotExist as exc:
            raise serializers.ValidationError(
                'No keypair setup.'
            )

        with transaction.atomic():
            wallet = Wallet.objects.create(
                **validated_data,
                keypair=keypair,
                user=user,
                backup_public_key=backup_public_key
            )
            wallet.setup_multisig()
        return wallet


class AdminTransactionSerializer(BaseModelSerializer):
    signed_transaction_object = serializers.CharField(read_only=True)
    status = EnumField(enum=TransactionStatus, read_only=True)

    class Meta:
        model = Transaction
        fields = (
            'id',
            'hash',
            'transaction_object',
            'signed_transaction_object',
            'rehive_transaction_id',
            'status',
            'user'
        )

    def create(self, validated_data): 
        user = APIUser.objects.get(
            user=self.context['request'].user
        )
        transaction = Transaction(
            **validated_data,
            user=user
        )
        try:
            wallet = Wallet.objects.get(
                user=user,
                setup=True
            )
        except Wallet.DoesNotExist as exc:
            transaction.status = TransactionStatus.REJECTED
            raise APIException(detail="Wallet has not been correctly setup.")
        if user.config.get().block_transactions:
            transaction.status = TransactionStatus.REJECTED
            raise APIException(detail="Signing is disabled.", code=403)         
        else:
            try:
                transaction.sign()
            except Exception as exc:
                raise serializers.ValidationError('Unable to sign transaction. Transaction object may be invalid.')
        return transaction
