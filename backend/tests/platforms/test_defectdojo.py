from functools import cached_property
from typing import Any
from unittest import mock

from django.test import TestCase

from findings.models import Path
from platforms.defectdojo.integrations import DefectDojo
from platforms.defectdojo.models import DefectDojoSettings, DefectDojoSync, DefectDojoTargetSync
from security.authorization.roles import Role
from tests.framework import ApiTest, ApiTestNoData, BaseTest
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase, PutApiTestCase
from tests.framework.data import SetupProject
from tools.models import Configuration

# pytype: disable=wrong-arg-types


def return_true(*args: Any, **kwargs: Any) -> bool:
    return True


def return_false(*args: Any, **kwargs: Any) -> bool:
    return False


def return_id(*args: Any, **kwargs: Any) -> dict[str, int]:
    return {"id": 1}


def create_engagement(*args: Any) -> dict[str, Any]:
    return {"id": 1, "product": args[1], "name": args[2], "description": args[3], "tags": args[4]}


def import_scan(*args: Any) -> dict[str, Any]:
    return {"test_id": 1, "engagement_id": 1, "product_id": 1, "product_type_id": 1, "active": True}


def return_test_type(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"id": 1, "name": "Nmap Scan"}


def return_test(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"id": 5}


def get_engagement(*args: Any, **kwargs: Any) -> tuple[dict[str, Any], bool]:
    # args: (self, "engagements", engagement_id); the engagement belongs to product 1
    return {"id": args[-1], "product": 1}, True


def get_engagement_other_product(*args: Any, **kwargs: Any) -> tuple[dict[str, Any], bool]:
    # The engagement exists but belongs to a different product
    return {"id": args[-1], "product": 999}, True


def exception(*args: Any, **kwargs: Any) -> Any:
    raise Exception("Test")


def missing(*args: Any, **kwargs: Any) -> tuple[None, bool]:
    return None, False


def product_exists_but_engagement_missing(*args: Any, **kwargs: Any) -> tuple[dict[str, Any] | None, bool]:
    return ({"id": args[-1]}, True) if args[1] == "products" else missing()


sync = {"project": 1, "product_id": 1, "engagement_id": 1}
sync_no_engagement = {"project": 1, "product_id": 1, "engagement_id": None}


class DefectDojoIntegrationTest(BaseTest, TestCase):
    endpoint = "/api/defectdojo/"
    data = [SetupProject()]

    @mock.patch("platforms.defectdojo.integrations.DefectDojo.is_enabled", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.is_available", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.exists", get_engagement)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo._import_or_reimport_scan", import_scan)
    def test_project_sync(self) -> None:
        self.execution.output_file = self.data_dir / "reports" / "nmap" / "enumeration-vulners.xml"
        DefectDojo().process_findings(self.execution, self.findings)
        self.assertIsNone(self.execution.defectdojo_test_id)
        PostApiTestCase(["admin1"], data=sync, expected={"id": 1, **sync}, endpoint="sync").test_case(
            0, self, self.endpoint
        )
        DefectDojo().process_findings(self.execution, self.findings)
        self.assertEqual(1, self.execution.defectdojo_test_id)

    @mock.patch("platforms.defectdojo.integrations.DefectDojo.is_enabled", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.is_available", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.exists", get_engagement)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.create_engagement", create_engagement)
    def test_target_sync(self) -> None:
        PostApiTestCase(
            ["auditor1"], data=sync_no_engagement, expected={"id": 1, **sync_no_engagement}, endpoint="sync"
        ).test_case(0, self, self.endpoint)
        self.assertFalse(DefectDojoTargetSync.objects.filter(target=self.target).exists())
        integration = DefectDojo()
        integration.process_findings(self.execution, self.findings)
        self.assertTrue(DefectDojoTargetSync.objects.filter(target=self.target).exists())
        integration.process_findings(self.execution, self.findings)
        self.assertEqual(1, DefectDojoTargetSync.objects.filter(target=self.target).count())

    def test_process_findings_empty(self) -> None:
        DefectDojoSync.objects.create(project=self.project, product_id=1, engagement_id=1)
        path_only = [f for f in self.findings if isinstance(f, Path)]
        DefectDojo().process_findings(self.execution, path_only)
        self.assertIsNone(self.execution.defectdojo_test_id)

    @mock.patch("platforms.defectdojo.integrations.DefectDojo.is_enabled", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.is_available", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo._import_or_reimport_scan", import_scan)
    def test_import(self) -> None:
        DefectDojoSync.objects.create(project=self.project, product_id=1, engagement_id=1)
        self.execution.configuration = Configuration.objects.get(pk=15)
        DefectDojo().process_findings(self.execution, self.findings)
        self.assertEqual(1, self.execution.defectdojo_test_id)

    @mock.patch("platforms.defectdojo.integrations.DefectDojo.is_enabled", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.is_available", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo._get_test_type", return_test_type)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo._get_test", return_test)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo._import_or_reimport_scan", import_scan)
    def test_reimport(self) -> None:
        DefectDojoSync.objects.create(project=self.project, product_id=1, engagement_id=1, reimport=True)
        self.execution.output_file = self.data_dir / "reports" / "nmap" / "enumeration-vulners.xml"
        DefectDojo().process_findings(self.execution, self.findings)
        self.assertEqual(1, self.execution.defectdojo_test_id)

    def _test_is_available_and_exists(self, expected: bool) -> None:
        settings = DefectDojoSettings.objects.first()
        settings.server = "http://localhost:8080"
        settings.secret = "fake-token"
        settings.save(update_fields=["server", "_api_token"])
        client = DefectDojo()
        self.assertEqual(expected, client.is_available())
        self.assertEqual(expected, client.exists("product-types", 1)[1])

    @mock.patch("platforms.defectdojo.integrations.DefectDojo._request", return_true)
    def test_is_available_and_exists(self) -> None:
        self._test_is_available_and_exists(True)

    @mock.patch("platforms.defectdojo.integrations.DefectDojo._request", exception)
    def test_is_not_available_and_does_not_exist(self) -> None:
        self._test_is_available_and_exists(False)

    @mock.patch("platforms.defectdojo.integrations.DefectDojo.is_enabled", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.is_available", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo._process_findings", exception)
    def test_handled_exception(self) -> None:
        DefectDojo().process_findings(self.execution, self.findings)
        self.assertTrue(True)


