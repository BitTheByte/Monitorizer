import os

import yaml

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitorizer.server.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from django.conf import settings
from django.contrib.auth.models import User

from monitorizer.inventory import models as inventory_models

email = os.environ.get("ADMIN_EMAIL", "monitorizer@bitthebyte.com")
username = os.getenv("ADMIN_USERNAME", "admin")
password = os.getenv("ADMIN_PASSWORD", "P@ssW0rd")

system_user = User.objects.filter(username=username).first()
if not system_user:
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        is_active=True,
        is_staff=True,
        is_superuser=True,
    )

defaults_config = yaml.safe_load(open(settings.BASE_DIR / "default.yml"))
for command in defaults_config.get("commands", []):
    inventory_models.CommandTemplate.objects.get_or_create(
        id=command["id"],
        defaults={
            "name": command["name"],
            "cmd": command["cmd"],
            "parser": command["parser"],
        },
    )
