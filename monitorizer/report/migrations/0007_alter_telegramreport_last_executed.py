# Generated by Django 5.0.4 on 2024-04-10 20:14

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("report", "0006_telegramreport_last_executed"),
    ]

    operations = [
        migrations.AlterField(
            model_name="telegramreport",
            name="last_executed",
            field=models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0)),
        ),
    ]