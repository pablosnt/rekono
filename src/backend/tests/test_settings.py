from typing import Any

from settings.models import Settings
from tests.cases import ApiTestCase
from tests.framework import RekonoTest

settings = {"max_uploaded_file_mb": 512}
new_settings = {"max_uploaded_file_mb": 1024}
invalid_settings_1 = {"max_uploaded_file_mb": 1}
invalid_settings_2 = {"max_uploaded_file_mb": 4096}


class SettingsTest(RekonoTest):
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
