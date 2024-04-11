import json

from django.db.models import Count, Q

from monitorizer.inventory import models

DEFAULT_CHART_OPTIONS = {
    "barPercentage": 1,
    "base": 0,
    "grouped": True,
    "maxBarThickness": 4,
    "responsive": True,
    "maintainAspectRatio": False,
    "datasets": {
        "bar": {
            "borderRadius": 12,
            "border": {"width": 0},
            "borderSkipped": "middle",
        },
        "line": {"borderWidth": 2, "pointBorderWidth": 0, "pointStyle": False},
    },
    "plugins": {
        "legend": {
            "align": "end",
            "display": True,
            "position": "top",
            "labels": {
                "boxHeight": 5,
                "boxWidth": 5,
                "color": "#9ca3af",
                "pointStyle": "circle",
                "usePointStyle": True,
            },
        },
        "tooltip": {"enabled": True},
    },
}


def dashboard_callback(request, context):
    scans_per_day = {
        group["created_day"]: group
        for group in models.DomainScan.objects.extra(
            {"created_day": "date(created_at)"}
        )
        .values("created_day")
        .annotate(
            success=Count(
                "status", filter=Q(status=models.DomainScan.ScanStatus.SUCCESS)
            ),
            error=Count("status", filter=Q(status=models.DomainScan.ScanStatus.ERROR)),
            running=Count(
                "status", filter=Q(status=models.DomainScan.ScanStatus.RUNNING)
            ),
            pending=Count(
                "status", filter=Q(status=models.DomainScan.ScanStatus.PENDING)
            ),
        )
    }
    top_seeds = {
        group["seeds__value"]: group["count"]
        for group in models.DiscoveredDomain.objects.values("seeds__value")
        .annotate(count=Count("seeds__value"))
        .order_by("-count")[:5]
    }
    context.update(
        {
            "DEFAULT_CHART_OPTIONS": json.dumps(DEFAULT_CHART_OPTIONS),
            "discovered_breakdown": json.dumps(
                {
                    "labels": list(top_seeds.keys()),
                    "datasets": [{"data": list(top_seeds.values())}],
                }
            ),
            "activity_per_day_chart": json.dumps(
                {
                    "labels": [str(v) for v in scans_per_day.keys()],
                    "datasets": [
                        {
                            "label": "Pending",
                            "data": [v["pending"] for v in scans_per_day.values()],
                            "backgroundColor": "#faf20a",
                        },
                        {
                            "label": "Running",
                            "data": [v["running"] for v in scans_per_day.values()],
                            "backgroundColor": "#1f85e5",
                        },
                        {
                            "label": "Success",
                            "data": [v["success"] for v in scans_per_day.values()],
                            "backgroundColor": "#0ad153",
                        },
                        {
                            "label": "Error",
                            "data": [v["error"] for v in scans_per_day.values()],
                            "backgroundColor": "#f54257",
                        },
                    ],
                }
            ),
            "cards": [
                {
                    "title": "Seeds",
                    "value": models.SeedDomain.objects.count(),
                },
                {
                    "title": "Overall Scans",
                    "value": models.DomainScan.objects.count(),
                },
                {
                    "title": "Discovered",
                    "value": models.DiscoveredDomain.objects.count(),
                },
            ],
        }
    )
    return context
