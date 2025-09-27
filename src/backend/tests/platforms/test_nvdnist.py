from functools import cached_property
from typing import Any
from unittest import mock

from django.test import TestCase

from findings.enums import Severity
from findings.models import Vulnerability
from platforms.nvdnist.integrations import NvdNist
from platforms.nvdnist.models import NvdNistSettings
from security.authorization.roles import Role
from tests.framework import ApiTestNoData, BaseTest
from tests.framework.cases import ApiTestCase, PutApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types

data = {
    "vulnerabilities": [
        {
            "cve": {
                "descriptions": [{"lang": "en", "value": "description"}],
                "weaknesses": [
                    {"type": "Whatever", "description": [{"lang": "en", "value": "CWE-100"}]},
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


def success_empty(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"vulnerabilities": []}


def not_found(*args: Any, **kwargs: Any) -> dict:
    raise Exception("CVE not found")


class NvdNistTest(BaseTest, TestCase):
    data = [SetupProject()]

    def setUp(self) -> None:
        super().setUp()
        self.vulnerability = Vulnerability.objects.create(
            name="test", description="test", cve="CVE-2023-1111", severity=Severity.LOW
        )
        self.vulnerability.executions.add(self.execution)
        self.settings = NvdNistSettings.objects.first()
        self.settings.secret = "fake-token"
        self.settings.save(update_fields=["_api_token"])
        self.nvdnist = NvdNist()

    def _test(
        self,
        severity: Severity,
        reference: str | None = None,
        cwe: str | None = "CWE-200",
        description: str = "description",
    ) -> None:
        self.nvdnist.process_finding(self.execution, self.vulnerability)
        self.assertEqual(reference, self.vulnerability.reference)
        self.assertEqual(cwe, self.vulnerability.cwe)
        self.assertEqual(description, self.vulnerability.description)
        self.assertEqual(severity, self.vulnerability.severity)

    @mock.patch("platforms.nvdnist.integrations.NvdNist._request", success_cvss_3)
    def test_integration_cvss_3(self) -> None:
        self._test(Severity.CRITICAL, self.nvdnist.reference.format(cve=self.vulnerability.cve))

    @mock.patch("platforms.nvdnist.integrations.NvdNist._request", success_cvss_2)
    def test_integration_cvss_2(self) -> None:
        self.settings.secret = None
        self.settings.save(update_fields=["_api_token"])
        self._test(Severity.HIGH, self.nvdnist.reference.format(cve=self.vulnerability.cve))

    @mock.patch("platforms.nvdnist.integrations.NvdNist._request", not_found)
    def test_integration_not_found(self) -> None:
        self._test(Severity.LOW, None, None, "test")

    @mock.patch("platforms.nvdnist.integrations.NvdNist._request", success_empty)
    def test_integration_empty(self) -> None:
        self._test(Severity.LOW, None, None, "test")

    @mock.patch("platforms.nvdnist.integrations.NvdNist._request", success_cvss_3)
    def test_is_api_token_available(self) -> None:
        self.assertTrue(self.nvdnist.is_api_token_available)

    @mock.patch("platforms.nvdnist.integrations.NvdNist._request", success_cvss_3)
    def test_is_api_token_not_available_1(self) -> None:
        self.settings.secret = None
        self.settings.save(update_fields=["_api_token"])
        self.assertFalse(self.nvdnist.is_api_token_available)

    @mock.patch("platforms.nvdnist.integrations.NvdNist._request", not_found)
    def test_is_api_token_not_available_2(self) -> None:
        self.assertFalse(self.nvdnist.is_api_token_available)


new_settings = {"api_token": "nvd-nist-token"}
invalid_settings = {"api_token": "a" * 51}


class NvdNistSettingsTest(ApiTestNoData, TestCase):
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
