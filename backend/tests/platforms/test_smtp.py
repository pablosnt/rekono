from functools import cached_property

from django.test import TestCase

from platforms.mail.models import SMTPSettings
from security.authorization.roles import Role
from tests.framework import ApiTestNoData
from tests.framework.cases import ApiTestCase, PutApiTestCase

# pytype: disable=wrong-arg-types

config = {"host": "smtp.rekono.com", "port": 587, "username": "rekono", "password": "rekono", "tls": True}
invalid_config = {"host": "smtp;rekono.com", "port": 999999, "username": "reko;no", "password": "re;kono", "tls": True}


class SmtpSettingsTest(ApiTestNoData, TestCase):
    endpoint = "/api/smtp/1/"
    expected_string = f"{config['host']}:{config['port']}"
    cases = [
        ApiTestCase([Role.AUDITOR, Role.READER], status_code=403),
        ApiTestCase(
            [Role.ADMIN],
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
        PutApiTestCase([Role.AUDITOR, Role.READER], 403, config),
        PutApiTestCase([Role.ADMIN], 400, invalid_config),
        PutApiTestCase(
            [Role.ADMIN],
            data=config,
            expected={"id": 1, **config, "password": "*" * len(str(config.get("password", ""))), "is_available": False},
        ),
        ApiTestCase(
            [Role.ADMIN],
            expected={"id": 1, **config, "password": "*" * len(str(config.get("password", ""))), "is_available": False},
        ),
    ]

    @cached_property
    def object(self) -> SMTPSettings:
        settings = SMTPSettings.objects.get(pk=1)
        config["secret"] = config.pop("password")
        for field, value in config.items():
            setattr(settings, field, value)
        config["_password"] = config.pop("secret")
        settings.save(update_fields=config.keys())
        return settings
