from functools import cached_property

from django.test import TestCase

from security.authorization.roles import Role
from settings.models import Settings
from tests.framework import ApiTestNoData
from tests.framework.cases import ApiTestCase, PutApiTestCase

# pytype: disable=wrong-arg-types

settings = {
    "max_uploaded_file_mb": 512,
    "all_proxy": None,
    "http_proxy": None,
    "https_proxy": None,
    "ftp_proxy": None,
    "no_proxy": None,
}
new_settings = {
    "max_uploaded_file_mb": 1024,
    "all_proxy": "10.10.10.10:8080",
    "http_proxy": "http://10.10.10.10:80",
    "https_proxy": "https://10.10.10.10:443",
    "ftp_proxy": "ftp://10.10.10.10:21",
    "no_proxy": "127.0.0.1",
}
invalid_settings_1 = {
    "max_uploaded_file_mb": 1,
    "all_proxy": "10.10.10.10;8080",
    "http_proxy": "http://10.10.10.10;80",
    "https_proxy": "https://10.10.10.10;443",
    "ftp_proxy": "ftp://10.10.10.10;21",
    "no_proxy": "127.0.0;1",
}
invalid_settings_2 = {**invalid_settings_1, "max_uploaded_file_mb": 4096}


class SettingsTest(ApiTestNoData, TestCase):
    endpoint = "/api/settings/"
    expected_string = "Settings"
    cases = [
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], expected=[{"id": 1, **settings}]),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], expected={"id": 1, **settings}, endpoint="1/"),
        PutApiTestCase([Role.AUDITOR, Role.READER], 403, new_settings, endpoint="1"),
        PutApiTestCase([Role.ADMIN], 400, invalid_settings_1, endpoint="1"),
        PutApiTestCase([Role.ADMIN], 400, invalid_settings_2, endpoint="1"),
        PutApiTestCase([Role.ADMIN], data=new_settings, expected={"id": 1, **new_settings}, endpoint="1"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], expected=[{"id": 1, **new_settings}]),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], expected={"id": 1, **new_settings}, endpoint="1"),
    ]

    @cached_property
    def object(self) -> Settings:
        return Settings.objects.first()
