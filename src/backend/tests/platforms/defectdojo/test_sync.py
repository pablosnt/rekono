from typing import Any
from unittest import mock

from platforms.defectdojo.models import DefectDojoSync, DefectDojoTargetSync
from tests.cases import ApiTestCase
from tests.framework import ApiTest
from tests.platforms.defectdojo.mock import return_true

sync1 = {"project": 1, "product_type_id": 1, "product_id": 1, "engagement_id": 1}
sync2 = {"project": 1, "product_type_id": 1, "product_id": 1, "engagement_id": None}


class DefectDojoSyncTest(ApiTest):
    endpoint = "/api/defect-dojo/sync/"
    expected_str = "test - 1 - 1 - 1"
    cases = [
        ApiTestCase(["admin2", "auditor2", "reader1", "reader2"], "post", 403, sync1),
        ApiTestCase(["auditor1"], "post", 201, sync1, {"id": 1, **sync1}),
        # ApiTestCase(["admin1"], "post", 400, sync1),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected={"id": 1, "defectdojo_sync": {"id": 1, **sync1}},
            endpoint="/api/projects/1/",
        ),
        ApiTestCase(["reader1", "reader2"], "delete", 403, endpoint="{endpoint}1/"),
        ApiTestCase(
            ["admin2", "auditor2"],
            "delete",
            404,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(["admin1"], "delete", 204, endpoint="{endpoint}1/"),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected={"id": 1, "defectdojo_sync": None},
            endpoint="/api/projects/1/",
        ),
        ApiTestCase(["admin1"], "post", 201, sync2, {"id": 2, **sync2}),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected={"id": 1, "defectdojo_sync": {"id": 2, **sync2}},
            endpoint="/api/projects/1/",
        ),
        ApiTestCase(["auditor1"], "delete", 204, endpoint="{endpoint}2/"),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected={"id": 1, "defectdojo_sync": None},
            endpoint="/api/projects/1/",
        ),
    ]

    @mock.patch(
        "platforms.defectdojo.integrations.DefectDojo.is_available", return_true
    )
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.exists", return_true)
    def test_cases(self) -> None:
        super().test_cases()

    def setUp(self) -> None:
        super().setUp()
        self._setup_project()

    def _get_object(self) -> Any:
        return DefectDojoSync.objects.create(**{**sync1, "project": self.project})


class DefectDojoTargetSyncTest(ApiTest):
    expected_str = "test - 1 - 1 - 10.10.10.10 - 1"

    def setUp(self) -> None:
        super().setUp()
        self._setup_target()

    def _get_object(self) -> Any:
        return DefectDojoTargetSync.objects.create(
            defectdojo_sync=DefectDojoSync.objects.create(
                **{**sync2, "project": self.project}
            ),
            target=self.target,
            engagement_id=1,
        )
