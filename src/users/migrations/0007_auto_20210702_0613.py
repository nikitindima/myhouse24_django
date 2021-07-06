# Generated by Django 3.2.4 on 2021-07-02 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_auto_20210702_0613"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="telegram",
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(max_length=150),
        ),
    ]
