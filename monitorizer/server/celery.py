import os

from celery import Celery
from kombu import Queue

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitorizer.server.settings")

app = Celery("asmcore")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
app.conf.task_routes = {
    "monitorizer.inventory.tasks.*": {"queue": "default"},
    "monitorizer.report.tasks.*": {"queue": "reports"},
}
app.conf.task_queues = (
    Queue("default", routing_key="task.#"),
    Queue("reports", routing_key="reports.#"),
)
