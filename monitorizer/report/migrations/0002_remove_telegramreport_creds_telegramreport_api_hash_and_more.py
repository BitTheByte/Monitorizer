# Generated by Django 5.0.4 on 2024-04-10 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("report", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="telegramreport",
            name="creds",
        ),
        migrations.AddField(
            model_name="telegramreport",
            name="api_hash",
            field=models.CharField(default="1", max_length=1024),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="telegramreport",
            name="api_id",
            field=models.PositiveIntegerField(default=22),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="telegramreport",
            name="filter",
            field=models.CharField(default="22"),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name="Report",
        ),
        migrations.DeleteModel(
            name="TelegramCredentials",
        ),
    ]