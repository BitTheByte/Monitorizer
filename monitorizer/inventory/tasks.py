import subprocess

from celery.signals import worker_ready
from django.db import transaction
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from monitorizer.inventory import models
from monitorizer.server import celery_app


@worker_ready.connect
def at_start(sender, **k):
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=10, period=IntervalSchedule.SECONDS
    )
    for task in [pick_and_start_scan]:
        PeriodicTask.objects.get_or_create(
            name=task.name,
            task=task.name,
            interval=schedule,
        )


@celery_app.task
def execute_scan_descriptor(descriptor_pk):
    descriptor = models.ScanAutoSubmitter.objects.get(pk=descriptor_pk)
    if not descriptor.domain.enabled:
        return

    if (
        models.DomainScan.objects.filter(
            status=models.DomainScan.ScanStatus.PENDING
        ).count()
        > 1500
    ):
        return

    for command in descriptor.commands.all():
        models.DomainScan.objects.create(
            descriptor=descriptor,
            command_tpl=command,
        )


@celery_app.task
def pick_and_start_scan():
    with transaction.atomic():
        scan: models.DomainScan = (
            models.DomainScan.objects.select_for_update(skip_locked=True)
            .filter(status=models.DomainScan.ScanStatus.PENDING, domain__enabled=True)
            .order_by("?")
            .first()
        )
        if not scan:
            return
        scan.status = models.DomainScan.ScanStatus.RUNNING
        scan.save()

    command = subprocess.run(
        scan.command, shell=True, capture_output=True, encoding="utf8"
    )

    if command.returncode == 0:
        scan.status = models.DomainScan.ScanStatus.SUCCESS
        _globals = {"__scan__": {"vars": scan.command_tpl_vars}, "__result__": {}}
        exec(scan.command_tpl.parser, _globals)
        for v in _globals.get("__result__", []):
            domain, _ = models.DiscoveredDomain.objects.get_or_create(value=v.strip())
            domain.seeds.add(scan.domain)
    else:
        scan.status = models.DomainScan.ScanStatus.ERROR
        scan.error = command.stderr

    scan.exit_code = command.returncode
    scan.finished_at = timezone.now()
    scan.save()
