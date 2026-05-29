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
    "cisaVulnerabilityName": "Log4Shell RCE",
    "vulnStatus": "Modified",
    "descriptions": [{"lang": "en", "value": "Remote code execution via JNDI lookup in Log4j2"}],
    "weaknesses": [
        {"type": "Primary", "description": [{"value": "CWE-917", "lang": "en"}]},
    ],
    "metrics": {
        "cvssMetricV31": [
            {
                "type": "Primary",
                "cvssData": {
                    "baseScore": 10.0,
                    "version": "3.1",
                    "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
                },
            }
        ]
    },
    "configurations": [{"nodes": [{"cpeMatch": [{"criteria": "cpe:2.3:a:apache:log4j:*:*:*:*:*:*:*:*"}]}]}],
}


def _mock_request_success(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"vulnerabilities": [{"cve": data}]}


def _mock_request_not_scheduled(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"vulnerabilities": [{"cve": {**data, "vulnStatus": "Deferred"}}]}


def _mock_request_empty(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"vulnerabilities": []}


class NvdNistTest(BaseTest, TestCase):
    data = [SetupProject()]

    def setUp(self) -> None:
        super().setUp()
        self.vulnerability = Vulnerability.objects.create(
            name="test", description="test", cve="CVE-2021-44228", severity=Severity.LOW
        )
        self.vulnerability.executions.add(self.execution)
        self.settings = NvdNistSettings.objects.first()
        self.settings.secret = "fake-token"
        self.settings.save(update_fields=["_api_token"])
        self.nvdnist = NvdNist()

    @mock.patch("platforms.nvdnist.integrations.NvdNist._request", _mock_request_success)
    def test_enrichment(self) -> None:
        # Retrieval
        enrichment = self.nvdnist.get_cve(self.vulnerability.cve)
        self.assertIsNotNone(enrichment)
        self.assertEqual(data["cisaVulnerabilityName"], enrichment.name)
        self.assertEqual(data["descriptions"][0]["value"], enrichment.description)
        self.assertEqual(data["weaknesses"][0]["description"][0]["value"], enrichment.cwe)
        self.assertEqual(data["metrics"]["cvssMetricV31"][0]["cvssData"]["baseScore"], enrichment.cvss_base_score)
        self.assertEqual(data["metrics"]["cvssMetricV31"][0]["cvssData"]["version"], enrichment.cvss_version)
        self.assertEqual(data["metrics"]["cvssMetricV31"][0]["cvssData"]["vectorString"], enrichment.cvss_vector)
        self.assertIsNone(enrichment.epss_score)
        self.assertIsNone(enrichment.epss_percentile)
        self.assertEqual([data["configurations"][0]["nodes"][0]["cpeMatch"][0]["criteria"]], enrichment.technologies)
        self.assertEqual(self.nvdnist.reference.format(cve=self.vulnerability.cve), enrichment.reference)
        self.assertEqual(data["vulnStatus"], enrichment.status)

        # Quality Score
        self.assertEqual(6, self.nvdnist.cve_quality_score(enrichment))

        # Save
        self.nvdnist.save(self.vulnerability, enrichment)
        vuln = Vulnerability.objects.get(pk=self.vulnerability.pk)
        self.assertEqual(Severity.CRITICAL, vuln.severity)
        self.assertEqual(enrichment.name, vuln.name)
        self.assertEqual(enrichment.description, vuln.description)
        self.assertEqual(enrichment.cvss_base_score, vuln.cvss_base_score)
        self.assertEqual(enrichment.cvss_vector, vuln.cvss_vector)
        self.assertEqual(enrichment.cvss_version, vuln.cvss_version)
        self.assertEqual(enrichment.cwe, vuln.cwe)
        self.assertIsNone(vuln.epss_score)
        self.assertIsNone(vuln.epss_percentile)
        self.assertEqual(enrichment.reference, vuln.reference)

    @mock.patch("platforms.nvdnist.integrations.NvdNist._request", _mock_request_not_scheduled)
    def test_not_scheduled(self) -> None:
        e = self.nvdnist.get_cve(self.vulnerability.cve)
        self.assertEqual("Deferred", e.status)
        self.assertEqual(0, self.nvdnist.cve_quality_score(e))

    @mock.patch("platforms.nvdnist.integrations.NvdNist._request", _mock_request_success)
    def test_is_available(self) -> None:
        self.assertTrue(self.nvdnist.is_available())

    @mock.patch("platforms.nvdnist.integrations.NvdNist._request", _mock_request_empty)
    def test_is_not_available(self) -> None:
        self.assertFalse(self.nvdnist.is_available())
        self.assertIsNone(self.nvdnist.get_cve(self.vulnerability.cve))


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
