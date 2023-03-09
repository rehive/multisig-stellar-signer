from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User

from service_stellar_signer.models import APIUser, Keypair
from stellar_sdk.keypair import Keypair as StellarKeypair


class Command(BaseCommand):
    help = 'Create a keypair based on a known secret and public address'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('user_id', type=str)
        parser.add_argument('kms_project', type=str)
        parser.add_argument('kms_region', type=str)
        parser.add_argument('kms_keyring', type=str)
        parser.add_argument('kms_key', type=str)
        parser.add_argument('secret_key', type=str)
        parser.add_argument('public_key', type=str)

    def handle(self, *args, **options):
        user = APIUser.objects.get(
            identifier=options['user_id']
        )
        try:
            keypair = Keypair.objects.get(
                user=user
            )
            print('Keypair already exists')
        except Keypair.DoesNotExist:
            keypair = Keypair.objects.create(
                public_key=options['public_key'],
                kms_project=options['kms_project'],
                kms_region=options['kms_region'],
                kms_keyring=options['kms_keyring'],
                kms_key=options['kms_key'],
                user=user,
            )
            keypair.set_encrypted_private_key(options['secret_key'])
            print('A keypair entry has been created and encrypted using the private key provided.')
