from typing import Any

from integrations.models import Integration
from tests.cases import ApiTestCase
from tests.framework import ApiTest


class IntegrationTest(ApiTest):
    endpoint = "/api/integrations/"
    expected_str = "Defect-Dojo"
    cases = [
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected=[
                {"id": 4, "enabled": True},
                {"id": 3, "enabled": True},
                {"id": 2, "enabled": True},
                {"id": 1, "enabled": True},
            ],
        ),
        ApiTestCase(
            ["auditor1", "auditor2", "reader1", "reader2"],
            "put",
            403,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin1", "admin2"],
            "put",
            200,
            {"enabled": False},
            {"id": 1, "enabled": False},
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected=[
                {"id": 4, "enabled": True},
                {"id": 3, "enabled": True},
                {"id": 2, "enabled": True},
                {"id": 1, "enabled": False},
            ],
        ),
    ]

    def _get_object(self) -> Any:
        return Integration.objects.first()
