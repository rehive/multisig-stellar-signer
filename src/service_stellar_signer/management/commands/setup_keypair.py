from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User

from service_stellar_signer.models import APIUser, Keypair
from stellar_sdk.keypair import Keypair as StellarKeypair


class Command(BaseCommand):
    help = 'Create and setup keypair object'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('user_id', type=str)
        parser.add_argument('kms_project', type=str)
        parser.add_argument('kms_region', type=str)
        parser.add_argument('kms_keyring', type=str)
        parser.add_argument('kms_key', type=str)

    def handle(self, *args, **options):
        user = APIUser.objects.get(
            identifier=options['user_id']
        )
        stellar_keypair = StellarKeypair.random()
        try:
            keypair = Keypair.objects.get(
                user=user
            )
            print('Keypair already exists')
        except Keypair.DoesNotExist:
            keypair = Keypair.objects.create(
                public_key=stellar_keypair.public_key,
                kms_project=options['kms_project'],
                kms_region=options['kms_region'],
                kms_keyring=options['kms_keyring'],
                kms_key=options['kms_key'],
                user=user,
            )
            keypair.set_encrypted_private_key(stellar_keypair.secret)
            print('Keypair created and setup. Your hotwallet address is: ' + str(stellar_keypair.public_key) + " Please fund this account with at least 2.5 XLM")
            print('Your encrypted private key is: ' + str(keypair.encrypted_private_key))
            print('Please store the encrypted private key in a secure location as a backup')
