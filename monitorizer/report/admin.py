from django.contrib import admin
from unfold.admin import ModelAdmin

from monitorizer.report.models import *


@admin.register(TelegramReport)
class TelegramReportAdmin(ModelAdmin):
    list_display = ["id", "chat_id", "api_id", "interval", "last_executed"]
    readonly_fields = ["last_executed"]
    list_filter = ["enabled"]


@admin.register(WebHookReport)
class WebHookReportAdmin(ModelAdmin):
    list_display = ["id", "url", "interval", "last_executed"]
    list_filter = ["enabled"]
    readonly_fields = ["last_executed"]
