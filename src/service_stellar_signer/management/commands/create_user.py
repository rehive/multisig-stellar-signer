from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from service_stellar_signer.models import APIUser, Configuration


class Command(BaseCommand):
    help = 'Generate a new user and returns their token'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('username', type=str)
        parser.add_argument('email', type=str)
        parser.add_argument('password', type=str)

    def handle(self, *args, **options):
        user = User.objects.create_user(
            email=options['email'],
            password=options['password'],
            username=options['username']
        )
        api_user = APIUser.objects.create(
            user=user
        )
        config = Configuration.objects.create(
            user=api_user
        )
        print('API Token: ' + str(Token.objects.create(user=user).key))
        print('User ID: ' + str(api_user.identifier))
