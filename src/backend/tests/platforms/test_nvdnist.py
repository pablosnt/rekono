from functools import cached_property
from typing import Any
from unittest import mock

from findings.enums import Severity
from findings.models import Vulnerability
from platforms.nvdnist.integrations import NvdNist
from platforms.nvdnist.models import NvdNistSettings
from security.authorization.roles import Role
from tests.framework import ApiTest, BaseTest
from tests.framework.cases import ApiTestCase, PutApiTestCase

# pytype: disable=wrong-arg-types

data = {
    "vulnerabilities": [
        {
            "cve": {
                "descriptions": [{"lang": "en", "value": "description"}],
                "weaknesses": [
                    {"type": "Primary", "description": [{"lang": "en", "value": "CWE-200"}]},
                    {"type": "Secondary", "description": [{"lang": "en", "value": "CWE-300"}]},
                ],
                "metrics": {},
            }
        }
    ]
}


def _success(impact_value: dict[str, Any]) -> dict[str, Any]:
    data["vulnerabilities"][0]["cve"]["metrics"] = impact_value
    return data


def success_cvss_3(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return _success({"cvssMetricV31": [{"type": "Primary", "cvssData": {"baseScore": 9}}]})


def success_cvss_2(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return _success({"cvssMetricV2": [{"type": "Primary", "cvssData": {"baseScore": 8}}]})


def not_found(*args: Any, **kwargs: Any) -> dict:
    raise Exception("CVE not found")


class NvdNistTest(BaseTest):
    setup_entities = ["executions"]

    def setUp(self) -> None:
        super().setUp()
        self.vulnerability = Vulnerability.objects.create(
            name="test", description="test", cve="CVE-2023-1111", severity=Severity.LOW
        )
        self.vulnerability.executions.add(self.selected_execution)
        self.nvdnist = NvdNist()

    def _test(
        self,
        severity: Severity,
        reference: str | None = None,
        cwe: str | None = "CWE-200",
        description: str = "description",
    ) -> None:
        self.nvdnist.process_finding(self.selected_execution, self.vulnerability)
        self.assertEqual(reference, self.vulnerability.reference)
        self.assertEqual(cwe, self.vulnerability.cwe)
        self.assertEqual(description, self.vulnerability.description)
        self.assertEqual(severity, self.vulnerability.severity)

    @mock.patch("platforms.nvdnist.integrations.NvdNist._request", success_cvss_3)
    def test_integration_cvss_3(self) -> None:
        self._test(Severity.CRITICAL, self.nvdnist.reference.format(cve=self.vulnerability.cve))

    @mock.patch("platforms.nvdnist.integrations.NvdNist._request", success_cvss_2)
    def test_integration_cvss_2(self) -> None:
        self._test(Severity.HIGH, self.nvdnist.reference.format(cve=self.vulnerability.cve))

    @mock.patch("platforms.nvdnist.integrations.NvdNist._request", not_found)
    def test_integration_not_found(self) -> None:
        self._test(Severity.LOW, None, None, "test")


new_settings = {"api_token": "nvd-nist-token"}
# TODO: settings must be invalid from 50 characters in the api_token
# However, the error is not triggered until it reaches 500 length
invalid_settings = {"api_token": "a" * 600}


class NvdNistSettingsTest(ApiTest):
    endpoint = "/api/nvdnist/1/"
    expected_string = "NVD NIST"
    cases = [
        ApiTestCase([Role.AUDITOR, Role.READER], 403),
        ApiTestCase([Role.ADMIN], expected={"id": 1, "api_token": None}),
        PutApiTestCase([Role.AUDITOR, Role.READER], 403, new_settings),
        PutApiTestCase([Role.ADMIN], 400, invalid_settings),
        PutApiTestCase(
            [Role.ADMIN],
            data=new_settings,
            expected={"id": 1, "api_token": "*" * len(str(new_settings.get("api_token", ""))), "is_available": False},
        ),
        ApiTestCase(
            [Role.ADMIN],
            expected={"id": 1, "api_token": "*" * len(str(new_settings.get("api_token", ""))), "is_available": False},
        ),
    ]

    @cached_property
    def object(self) -> NvdNistSettings:
        return NvdNistSettings.objects.first()
