# Generated by Django 3.2.4 on 2021-07-12 13:24

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0036_message_to_all'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='floor',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]