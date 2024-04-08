from typing import Any, List
from unittest import mock

from alerts.enums import AlertItem, AlertMode
from alerts.models import Alert
from findings.enums import Severity
from findings.models import Vulnerability
from platforms.cvecrowd.integrations import CVECrowd
from platforms.cvecrowd.models import CVECrowdSettings
from tests.cases import ApiTestCase
from tests.framework import ApiTest, RekonoTest


def success(*args: Any, **kwargs: Any) -> List[str]:
    return ["CVE-2020-1111", "CVE-2021-1112", "CVE-2022-1113"]


def not_found(*args: Any, **kwargs: Any) -> List[str]:
    return []


class CVECrowdTest(RekonoTest):
    def setUp(self) -> None:
        super().setUp()
        self._setup_tasks_and_executions()
        self.not_trending = Vulnerability.objects.create(
            name="not trending",
            description="not trending",
            cve="CVE-2023-9999",
            severity=Severity.LOW,
        )
        self.trending = Vulnerability.objects.create(
            name="trending",
            description="trending",
            cve="CVE-2022-1113",
            severity=Severity.HIGH,
        )
        self.not_trending.executions.add(self.execution3)
        self.trending.executions.add(self.execution3)
        self.settings = CVECrowdSettings.objects.first()
        self.settings.secret = "fake-token"
        self.settings.save(update_fields=["_api_token"])
        Alert.objects.create(
            project=self.execution3.task.target.project,
            item=AlertItem.CVE,
            mode=AlertMode.MONITOR,
            enabled=True,
        )
        self.cvecrowd = CVECrowd()

    def _verify_success(self) -> None:
        self.assertTrue(Vulnerability.objects.get(pk=self.trending.id).trending)
        self.assertFalse(Vulnerability.objects.get(pk=self.not_trending.id).trending)

    def _verify_error(self) -> None:
        self.assertFalse(Vulnerability.objects.get(pk=self.trending.id).trending)
        self.assertFalse(Vulnerability.objects.get(pk=self.not_trending.id).trending)

    @mock.patch("platforms.cvecrowd.integrations.CVECrowd._request", success)
    def test_process_findings(self) -> None:
        self.cvecrowd.process_findings(
            self.execution3, [self.trending, self.not_trending]
        )
        self._verify_success()

    @mock.patch("platforms.cvecrowd.integrations.CVECrowd._request", not_found)
    def test_process_findings_not_found(self) -> None:
        self.cvecrowd.process_findings(
            self.execution3, [self.trending, self.not_trending]
        )
        self._verify_error()

    @mock.patch("platforms.cvecrowd.integrations.CVECrowd._request", success)
    def test_process_findings_not_enabled(self) -> None:
        self.settings.execute_per_execution = False
        self.settings.save(update_fields=["execute_per_execution"])
        self.cvecrowd = CVECrowd()
        self.cvecrowd.process_findings(
            self.execution3, [self.trending, self.not_trending]
        )
        self._verify_error()

    @mock.patch("platforms.cvecrowd.integrations.CVECrowd._request", success)
    def test_monitor(self) -> None:
        self.cvecrowd.monitor()
        self._verify_success()

    @mock.patch("platforms.cvecrowd.integrations.CVECrowd._request", not_found)
    def test_monitor_not_found(self) -> None:
        self.cvecrowd.monitor()
        self._verify_error()


new_settings = {
    "api_token": "cve-crowd-token",
    "trending_span_days": 3,
    "execute_per_execution": False,
}
invalid_settings = {**new_settings, "trending_span_days": 10}


class CVECrowdSettingsTest(ApiTest):
    endpoint = "/api/cvecrowd/1/"
    expected_str = "CVE Crowd"
    cases = [
        ApiTestCase(["auditor1", "auditor2", "reader1", "reader2"], "get", 403),
        ApiTestCase(
            ["admin1", "admin2"],
            "get",
            200,
            expected={
                "id": 1,
                "api_token": None,
                "trending_span_days": 7,
                "execute_per_execution": True,
            },
        ),
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
                "api_token": "*" * len(str(new_settings.get("api_token", ""))),
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
                "api_token": "*" * len(str(new_settings.get("api_token", ""))),
                "is_available": False,
            },
        ),
    ]

    def _get_object(self) -> Any:
        return CVECrowdSettings.objects.first()
