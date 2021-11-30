import datetime
import uuid
import os

from django.db import models
from django.contrib.auth.models import User
from django_rehive_extras.models import DateModel
from service_stellar_signer.enums import TransactionStatus, KeypairType
from enumfields import EnumField
from .utils import encrypt_symmetric, decrypt_symmetric
import stellar_sdk
from service_stellar_signer.crypto_interface import WalletAPI


class APIUser(DateModel):
    """
    Signers internal API User used for auth
    """
    identifier = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )


class Configuration(DateModel):
    user = models.ForeignKey(
        'service_stellar_signer.APIUser',
        null=True,
        on_delete=models.SET_NULL,
        related_name='config'
    )
    backup_public_key = models.CharField(max_length=250, unique=True, db_index=True, null=True, blank=True)
    active = models.BooleanField(default=True, blank=False, null=False)
    block_transactions = models.BooleanField(default=False, blank=False, null=False)


class Transaction(DateModel):
    hash = models.CharField(max_length=64, db_index=True)
    transaction_object = models.TextField()
    signed_transaction_object = models.TextField()
    rehive_transaction_id = models.UUIDField(db_index=True)
    status = EnumField(
        TransactionStatus,
        max_length=24,
        default=TransactionStatus.UNSIGNED,
        db_index=True
    )
    user = models.ForeignKey(
        'service_stellar_signer.APIUser',
        null=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return str(self.hash)

    def sign(self):
        wallet = WalletAPI(private_key=self.user.wallet.get().keypair.private_key)
        self.signed_transaction_object = wallet.sign_raw(self.transaction_object)
        self.status = TransactionStatus.SIGNED
        self.save()


class Wallet(DateModel):
    user = models.ForeignKey(
        'service_stellar_signer.APIUser',
        null=True,
        on_delete=models.SET_NULL,
        related_name='wallet',
    )
    setup = models.BooleanField(default=False, blank=False, null=False)
    block_transactions = models.BooleanField(default=False, blank=False, null=False)
    external_public_key = models.CharField(max_length=250, unique=True, db_index=True, null=True, blank=True)
    backup_public_key = models.CharField(max_length=250, unique=True, db_index=True, null=True, blank=True)
    keypair = models.ForeignKey(
        'service_stellar_signer.Keypair',
        null=True,
        on_delete=models.SET_NULL
    )

    def setup_multisig(self):
        if not self.setup:
            wallet = WalletAPI(private_key=self.keypair.private_key)
            wallet.setup_two_of_three_multisig(
                signer_1=self.external_public_key,
                signer_2=self.backup_public_key
            )
            self.setup = True
            self.save()
        else:
            raise Exception('Wallet has been marked as setup')


class Keypair(DateModel):
    encrypted_private_key = models.CharField(max_length=250, null=True)
    public_key = models.CharField(max_length=250, db_index=True, null=True)
    kms_project = models.CharField(max_length=250, db_index=True, null=True)
    kms_region = models.CharField(max_length=250, db_index=True, null=True)
    kms_keyring = models.CharField(max_length=250, db_index=True, null=True)
    kms_key = models.CharField(max_length=250, db_index=True, null=True)
    user = models.ForeignKey(
        'service_stellar_signer.APIUser',
        null=True,
        on_delete=models.SET_NULL,
        related_name='keypair',
    )

    type = EnumField(
        KeypairType,
        max_length=24,
        default=KeypairType.ENCRYPTED_KEY,
        db_index=True
    )

    def set_encrypted_private_key(self, private_key):
        self.encrypted_private_key =  encrypt_symmetric(self.kms_project, 
                                                        self.kms_region,
                                                        self.kms_keyring,
                                                        self.kms_key,
                                                        private_key).decode()
        self.save()


    @property
    def private_key(self):
        return decrypt_symmetric(self.kms_project, 
                                 self.kms_region,
                                 self.kms_keyring,
                                 self.kms_key,
                                 self.encrypted_private_key.encode()).decode()

     
    


