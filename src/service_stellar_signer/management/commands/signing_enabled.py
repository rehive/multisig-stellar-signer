from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User

from service_stellar_signer.models import APIUser, Keypair
from stellar_sdk.keypair import Keypair as StellarKeypair


class Command(BaseCommand):
    help = 'Command used to disable or enable signing functionality for wallets associated to your user'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('user_id', type=str)
        parser.add_argument('enabled', type=str)

    def handle(self, *args, **options):
        user = APIUser.objects.get(
            identifier=options['user_id']
        )
        config = user.config.get()
        if options['enabled'] == 'false':
            block_transactions = True
        elif options['enabled'] == 'true':
            block_transactions = False
        else:
            print('The enabled flag should either be true or false.')
        config.block_transactions = block_transactions
        config.save()
        
        if block_transactions:
            print('Signing has been disabled for this users wallet')
        elif not block_transactions:
            print('Signing has been enabled for this users wallet')