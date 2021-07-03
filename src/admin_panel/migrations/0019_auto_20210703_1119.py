# Generated by Django 3.2.4 on 2021-07-03 11:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0018_auto_20210703_0455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='floors',
            field=models.PositiveIntegerField(blank=True, default=10, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='section',
            name='name',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
