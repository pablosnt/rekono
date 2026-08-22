"""Command that migrates a version 1.x configuration file to the 2.x schema.

Version 2.x keeps the SMTP configuration in the database, and derives the root path from the
frontend URL, so the values that version 1.x kept in the configuration file have to be moved
before that file can be cleaned up. The deployment runs this after migrate, since the SMTP
settings live in a table that the migrations create. It is only needed until every deployment
has been upgraded, and can be removed then.
"""

from typing import Any
from urllib.parse import urlparse

from django.core.management.base import BaseCommand

from framework.logging import LoggingEntity
from platforms.email.models import SMTPSettings
from rekono.config import Property
from rekono.settings import CONFIG

ROOT_PATH = Property("RKN_ROOT_PATH", "rootpath", None)
SMTP = Property(None, "email", None)
SMTP_HOST = Property("RKN_EMAIL_HOST", "email.host", None)
SMTP_PORT = Property("RKN_EMAIL_PORT", "email.port", 587)
SMTP_USERNAME = Property("RKN_EMAIL_USER", "email.user", None)
SMTP_PASSWORD = Property("RKN_EMAIL_PASSWORD", "email.password", None)
SMTP_TLS = Property(None, "email.tls", True)
FRONTEND_URL = Property(None, "frontend.url", "https://127.0.0.1")
NEW_KEYS = {
    "security.cookies.secure": False,
    "reports.pdf-template": None,
    "tools.emailharvester.directory": "/opt/EmailHarvester",
}


class Command(BaseCommand, LoggingEntity):
    """Command that moves the deprecated version 1.x values out of the configuration file.

    Attributes:
        help: Description of the command shown by the Django help.
    """

    help = "Apply the version 2.x schema to a configuration file written by version 1.x"

    def handle(self, *args: Any, **options: Any) -> None:
        """Move the deprecated configuration to the database and clean up the file.

        Every step is skipped when the version 1.x value it migrates is not in the file, so
        this is a no-op on a fresh installation and on a deployment already upgraded.

        Args:
            *args: Not used, since the command takes no arguments.
            **options: Not used, since the command takes no options.
        """
        if not CONFIG.config_file.is_file():
            self.stdout.write(self.style.ERROR("No configuration file found"))
            return
        root_path = ROOT_PATH.read(CONFIG.config_from_file)
        smtp_host = SMTP_HOST.read(CONFIG.config_from_file)
        if smtp_host:
            settings = SMTPSettings.objects.first()
            if not settings.host:
                settings.host = smtp_host
                settings.port = SMTP_PORT.read(CONFIG.config_from_file)
                settings.username = SMTP_USERNAME.read(CONFIG.config_from_file)
                settings.tls = SMTP_TLS.read(CONFIG.config_from_file)
                settings.secret = SMTP_PASSWORD.read(CONFIG.config_from_file)
                settings.save()
                self.stdout.write(f"SMTP settings updated from {CONFIG.config_file}")
            else:
                self.stdout.write(self.style.WARNING("SMTP server is already configured"))
            SMTP.remove(CONFIG)
        elif root_path:
            frontend_url = str(FRONTEND_URL.read(CONFIG.config_from_file)).rstrip("/")
            # A frontend URL that already carries a path is not changed
            if not urlparse(frontend_url).path.strip("/"):
                FRONTEND_URL.update(CONFIG, f"{frontend_url}/{str(root_path).strip('/')}")
            ROOT_PATH.remove(CONFIG)
        else:
            self.stdout.write(self.style.ERROR("No configuration file from Rekono 1.x found"))
            return
        for key, value in NEW_KEYS.items():
            Property(None, key, value).update(CONFIG, value)
        self.stdout.write("Created new configuration entries")
