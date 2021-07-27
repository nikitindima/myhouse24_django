import random

from django.core.management import BaseCommand
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from faker import Faker

from src.users.models import UserRole, User
from src.users.services.user_roles_services import get_or_create_user_roles


class Command(BaseCommand):
    def handle(self, *args, **options):
        get_or_create_user_roles()
        fake = Faker()
        user = User(
            first_name='Роман',
            last_name='Чебан',
            patronymic='Виорелович',
            email='roman.cheban@ukr.net',
            status='ACTIVE',
            user_id=str(random.randint(10000, 99999)),
            role=get_object_or_404(UserRole, name='Директор'),
            is_active=True,
            is_superuser=True,
            is_staff=True,
        ).save()

        User.objects.last().set_password('admin')

        for _ in range(5):
            try:
                user = User(
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    patronymic=fake.last_name(),
                    email=fake.email(),
                    status='ACTIVE',
                    user_id=str(random.randint(10000, 99999)),
                    role=get_object_or_404(UserRole, name='Управляющий'),
                    is_active=True,
                    is_superuser=False,
                    is_staff=True,
                ).save()

                User.objects.last().set_password('admin')

            except IntegrityError:
                pass
