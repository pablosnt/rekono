from typing import Any

from platforms.mail.models import SMTPSettings
from tests.cases import ApiTestCase
from tests.framework import ApiTest

settings = {
    "host": "smtp.rekono.com",
    "port": 587,
    "username": "rekono",
    "password": "rekono",
    "tls": True,
}
invalid_settings = {
    "host": "smtp;rekono.com",
    "port": 999999,
    "username": "reko;no",
    "password": "re;kono",
    "tls": True,
}


class SmtpSettingsTest(ApiTest):
    endpoint = "/api/smtp/1/"
    expected_str = f"{settings['host']}:{settings['port']}"
    cases = [
        ApiTestCase(["auditor1", "auditor2", "reader1", "reader2"], "get", 403),
        ApiTestCase(
            ["admin1", "admin2"],
            "get",
            200,
            expected={
                "id": 1,
                "host": None,
                "port": 587,
                "username": None,
                "password": None,
                "tls": True,
                "is_available": False,
            },
        ),
        ApiTestCase(
            ["auditor1", "auditor2", "reader1", "reader2"], "put", 403, settings
        ),
        ApiTestCase(["admin1", "admin2"], "put", 400, invalid_settings),
        ApiTestCase(
            ["admin1", "admin2"],
            "put",
            200,
            settings,
            expected={
                "id": 1,
                **settings,
                "password": "*" * len(settings["password"]),
                "is_available": False,
            },
        ),
        ApiTestCase(
            ["admin1", "admin2"],
            "get",
            200,
            expected={
                "id": 1,
                **settings,
                "password": "*" * len(settings["password"]),
                "is_available": False,
            },
        ),
    ]

    def _get_object(self) -> Any:
        settings = SMTPSettings.objects.get(pk=1)
        settings["secret"] = settings.pop("password")
        for field, value in settings.items():
            setattr(settings, field, value)
        settings["_password"] = settings.pop("secret")
        settings.save(update_fields=settings.keys())
        return settings
