from functools import cached_property
from typing import Any, cast
from unittest import mock

from platforms.defectdojo.integrations import DefectDojo
from platforms.defectdojo.models import DefectDojoSettings, DefectDojoSync, DefectDojoTargetSync
from security.authorization.roles import Role
from tests.framework import ApiTest, BaseTest
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase, PutApiTestCase

# pytype: disable=wrong-arg-types


def return_true(*args: Any) -> bool:
    return True


def return_false(*args: Any) -> bool:
    return False


def return_id(*args: Any) -> dict[str, int]:
    return {"id": 1}


def create_product_type(*args: Any) -> dict[str, Any]:
    return {"id": 1, "name": args[1], "description": args[2]}


def create_product(*args: Any) -> dict[str, Any]:
    return {"id": 1, "prod_type": args[1], "name": args[2], "description": args[3], "tags": args[4]}


def create_engagement(*args: Any) -> dict[str, Any]:
    return {"id": 1, "product": args[1], "name": args[2], "description": args[3], "tags": args[4]}


def create_test_type(*args: Any) -> dict[str, Any]:
    return {"id": 1, "name": args[1], "tags": args[2], "dynamic_tool": True}


def create_test(*args: Any) -> dict[str, Any]:
    return {"id": 1, "test_type": args[1], "engagement": args[2], "title": args[3], "description": args[4]}


def import_scan(*args: Any) -> dict[str, Any]:
    return {"test_id": 1, "engagement_id": 1, "product_id": 1, "product_type_id": 1, "active": True}


class DefectDojoEntitiesTest(ApiTest):
    endpoint = "/api/defect-dojo/"
    setup_entities = ["project"]
    valid = {"name": "test", "description": "test"}
    invalid = {"name": "te;st", "description": "te;st"}
    entity_cases = [
        ("product-types", {}, {}),
        ("products", {"product_type": 1, "project_id": 1}, {"product_type": 9999999999, "project_id": 1}),
        ("engagements", {"product": 1}, {"product": 1}),
    ]

    @cached_property
    def cases(self) -> list[ApiTestCase]:
        cases = []
        for entity, valid, invalid in self.entity_cases:
            valid = {**valid, **self.valid}
            invalid = {**invalid, **self.invalid}
            cases.extend(
                [
                    PostApiTestCase([Role.READER], 403, data=valid, endpoint=entity),
                    PostApiTestCase([Role.ADMIN, Role.AUDITOR], 400, data=invalid, endpoint=entity),
                ]
                + (
                    [
                        PostApiTestCase(["admin1", "auditor1"], data=valid, expected={"id": 1}, endpoint=entity),
                        PostApiTestCase(["admin2", "auditor2"], 404, valid, endpoint=entity),
                    ]
                    if "project_id" in cast(dict[str, str], valid)
                    else [PostApiTestCase([Role.ADMIN, Role.AUDITOR], data=valid, expected={"id": 1}, endpoint=entity)]
                )
            )
        return cases

    @mock.patch("platforms.defectdojo.integrations.DefectDojo.is_available", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.exists", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.create_product_type", create_product_type)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.create_product", create_product)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.create_engagement", create_engagement)
    def test_cases(self) -> None:
        super().test_cases()

    @mock.patch("platforms.defectdojo.integrations.DefectDojo.is_available", return_false)
    def test_cases_not_available(self) -> None:
        for entity, valid, _ in self.entity_cases:
            PostApiTestCase(["admin1", "auditor1"], 400, {**valid, **self.valid}, endpoint=entity).test_case(
                1, self, base_endpoint=self.endpoint
            )

    def test_anonymous_access(self) -> None:
        base = self.endpoint
        for entity, _, _ in self.entity_cases:
            self.endpoint = f"{base}{entity}/"
            super().test_anonymous_access()
        self.endpoint = base


sync: dict[str, Any] = {"project": 1, "product_type_id": 1, "product_id": 1, "engagement_id": 1}


