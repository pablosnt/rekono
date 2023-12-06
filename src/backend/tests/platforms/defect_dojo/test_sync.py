from unittest import mock

from tests.cases import ApiTestCase
from tests.framework import ApiTest
from tests.platforms.defect_dojo.mock import return_true

sync1 = {"project": 1, "product_type_id": 1, "product_id": 1, "engagement_id": 1}
sync2 = {"project": 1, "product_type_id": 1, "product_id": 1, "engagement_id": None}


class DefectDojoSyncTest(ApiTest):
    endpoint = "/api/defect-dojo/sync/"

    cases = [
        ApiTestCase(["admin2", "auditor2", "reader1", "reader2"], "post", 403, sync1),
        ApiTestCase(["auditor1"], "post", 201, sync1, {"id": 1, **sync1}),
        # ApiTestCase(["admin1"], "post", 400, sync1),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected={"id": 1, "defect_dojo_sync": {"id": 1, **sync1}},
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
            expected={"id": 1, "defect_dojo_sync": None},
            endpoint="/api/projects/1/",
        ),
        ApiTestCase(["admin1"], "post", 201, sync2, {"id": 2, **sync2}),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected={"id": 1, "defect_dojo_sync": {"id": 2, **sync2}},
            endpoint="/api/projects/1/",
        ),
        ApiTestCase(["auditor1"], "delete", 204, endpoint="{endpoint}2/"),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected={"id": 1, "defect_dojo_sync": None},
            endpoint="/api/projects/1/",
        ),
    ]

    @mock.patch(
        "platforms.defect_dojo.integrations.DefectDojo.is_available", return_true
    )
    @mock.patch("platforms.defect_dojo.integrations.DefectDojo.exists", return_true)
    def test_cases(self) -> None:
        super().test_cases()

    def setUp(self) -> None:
        super().setUp()
        self._setup_project()
