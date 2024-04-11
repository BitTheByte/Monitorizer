import json
from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from monitorizer.server.models import BaseModel


class Report(BaseModel):
    class FilterTypes(models.TextChoices):
        STARTS_WITH = "value__startswith", "Starts with"
        ENDS_WITH = "value__endswith", "Ends with"
        CONTAINS = "value__contains", "Contains"

    enabled = models.BooleanField(default=True)
    interval = models.ForeignKey(IntervalSchedule, on_delete=models.SET_NULL, null=True)
    filter_type = models.CharField(choices=FilterTypes.choices, max_length=32)
    filter_value = models.CharField()
    last_executed = models.DateTimeField(default=datetime(1970, 1, 1))

    class Meta:
        abstract = True

    @property
    def task_name(self):
        return f"report_{self.__class__.__name__}_{self.pk}_schedule"

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        PeriodicTask.objects.update_or_create(
            name=self.task_name,
            task="monitorizer.report.tasks.send_report_result",
            defaults={
                "kwargs": json.dumps(
                    {
                        "report_channel_type": self.__class__.__name__,
                        "channel_pk": str(self.pk),
                    }
                ),
                "interval": self.interval,
                "enabled": self.enabled,
            },
        )
        return result


class TelegramReport(Report):
    api_id = models.BigIntegerField()
    api_hash = models.CharField(max_length=1024)
    chat_id = models.BigIntegerField()


class WebHookReport(Report):
    url = models.URLField()
    message_param = models.CharField(default="content")
    file_param = models.CharField(default="file")


@receiver(post_delete, sender=TelegramReport)
@receiver(post_delete, sender=WebHookReport)
def on_delete(sender, instance, **kwargs):
    PeriodicTask.objects.filter(name=instance.task_name).delete()
