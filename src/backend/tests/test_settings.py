from typing import Any

from settings.models import Settings
from tests.cases import ApiTestCase
from tests.framework import ApiTest

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


class SettingsTest(ApiTest):
    endpoint = "/api/settings/"
    expected_str = "Settings"
    cases = [
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected=[{"id": 1, **settings}],
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected={"id": 1, **settings},
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["auditor1", "auditor2", "reader1", "reader2"],
            "put",
            403,
            new_settings,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin1", "admin2"],
            "put",
            400,
            invalid_settings_1,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin1", "admin2"],
            "put",
            400,
            invalid_settings_2,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin1", "admin2"],
            "put",
            200,
            new_settings,
            expected={"id": 1, **new_settings},
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected=[{"id": 1, **new_settings}],
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected={"id": 1, **new_settings},
            endpoint="{endpoint}1/",
        ),
    ]

    def _get_object(self) -> Any:
        return Settings.objects.first()
