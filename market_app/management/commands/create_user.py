from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create a new user'

    def add_arguments(self, parser):
        parser.add_argument('--admin', action='store_true', help='Create a superuser')
        parser.add_argument('username', type=str, help='The username of the user to create')
        parser.add_argument('password', type=str, help='The password of the user to create')
        parser.add_argument('email', type=str, help='The email of the user to create')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        password = kwargs['password']
        email = kwargs['email']
        user = User.objects.create_user(username=username, email=email, password=password)
        if kwargs['admin']:
            user.is_superuser = True
            user.is_staff = True
            user.save()
        print("New User Created: ", user.username)