from unittest import mock

from tests.cases import ApiTestCase
from tests.framework import ApiTest
from tests.platforms.mocks.defect_dojo import (
    create_engagement,
    create_product,
    create_product_type,
    return_true,
)

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


class DefectDojoEntitiesTest(ApiTest):
    endpoint = "/api/defect-dojo/"
    cases = []

    def setUp(self) -> None:
        super().setUp()
        self._setup_project()

    @mock.patch(
        "platforms.defect_dojo.integrations.DefectDojo.is_available", return_true
    )
    @mock.patch("platforms.defect_dojo.integrations.DefectDojo.exists", return_true)
    @mock.patch(
        "platforms.defect_dojo.integrations.DefectDojo.create_product_type",
        create_product_type,
    )
    @mock.patch(
        "platforms.defect_dojo.integrations.DefectDojo.create_product", create_product
    )
    @mock.patch(
        "platforms.defect_dojo.integrations.DefectDojo.create_engagement",
        create_engagement,
    )
    def test_cases(self) -> None:
        valid = {"name": "test", "description": "test"}
        invalid = {"name": "te;st", "description": "te;st"}
        for endpoint, valid, invalid in [
            (f"{self.endpoint}product-types/", valid, invalid),
            (
                f"{self.endpoint}products/",
                {"product_type": 1, "project_id": 1, **valid},
                {"product_type": 9999999999, "project_id": 1, **invalid},
            ),
            (
                f"{self.endpoint}engagements/",
                {"product": 1, **valid},
                {"product": 1, **invalid},
            ),
        ]:
            self.cases.extend(
                [
                    ApiTestCase(
                        ["reader1", "reader2"], "post", 403, valid, endpoint=endpoint
                    ),
                    ApiTestCase(
                        ["admin1", "admin2", "auditor1", "auditor2"],
                        "post",
                        400,
                        invalid,
                        endpoint=endpoint,
                    ),
                ]
            )
            self.cases.extend(
                [
                    ApiTestCase(
                        ["admin1", "auditor1"], "post", 201, valid, {"id": 1}, endpoint
                    ),
                    ApiTestCase([], "post", 404, valid, endpoint),
                ]
                if "project_id" in valid
                else [
                    ApiTestCase(
                        ["admin1", "admin2", "auditor1", "auditor2"],
                        "post",
                        201,
                        valid,
                        {"id": 1},
                        endpoint,
                    )
                ]
            )
        super().test_cases()
        self.cases = []

    def test_anonymous_access(self) -> None:
        base = self.endpoint
        for endpoint in ["product-types", "products", "engagements"]:
            self.endpoint = f"{base}{endpoint}/"
            super().test_anonymous_access()
        self.endpoint = base