class DefectDojoSyncTest(ApiTest, TestCase):
    endpoint = "/api/defectdojo/sync/"
    expected_string = "Project 1 - 1 - 1"
    data = [SetupProject(targets_and_tasks=0)]
    cases = [
        PostApiTestCase(["admin2", "auditor2", Role.READER], 403, sync),
        PostApiTestCase(["auditor1"], data=sync, expected={"id": 1, **sync}),
        PostApiTestCase(["admin1"], 400, data=sync),
        ApiTestCase(["members"], expected={"id": 1, "defectdojo_sync": {"id": 1, **sync}}, endpoint="/api/projects/1/"),
        DeleteApiTestCase([Role.READER], 403, endpoint="1/"),
        DeleteApiTestCase(["admin2", "auditor2"], 404, endpoint="1"),
        DeleteApiTestCase(["admin1"], endpoint="1"),
        ApiTestCase(["members"], expected={"id": 1, "defectdojo_sync": None}, endpoint="/api/projects/1/"),
        PostApiTestCase(["admin1"], data=sync_no_engagement, expected={"id": 2, **sync_no_engagement}),
        ApiTestCase(
            ["members"],
            expected={"id": 1, "defectdojo_sync": {"id": 2, **sync_no_engagement}},
            endpoint="/api/projects/1/",
        ),
        DeleteApiTestCase(["auditor1"], endpoint="2"),
        ApiTestCase(["members"], expected={"id": 1, "defectdojo_sync": None}, endpoint="/api/projects/1/"),
    ]

    @mock.patch("platforms.defectdojo.integrations.DefectDojo.is_available", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.exists", get_engagement)
    def test_cases(self) -> None:
        super().test_cases()

    @mock.patch("platforms.defectdojo.integrations.DefectDojo.is_available", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.exists", get_engagement_other_product)
    def test_engagement_from_another_product_is_rejected(self) -> None:
        PostApiTestCase(["admin1"], 400, data=sync).test_case(0, self, self.endpoint)

    @mock.patch("platforms.defectdojo.integrations.DefectDojo.is_available", return_false)
    def test_not_available_is_rejected(self) -> None:
        PostApiTestCase(["admin1"], 400, data=sync).test_case(0, self, self.endpoint)

    @mock.patch("platforms.defectdojo.integrations.DefectDojo.is_available", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.exists", missing)
    def test_missing_product_is_rejected(self) -> None:
        PostApiTestCase(["admin1"], 400, data=sync).test_case(0, self, self.endpoint)

    @mock.patch("platforms.defectdojo.integrations.DefectDojo.is_available", return_true)
    @mock.patch("platforms.defectdojo.integrations.DefectDojo.exists", product_exists_but_engagement_missing)
    def test_missing_engagement_is_rejected(self) -> None:
        PostApiTestCase(["admin1"], 400, data=sync).test_case(0, self, self.endpoint)

    @cached_property
    def object(self) -> DefectDojoSync:
        return DefectDojoSync.objects.create(**{**sync, "project": self.project})


class DefectDojoTargetSyncTest(ApiTest, TestCase):
    expected_string = "Project 1 - 1 - 10.10.10.10 - 1"
    data = [SetupProject(executions_per_task=0)]

    @cached_property
    def object(self) -> DefectDojoTargetSync:
        defectdojo_sync = DefectDojoSync.objects.create(**{**sync_no_engagement, "project": self.project})
        return DefectDojoTargetSync.objects.create(defectdojo_sync=defectdojo_sync, target=self.target, engagement_id=1)


settings = {
    "server": None,
    "api_token": None,
    "tls_validation": True,
    "tag": "rekono",
}
new_settings = {
    "server": "https://defectdojo.rekono.dev/api/v2/",
    "api_token": "any_valid_defectdojo_token",
    "tls_validation": True,
    "tag": "rekono",
}
invalid_settings = {
    "server": "invalid server",
    "api_token": "invalid;token",
    "tls_validation": True,
    "tag": "rek;ono",
}


class DefectDojoSettingsTest(ApiTestNoData, TestCase):
    endpoint = "/api/defectdojo/settings/1/"
    expected_string = "DefectDojoSettings"
    cases = [
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], expected={"id": 1, **settings}),
        PutApiTestCase([Role.AUDITOR, Role.READER], 403, data=new_settings),
        PutApiTestCase([Role.ADMIN], 400, data=invalid_settings),
        PutApiTestCase(
            [Role.ADMIN],
            data=new_settings,
            expected={
                "id": 1,
                **new_settings,
                "server": new_settings["server"].replace("/api/v2/", ""),
                "api_token": "*" * len(str(new_settings.get("api_token", ""))),
                "is_available": False,
            },
        ),
        ApiTestCase(
            [Role.ADMIN, Role.AUDITOR, Role.READER],
            expected={
                "id": 1,
                **new_settings,
                "server": new_settings["server"].replace("/api/v2/", ""),
                "api_token": "*" * len(str(new_settings.get("api_token", ""))),
                "is_available": False,
            },
        ),
    ]

    @cached_property
    def object(self) -> DefectDojoSettings:
        return DefectDojoSettings.objects.get(pk=1)
