# Generated by Django 3.2.4 on 2021-07-17 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0052_auto_20210717_1304'),
    ]

    operations = [
        migrations.AddField(
            model_name='receipt',
            name='number',
            field=models.CharField(default=0, max_length=40, unique=True),
            preserve_default=False,
        ),
    ]