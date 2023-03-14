from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from service_stellar_signer.status_checker import StatusChecker


class Command(BaseCommand):
    help = 'Runs the status checker diagnostic tool'

    def handle(self, *args, **options):
        sc = StatusChecker()
        print(sc.return_full_diagnostic_dict())
