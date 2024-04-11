from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from jinja2 import Template


class Command(BaseCommand):
    help = "Generate openresty config template"

    def add_arguments(self, parser):
        parser.add_argument("--gateway", required=True, type=str)

    def handle(self, *args, **options):
        template = Template(
            (Path(__file__).parent / "openresty.conf.jinja").open("r").read()
        )
        return template.render(
            gateway=options["gateway"],
            static_root=str(settings.STATIC_ROOT).removesuffix("/") + "/",
            static_path=settings.STATIC_URL,
        )
