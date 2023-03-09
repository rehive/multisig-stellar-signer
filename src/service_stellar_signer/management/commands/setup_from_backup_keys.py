from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User

from service_stellar_signer.models import APIUser


class Command(BaseCommand):
    help = 'Sets the services backup key'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('user_id', type=str)
        parser.add_argument('previous_signer_public_key', type=str)


    def handle(self, *args, **options):
        # Create the wallet
        user = APIUser.objects.get(
            identifier=options['user_id']
        )

        backup_public_key = user.config.get().backup_public_key
        if not backup_public_key:
            print('Please setup the backup key before running the full setup.')
            return

        try:
            keypair = Keypair.objects.get(
                user=user
            )
        except Keypair.DoesNotExist as exc:
            print('Please run the setup_keypair command before running the full setup.')
            return
        
        wallet = Wallet.objects.create(
            keypair=keypair,
            user=user,
            backup_public_key=backup_public_key,
            external_public_address=options['previous_signer_public_key'],
            setup=True
        )
        print('Signer initiated using the previous public address.')
