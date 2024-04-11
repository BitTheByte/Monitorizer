# Generated by Django 5.0.4 on 2024-04-10 21:18

import datetime

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_celery_beat", "0018_improve_crontab_helptext"),
        ("report", "0010_alter_telegramreport_filter_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="WebHookReport",
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
                ("enabled", models.BooleanField(default=True)),
                (
                    "filter_type",
                    models.CharField(
                        choices=[
                            ("value__startswith", "Starts with"),
                            ("value__endswith", "Ends with"),
                            ("value__contains", "Contains"),
                        ],
                        max_length=32,
                    ),
                ),
                ("filter_value", models.CharField()),
                (
                    "last_executed",
                    models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0)),
                ),
                ("url", models.URLField()),
                (
                    "interval",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="django_celery_beat.intervalschedule",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]