class DefectDojoIntegrationTest(BaseTest):
    endpoint = "/api/defect-dojo/"
    setup_entities = ["executions"]

    @mock.patch("platforms.defectdojo.integrations.DefectDojo.is_available", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.exists", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo._import_scan", import_scan)
    def test_project_sync(self) -> None:
        PostApiTestCase(["admin1"], data=sync, expected={"id": 1, **sync}, endpoint="sync").test_case(
            0, self, self.endpoint
        )
        self.setup_findings()
        self.selected_execution.output_file = self.data_dir / "reports" / "nmap" / "enumeration-vulners.xml"
        DefectDojo().process_findings(self.selected_execution, self.findings)
        self.assertEqual(1, self.selected_execution.defectdojo_test_id)
        for finding in self.findings:
            self.assertIsNone(finding.defectdojo_id)

    @mock.patch("platforms.defectdojo.integrations.DefectDojo.is_available", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.exists", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.create_engagement", create_engagement)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo._create_test_type", create_test_type)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo._create_test", create_test)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo._create_endpoint", return_id)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo._create_finding", return_id)
    def test_target_sync(self) -> None:
        sync["engagement_id"] = None
        PostApiTestCase(["auditor1"], data=sync, expected={"id": 1, **sync}, endpoint="sync").test_case(
            0, self, self.endpoint
        )
        self.assertFalse(DefectDojoTargetSync.objects.filter(target=self.target).exists())
        self.setup_findings()
        integration = DefectDojo()
        integration.process_findings(self.selected_execution, self.findings)
        self.assertTrue(DefectDojoTargetSync.objects.filter(target=self.target).exists())
        for finding in self.findings:
            self.assertEqual(1, finding.defectdojo_id)
        integration.process_findings(self.selected_execution, self.findings)
        self.assertEqual(1, DefectDojoTargetSync.objects.filter(target=self.target).count())
        for finding in self.findings:
            self.assertEqual(1, finding.defectdojo_id)


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
    expected_string = "DefectDojoSettings"
    cases = [
        ApiTestCase([Role.AUDITOR, Role.READER], 403),
        ApiTestCase([Role.ADMIN], expected={"id": 1, **settings}),
        PutApiTestCase([Role.AUDITOR, Role.READER], 403, data=new_settings),
        PutApiTestCase([Role.ADMIN], 400, data=invalid_settings),
        PutApiTestCase(
            [Role.ADMIN],
            data=new_settings,
            expected={
                "id": 1,
                **new_settings,
                "api_token": "*" * len(str(new_settings.get("api_token", ""))),
                "is_available": False,
            },
        ),
        ApiTestCase(
            [Role.ADMIN],
            expected={
                "id": 1,
                **new_settings,
                "api_token": "*" * len(str(new_settings.get("api_token", ""))),
                "is_available": False,
            },
        ),
    ]

    @cached_property
    def object(self) -> DefectDojoSettings:
        return DefectDojoSettings.objects.get(pk=1)


sync1 = {"project": 1, "product_type_id": 1, "product_id": 1, "engagement_id": 1}
sync2 = {"project": 1, "product_type_id": 1, "product_id": 1, "engagement_id": None}


class DefectDojoSyncTest(ApiTest):
    endpoint = "/api/defect-dojo/sync/"
    expected_string = "test - 1 - 1 - 1"
    setup_entities = ["project"]
    cases = [
        PostApiTestCase(["admin2", "auditor2", Role.READER], 403, sync1),
        PostApiTestCase(["auditor1"], data=sync1, expected={"id": 1, **sync1}),
        PostApiTestCase(["admin1"], 400, data=sync1),
        ApiTestCase(
            ["members"], expected={"id": 1, "defectdojo_sync": {"id": 1, **sync1}}, endpoint="/api/projects/1/"
        ),
        DeleteApiTestCase([Role.READER], 403, endpoint="1/"),
        DeleteApiTestCase(["admin2", "auditor2"], 404, endpoint="1"),
        DeleteApiTestCase(["admin1"], endpoint="1"),
        ApiTestCase(["members"], expected={"id": 1, "defectdojo_sync": None}, endpoint="/api/projects/1/"),
        PostApiTestCase(["admin1"], data=sync2, expected={"id": 2, **sync2}),
        ApiTestCase(
            ["members"], expected={"id": 1, "defectdojo_sync": {"id": 2, **sync2}}, endpoint="/api/projects/1/"
        ),
        DeleteApiTestCase(["auditor1"], endpoint="2"),
        ApiTestCase(["members"], expected={"id": 1, "defectdojo_sync": None}, endpoint="/api/projects/1/"),
    ]

    @mock.patch("platforms.defectdojo.integrations.DefectDojo.is_available", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.exists", return_true)
    def test_cases(self) -> None:
        super().test_cases()

    @cached_property
    def object(self) -> DefectDojoSync:
        return DefectDojoSync.objects.create(**{**sync1, "project": self.project})


class DefectDojoTargetSyncTest(ApiTest):
    expected_string = "test - 1 - 1 - 10.10.10.10 - 1"
    setup_entities = ["target"]

    @cached_property
    def object(self) -> DefectDojoTargetSync:
        defectdojo_sync = DefectDojoSync.objects.create(**{**sync2, "project": self.project})
        return DefectDojoTargetSync.objects.create(defectdojo_sync=defectdojo_sync, target=self.target, engagement_id=1)
