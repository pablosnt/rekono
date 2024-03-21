from typing import Dict, List, cast
from unittest import mock

from tests.cases import ApiTestCase, RekonoTestCase
from tests.framework import ApiTest
from tests.platforms.defect_dojo.mock import (
    create_engagement,
    create_product,
    create_product_type,
    return_false,
    return_true,
)


class DefectDojoEntitiesTest(ApiTest):
    endpoint = "/api/defect-dojo/"
    cases: List[RekonoTestCase] = []

    def setUp(self) -> None:
        super().setUp()
        self._setup_project()
        valid = {"name": "test", "description": "test"}
        invalid = {"name": "te;st", "description": "te;st"}
        self.entities_cases = [
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
        ]
        for endpoint, valid_data, invalid_data in self.entities_cases:
            self.cases.extend(
                [
                    ApiTestCase(
                        ["reader1", "reader2"],
                        "post",
                        403,
                        valid_data,
                        endpoint=endpoint,
                    ),
                    ApiTestCase(
                        ["admin1", "admin2", "auditor1", "auditor2"],
                        "post",
                        400,
                        invalid_data,
                        endpoint=endpoint,
                    ),
                ]
            )
            self.cases.extend(
                [
                    ApiTestCase(
                        ["admin1", "auditor1"],
                        "post",
                        201,
                        valid_data,
                        {"id": 1},
                        endpoint,
                    ),
                    ApiTestCase([], "post", 404, valid_data, endpoint),
                ]
                if "project_id" in cast(Dict[str, str], valid_data)
                else [
                    ApiTestCase(
                        ["admin1", "admin2", "auditor1", "auditor2"],
                        "post",
                        201,
                        valid_data,
                        {"id": 1},
                        endpoint,
                    )
                ]
            )

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
        super().test_cases()

    @mock.patch(
        "platforms.defect_dojo.integrations.DefectDojo.is_available", return_false
    )
    def test_cases_not_available(self) -> None:
        for endpoint, valid, _ in self.entities_cases:
            ApiTestCase(
                ["admin1", "auditor1"], "post", 400, valid, endpoint=endpoint
            ).test_case(endpoint=endpoint)

    def test_anonymous_access(self) -> None:
        base = self.endpoint
        for endpoint in ["product-types", "products", "engagements"]:
            self.endpoint = f"{base}{endpoint}/"
            super().test_anonymous_access()
        self.endpoint = base
