from typing import Any

from platforms.defect_dojo.models import DefectDojoSettings
from tests.cases import ApiTestCase
from tests.framework import ApiTest

settings = {
    "server": None,
    "api_token": None,
    "tls_validation": True,
    "tag": "rekono",
    "test_type": "Rekono Findings Import",
    "test": "Rekono Execution",
}
new_settings = {
    "server": "https://defectdojo.rekono.com",
    "api_token": "any_valid_defectdojo_token",
    "tls_validation": True,
    "tag": "rekono",
    "test_type": "Rekono",
    "test": "Rekono",
}
invalid_settings = {
    "server": "invalid server",
    "api_token": "invalid;token",
    "tls_validation": True,
    "tag": "rek;ono",
    "test_type": "Rek;ono",
    "test": "Rek;ono",
}


class DefectDojoSettingsTest(ApiTest):
    endpoint = "/api/defect-dojo/settings/1/"
    # expected_str = DefectDojoSettings.__class__.__name__
    cases = [
        ApiTestCase(["auditor1", "auditor2", "reader1", "reader2"], "get", 403),
        ApiTestCase(["admin1", "admin2"], "get", 200, expected={"id": 1, **settings}),
        ApiTestCase(
            ["auditor1", "auditor2", "reader1", "reader2"], "put", 403, new_settings
        ),
        ApiTestCase(["admin1", "admin2"], "put", 400, invalid_settings),
        ApiTestCase(
            ["admin1", "admin2"],
            "put",
            200,
            new_settings,
            expected={
                "id": 1,
                **new_settings,
                "api_token": "*" * len(new_settings["api_token"]),
                "is_available": False,
            },
        ),
        ApiTestCase(
            ["admin1", "admin2"],
            "get",
            200,
            expected={
                "id": 1,
                **new_settings,
                "api_token": "*" * len(new_settings["api_token"]),
                "is_available": False,
            },
        ),
    ]

    def _get_object(self) -> Any:
        return DefectDojoSettings.objects.get(pk=1)
