# Generated by Django 3.2.4 on 2021-07-02 11:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("admin_panel", "0014_auto_20210702_0817"),
    ]

    operations = [
        migrations.RenameField(
            model_name="section",
            old_name="section",
            new_name="house",
        ),
    ]
