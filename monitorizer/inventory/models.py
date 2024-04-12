import json
import re

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from monitorizer.server.models import BaseModel, TimedModel
from monitorizer.utils.engine import tmp_file


class SeedDomain(BaseModel):
    value = models.CharField(max_length=255, unique=True, db_index=True)
    enabled = models.BooleanField(
        default=True,
        help_text="If set to false."
        " disables all enumeration operations related to this seed"
        " including scans and submitters.",
    )

    def __str__(self):
        return self.value


class DiscoveredDomain(BaseModel):
    value = models.CharField(max_length=255, unique=True, db_index=True)
    seeds = models.ManyToManyField(SeedDomain, blank=False, related_name="discovered")

    def __str__(self):
        return self.value


class CommandTemplate(BaseModel):
    name = models.CharField(null=False, blank=False)
    cmd = models.CharField(null=False, blank=False)
    parser = models.TextField()

    def __str__(self):
        return self.name


class ScanAutoSubmitter(BaseModel):
    enabled = models.BooleanField(default=True)
    interval = models.ForeignKey(IntervalSchedule, on_delete=models.CASCADE)
    commands = models.ManyToManyField(CommandTemplate, blank=False)
    domain = models.ForeignKey(SeedDomain, on_delete=models.CASCADE)

    @staticmethod
    @receiver(post_delete, sender="inventory.ScanAutoSubmitter")
    def on_delete(sender, instance, using, **kwargs):
        PeriodicTask.objects.filter(name=f"descriptor_{instance.pk}_schedule").delete()

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        PeriodicTask.objects.update_or_create(
            name=f"descriptor_{self.pk}_schedule",
            task="monitorizer.inventory.tasks.execute_scan_descriptor",
            defaults={
                "kwargs": json.dumps({"descriptor_pk": str(self.pk)}),
                "interval": self.interval,
                "enabled": self.enabled,
            },
        )
        return result


class DomainScan(BaseModel):
    class ScanStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        ERROR = "error", "Error"

    descriptor = models.ForeignKey(
        ScanAutoSubmitter, on_delete=models.CASCADE, null=True, blank=True
    )

    domain = models.ForeignKey(SeedDomain, on_delete=models.CASCADE, blank=True)
    status = models.CharField(
        choices=ScanStatus.choices,
        max_length=32,
        default=ScanStatus.PENDING,
        db_index=True,
    )
    command_tpl = models.ForeignKey(CommandTemplate, on_delete=models.CASCADE)
    command_tpl_vars = models.JSONField(null=True, blank=True)
    exit_code = models.PositiveIntegerField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    built_in_template_vars = {"domain", "domain:file", "output", "output:file"}

    @property
    def command(self):
        command = self.command_tpl.cmd
        for var, value in (self.command_tpl_vars or {}).items():
            command = command.replace("{%s}" % var, value)
        return command

    def save(self, *args, **kwargs):
        maybe_vars = re.findall(r"{(.*?)}", self.command_tpl.cmd)
        self.command_tpl_vars = self.command_tpl_vars or {}
        if self.descriptor:
            self.domain = self.descriptor.domain

        for var in maybe_vars:
            if (
                var not in self.built_in_template_vars
                and var not in self.command_tpl_vars
            ):
                continue
            if var == "domain":
                self.command_tpl_vars[var] = self.domain.value
            if var == "domain:file":
                path = tmp_file()
                open(path, "w").write(self.domain.value)
                self.command_tpl_vars[var] = path
            if var == "output:file":
                self.command_tpl_vars[var] = tmp_file()

        return super().save(*args, **kwargs)
