from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin, StackedInline
from unfold.contrib.import_export.forms import ExportForm, ImportForm
from unfold.decorators import display

from monitorizer.inventory import models


class SeedDomainResource(resources.ModelResource):
    class Meta:
        model = models.SeedDomain
        fields = ("value",)


class CommandTemplateResource(resources.ModelResource):
    class Meta:
        model = models.CommandTemplate
        fields = ("name", "cmd", "parser")


class ScanDescriptorAdmin(StackedInline):
    extra = 0
    model = models.ScanAutoSubmitter


@admin.register(models.DiscoveredDomain)
class DiscoveredDomainAdmin(
    ImportExportModelAdmin,
    ModelAdmin,
):
    export_form_class = ExportForm
    import_form_class = ImportForm
    list_display = ["id", "value", "created_at"]
    search_fields = ["id", "value"]

    def has_import_permission(self, request):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return models.DiscoveredDomain.objects.order_by("-created_at")


@admin.register(models.SeedDomain)
class SeedDomainAdmin(
    ImportExportModelAdmin,
    ModelAdmin,
):
    resource_class = SeedDomainResource
    export_form_class = ExportForm
    import_form_class = ImportForm
    inlines = [ScanDescriptorAdmin]
    search_fields = ["id", "value"]
    list_filter = ["enabled"]
    list_display = ["id", "value", "enabled", "created_at"]
    add_fieldsets = ((None, {"fields": ["value"]}),)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["value"]
        return []

    def get_queryset(self, request):
        return models.SeedDomain.objects.order_by("-created_at")


@admin.register(models.DomainScan)
class DomainScanAdmin(ModelAdmin, ImportExportModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    add_fieldsets = ((None, {"fields": ["domain", "command_tpl"]}),)
    list_display = [
        "id",
        "command_name",
        "scan_domain",
        "status_label",
        "created_at",
        "finished_at",
    ]

    @display(
        description="Status",
        ordering="status",
        label={
            models.DomainScan.ScanStatus.PENDING: "warning",
            models.DomainScan.ScanStatus.RUNNING: "info",
            models.DomainScan.ScanStatus.SUCCESS: "success",
            models.DomainScan.ScanStatus.ERROR: "danger",
        },
    )
    def status_label(self, obj):
        return obj.status

    @staticmethod
    def scan_domain(obj):
        return obj.domain.value

    @staticmethod
    def command_name(obj):
        return obj.command_tpl.name

    def has_change_permission(self, request, obj=None):
        return False

    def has_import_permission(self, request):
        return False

    def get_queryset(self, request):
        return models.DomainScan.objects.order_by("-created_at")


@admin.register(models.CommandTemplate)
class CommandTemplateAdmin(ModelAdmin, ImportExportModelAdmin):
    export_form_class = ExportForm
    import_form_class = ImportForm
    resource_class = CommandTemplateResource
    list_display = ["id", "name"]

    def get_queryset(self, request):
        return models.CommandTemplate.objects.order_by("-created_at")
