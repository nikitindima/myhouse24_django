# Generated by Django 3.2.4 on 2021-07-06 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_alter_user_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_id',
            field=models.CharField(default=1, max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='status',
            field=models.CharField(choices=[('ACTIVE', 'Активный'), ('INACTIVE', 'Неактивный'), ('DEACTIVATED', 'Деактивированный')], max_length=11),
        ),
    ]