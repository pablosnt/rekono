from functools import cached_property
from typing import Any
from unittest import mock

from django.test import TestCase

from findings.enums import Severity
from findings.models import Vulnerability
from platforms.vulncheck.integrations import VulnCheck
from platforms.vulncheck.models import VulnCheckSettings
from security.authorization.roles import Role
from tests.framework import ApiTestNoData, BaseTest
from tests.framework.cases import ApiTestCase, PutApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types

data = {
    "id": "CVE-2024-21762",
    "vulnStatus": "Analyzed",
    "descriptions": [
        {
            "lang": "en",
            "value": "A out-of-bounds write in Fortinet FortiOS allows attacker to execute unauthorized code",
        }
    ],
    "weaknesses": [
        {"type": "Secondary", "description": [{"value": "CWE-787", "lang": "en"}]},
    ],
    "metrics": {
        "cvssMetricV31": [
            {
                "source": "nvd@nist.gov",
                "type": "Primary",
                "cvssData": {
                    "version": "3.1",
                    "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                    "baseScore": 9.8,
                },
            }
        ]
    },
    "configurations": [{"nodes": [{"cpeMatch": [{"criteria": "cpe:2.3:o:fortinet:fortios:*:*:*:*:*:*:*:*"}]}]}],
    "vcVulnerableCPEs": [
        "cpe:2.3:o:fortinet:fortios:6.0.0:*:*:*:*:*:*:*",
        "cpe:2.3:o:fortinet:fortios:7.4.2:*:*:*:*:*:*:*",
    ],
}


def _mock_request_success(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"data": [data]}


def _mock_request_deferred(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"data": [{**data, "vulnStatus": "Deferred"}]}


def _mock_request_empty(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"data": []}


class VulnCheckTest(BaseTest, TestCase):
    data = [SetupProject()]

    def setUp(self) -> None:
        super().setUp()
        self.vulnerability = Vulnerability.objects.create(
            name="test", description="test", cve="CVE-2024-21762", severity=Severity.LOW
        )
        self.vulnerability.executions.add(self.execution)
        self.settings = VulnCheckSettings.objects.first()
        self.settings.secret = "fake-vulncheck-token"
        self.settings.save(update_fields=["_api_token"])
        self.vulncheck = VulnCheck()

    @mock.patch("platforms.vulncheck.integrations.VulnCheck._request", _mock_request_success)
    def test_enrichment(self) -> None:
        enrichment = self.vulncheck.get_cve(self.vulnerability.cve)
        self.assertIsNotNone(enrichment)
        self.assertEqual(data["id"], enrichment.name)
        self.assertEqual(data["descriptions"][0]["value"], enrichment.description)
        self.assertEqual([data["weaknesses"][0]["description"][0]["value"]], enrichment.cwes)
        self.assertEqual(data["metrics"]["cvssMetricV31"][0]["cvssData"]["baseScore"], enrichment.cvss_base_score)
        self.assertEqual(data["metrics"]["cvssMetricV31"][0]["cvssData"]["version"], enrichment.cvss_version)
        self.assertEqual(data["metrics"]["cvssMetricV31"][0]["cvssData"]["vectorString"], enrichment.cvss_vector)
        self.assertIsNone(enrichment.epss_score)
        self.assertIsNone(enrichment.epss_percentile)
        self.assertEqual(data["vcVulnerableCPEs"], enrichment.technologies)
        self.assertEqual(self.vulncheck.reference.format(cve=self.vulnerability.cve), enrichment.reference)
        self.assertEqual(data["vulnStatus"], enrichment.status)

        # Quality Score
        self.assertEqual(10, self.vulncheck.cve_quality_score(enrichment))

        # Save
        self.vulncheck.save(self.vulnerability, enrichment)
        vuln = Vulnerability.objects.get(pk=self.vulnerability.pk)
        self.assertEqual(Severity.CRITICAL, vuln.severity)
        self.assertEqual(enrichment.name, vuln.name)
        self.assertEqual(enrichment.description, vuln.description)
        self.assertEqual(enrichment.cvss_base_score, vuln.cvss_base_score)
        self.assertEqual(enrichment.cvss_vector, vuln.cvss_vector)
        self.assertEqual(enrichment.cvss_version, vuln.cvss_version)
        self.assertEqual(enrichment.cwes, vuln.cwes)
        self.assertIsNone(vuln.epss_score)
        self.assertIsNone(vuln.epss_percentile)
        self.assertEqual(enrichment.reference, vuln.reference)

    @mock.patch("platforms.vulncheck.integrations.VulnCheck._request", _mock_request_deferred)
    def test_deferred_quality_score(self) -> None:
        enrichment = self.vulncheck.get_cve(self.vulnerability.cve)
        self.assertEqual("Deferred", enrichment.status)
        self.assertEqual(0, self.vulncheck.cve_quality_score(enrichment))

    @mock.patch("platforms.vulncheck.integrations.VulnCheck._request", _mock_request_success)
    def test_is_available(self) -> None:
        self.assertTrue(self.vulncheck.is_available())

    @mock.patch("platforms.vulncheck.integrations.VulnCheck._request", _mock_request_empty)
    def test_is_not_available_empty_response(self) -> None:
        self.assertFalse(self.vulncheck.is_available())
        self.assertIsNone(self.vulncheck.get_cve(self.vulnerability.cve))

    def test_is_not_available_no_token(self) -> None:
        self.settings.secret = None
        self.settings.save(update_fields=["_api_token"])
        self.assertFalse(self.vulncheck.is_available())


new_settings = {"api_token": "vulncheck-api-token"}
invalid_settings = {"api_token": "a" * 201}


class VulnCheckSettingsTest(ApiTestNoData, TestCase):
    endpoint = "/api/vulncheck/1/"
    expected_string = "VulnCheck"
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
    def object(self) -> VulnCheckSettings:
        return VulnCheckSettings.objects.first()
