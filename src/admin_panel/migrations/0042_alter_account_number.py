# Generated by Django 3.2.4 on 2021-07-14 03:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0041_alter_account_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='number',
            field=models.CharField(max_length=40, unique=True),
        ),
    ]