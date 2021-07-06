# Generated by Django 3.2.4 on 2021-06-30 08:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("admin_panel", "0007_auto_20210629_0626"),
    ]

    operations = [
        migrations.CreateModel(
            name="SiteServicePage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "seo_data",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="admin_panel.seodata",
                    ),
                ),
                ("services", models.ManyToManyField(to="admin_panel.Article")),
            ],
        ),
    ]
