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
        parser.add_argument('backup_key', type=str)

    def handle(self, *args, **options):
        user = APIUser.objects.get(
            identifier=options['user_id']
        )
        config = user.config.get()
        config.backup_public_key = options['backup_key']
        config.save()
        print('Set backup key!')
