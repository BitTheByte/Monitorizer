import os
import uuid

from django.utils import timezone

from monitorizer.inventory import models as inventory_models
from monitorizer.report import models
from monitorizer.server import celery_app

MESSAGE_TEMPLATE = """
Monitorizer has discovered new %i domain(s) since %s
Filter Type: %s
Filter Value: %s 
"""


@celery_app.task
def send_report_result(report_channel_type, channel_pk):
    report_path = f"/tmp/{uuid.uuid4()}"
    report = getattr(models, report_channel_type).objects.get(pk=channel_pk)

    if not report or not report.enabled:
        return

    domains = [
        d[0]
        for d in inventory_models.DiscoveredDomain.objects.filter(
            **{report.filter_type: report.filter_value},
            created_at__gte=report.last_executed,
        ).values_list("value")
    ]
    message = MESSAGE_TEMPLATE % (
        len(domains),
        str(report.last_executed),
        report.filter_type.get_display(),
        report.filter_value,
    )

    report.last_executed = timezone.now()
    if not domains:
        report.save()
        return

    open(report_path, "w").write("\n".join(domains))

    if isinstance(report, models.TelegramReport):
        from telebot import TeleBot

        bot = TeleBot(token="%s:%s" % (report.api_id, report.api_hash))
        bot.send_document(
            chat_id=report.chat_id, caption=message, document=open(report_path)
        )

    if isinstance(report, models.WebHookReport):
        import requests

        response = requests.post(
            report.url,
            verify=False,
            timeout=60,
            data={report.message_param: message},
            files={report.file_param: open(report_path)},
        )
        response.raise_for_status()

    if os.path.exists(report_path):
        os.unlink(report_path)
    report.save()
