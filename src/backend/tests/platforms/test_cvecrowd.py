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
        Alert.objects.create(
            project=self.execution3.task.target.project,
            item=AlertItem.CVE,
            mode=AlertMode.MONITOR,
            enabled=True,
        )
        self.settings = CVECrowdSettings.objects.first()
        self.settings.secret = "fake-token"
        self.settings.save(update_fields=["_api_token"])
        self.cvecrowd = CVECrowd()

    @mock.patch("platforms.cvecrowd.integrations.CVECrowd._request", success)
    def test_process_findings(self) -> None:
        self.cvecrowd.process_findings(
            self.execution3, [self.trending, self.not_trending]
        )
        self.assertTrue(self.trending.trending)
        self.assertFalse(self.not_trending.trending)

    @mock.patch(
        "platforms.cvecrowd.integrations.CVECrowd._request", lambda *args, **kwargs: []
    )
    def test_process_findings_not_found(self) -> None:
        self.cvecrowd.process_findings(
            self.execution3, [self.trending, self.not_trending]
        )
        self.assertFalse(self.trending.trending)
        self.assertFalse(self.not_trending.trending)

    @mock.patch("platforms.cvecrowd.integrations.CVECrowd._request", success)
    def test_monitor(self) -> None:
        CVECrowd.monitor()
        for vulnerability, trending in [
            (self.trending, True),
            (self.not_trending, False),
        ]:
            vulnerability = Vulnerability.objects.get(pk=vulnerability.id)
            self.assertEquals(trending, vulnerability.trending)


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
