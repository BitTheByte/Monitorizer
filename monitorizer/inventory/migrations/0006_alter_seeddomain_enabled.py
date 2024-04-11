# Generated by Django 5.0.4 on 2024-04-10 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0005_alter_seeddomain_enabled"),
    ]

    operations = [
        migrations.AlterField(
            model_name="seeddomain",
            name="enabled",
            field=models.BooleanField(
                default=True,
                help_text="If set to false. disables all enumeration operations related to this seed including scans and submitters.",
            ),
        ),
    ]