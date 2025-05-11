from typing import Any, Optional
from unittest import mock

from findings.enums import Severity
from findings.models import Vulnerability
from platforms.nvdnist.integrations import NvdNist
from platforms.nvdnist.models import NvdNistSettings
from tests.cases import ApiTestCase
from tests.framework import ApiTest, RekonoTest

success = {
    "vulnerabilities": [
        {
            "cve": {
                "descriptions": [{"lang": "en", "value": "description"}],
                "weaknesses": [
                    {
                        "type": "Primary",
                        "description": [{"lang": "en", "value": "CWE-200"}],
                    },
                    {
                        "type": "Secondary",
                        "description": [{"lang": "en", "value": "CWE-300"}],
                    },
                ],
                "metrics": {},
            }
        }
    ]
}


def _success(impact_value: dict[str, Any]) -> dict[str, Any]:
    success["vulnerabilities"][0]["cve"]["metrics"] = impact_value
    return success


def success_cvss_3(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return _success({"cvssMetricV31": [{"type": "Primary", "cvssData": {"baseScore": 9}}]})


def success_cvss_2(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return _success({"cvssMetricV2": [{"type": "Primary", "cvssData": {"baseScore": 8}}]})


def not_found(*args: Any, **kwargs: Any) -> dict:
    raise Exception("CVE not found")


class NvdNistTest(RekonoTest):
    def setUp(self) -> None:
        super().setUp()
        self._setup_tasks_and_executions()
        self.vulnerability = Vulnerability.objects.create(
            name="test", description="test", cve="CVE-2023-1111", severity=Severity.LOW
        )
        self.vulnerability.executions.add(self.execution3)
        self.nvdnist = NvdNist()

    def _test(
        self,
        severity: Severity,
        reference: Optional[str] = None,
        cwe: Optional[str] = "CWE-200",
        description: str = "description",
    ) -> None:
        self.nvdnist.process_findings(self.execution3, [self.vulnerability])
        self.assertEqual(reference, self.vulnerability.reference)
        self.assertEqual(cwe, self.vulnerability.cwe)
        self.assertEqual(description, self.vulnerability.description)
        self.assertEqual(severity, self.vulnerability.severity)

    @mock.patch("platforms.nvdnist.integrations.NvdNist._request", success_cvss_3)
    def test_integration_cvss_3(self) -> None:
        self._test(
            Severity.CRITICAL,
            self.nvdnist.reference.format(cve=self.vulnerability.cve),
        )

    @mock.patch("platforms.nvdnist.integrations.NvdNist._request", success_cvss_2)
    def test_integration_cvss_2(self) -> None:
        self._test(Severity.HIGH, self.nvdnist.reference.format(cve=self.vulnerability.cve))

    @mock.patch("platforms.nvdnist.integrations.NvdNist._request", not_found)
    def test_integration_not_found(self) -> None:
        self._test(Severity.LOW, None, None, "test")


new_settings = {"api_token": "nvd-nist-token"}
invalid_settings = {"api_token": "token" * 50}


class NvdNistSettingsTest(ApiTest):
    endpoint = "/api/nvdnist/1/"
    expected_str = "NVD NIST"
    cases = [
        ApiTestCase(["auditor1", "auditor2", "reader1", "reader2"], "get", 403),
        ApiTestCase(
            ["admin1", "admin2"],
            "get",
            200,
            expected={"id": 1, "api_token": None},
        ),
        ApiTestCase(["auditor1", "auditor2", "reader1", "reader2"], "put", 403, new_settings),
        # ApiTestCase(["admin1", "admin2"], "put", 400, invalid_settings),
        ApiTestCase(
            ["admin1", "admin2"],
            "put",
            200,
            new_settings,
            expected={
                "id": 1,
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
                "api_token": "*" * len(str(new_settings.get("api_token", ""))),
                "is_available": False,
            },
        ),
    ]

    def _get_object(self) -> Any:
        return NvdNistSettings.objects.first()
