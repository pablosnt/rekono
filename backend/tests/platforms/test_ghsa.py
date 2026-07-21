from typing import Any
from unittest import mock

from django.test import TestCase

from findings.enums import Severity
from findings.models import Vulnerability
from platforms.ghsa import GHSA
from tests.framework import BaseTest
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types

data = {
    "ghsa_id": "GHSA-jfh8-c2jp-hdp3",
    "summary": "Critical RCE in Apache Log4j",
    "description": "Remote code execution vulnerability in Apache Log4j2 via JNDI lookup",
    "cwes": [{"cwe_id": "CWE-400"}, {"cwe_id": "CWE-917"}],
    "cvss_severities": {
        "cvss_v4": {
            "score": 9.3,
            "vector_string": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N",
        },
        "cvss_v3": {
            "score": 10.0,
            "vector_string": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
        },
    },
    "epss": {"percentage": 0.97543, "percentile": 0.999},
    "vulnerabilities": [{"package": {"name": "log4j-core"}}],
    "html_url": "https://github.com/advisories/GHSA-jfh8-c2jp-hdp3",
    "type": "reviewed",
}


def _mock_request_success(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    return [data]


def _mock_request_unreviewed(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    return [{**data, "type": "unreviewed"}]


def _mock_request_empty(*args: Any, **kwargs: Any) -> list:
    return []


class GhsaTest(BaseTest, TestCase):
    data = [SetupProject()]

    def setUp(self) -> None:
        super().setUp()
        self.vulnerability = Vulnerability.objects.create(
            name="test", description="test", cve="CVE-2021-44228", severity=Severity.LOW
        )
        self.vulnerability.executions.add(self.execution)
        self.ghsa = GHSA()

    @mock.patch("platforms.ghsa.GHSA._request", _mock_request_success)
    def test_enrichement(self) -> None:
        # Retrieval
        enrichment = self.ghsa.get_cve(self.vulnerability.cve)
        self.assertIsNotNone(enrichment)
        self.assertEqual(data["summary"], enrichment.name)
        self.assertEqual(data["description"], enrichment.description)
        self.assertEqual(data["cvss_severities"]["cvss_v4"]["score"], enrichment.cvss_base_score)
        self.assertEqual(data["cvss_severities"]["cvss_v4"]["vector_string"], enrichment.cvss_vector)
        self.assertEqual("4.0", enrichment.cvss_version)
        self.assertEqual(["CWE-400", "CWE-917"], enrichment.cwes)
        self.assertEqual(data["ghsa_id"], enrichment.ghsa_id)
        self.assertEqual(data["epss"]["percentage"] * 100, enrichment.epss_score)
        self.assertEqual(data["epss"]["percentile"] * 100, enrichment.epss_percentile)
        self.assertEqual([data["vulnerabilities"][0]["package"]["name"]], enrichment.technologies)
        self.assertEqual(data["html_url"], enrichment.reference)
        self.assertEqual(data["type"], enrichment.status)

        # Quality Score
        self.assertEqual(11, self.ghsa.cve_quality_score(enrichment))

        # Save
        self.ghsa.save(self.vulnerability, enrichment)
        vuln = Vulnerability.objects.get(pk=self.vulnerability.pk)
        self.assertEqual(Severity.CRITICAL, vuln.severity)
        self.assertEqual(enrichment.name, vuln.name)
        self.assertEqual(enrichment.description, vuln.description)
        self.assertEqual(enrichment.cvss_base_score, vuln.cvss_base_score)
        self.assertEqual(enrichment.cvss_vector, vuln.cvss_vector)
        self.assertEqual(enrichment.cvss_version, vuln.cvss_version)
        self.assertEqual(enrichment.cwes, vuln.cwes)
        self.assertEqual(enrichment.ghsa_id, vuln.ghsa_id)
        self.assertEqual(enrichment.epss_score, vuln.epss_score)
        self.assertEqual(enrichment.epss_percentile, vuln.epss_percentile)
        self.assertEqual(enrichment.reference, vuln.reference)

    @mock.patch("platforms.ghsa.GHSA._request", _mock_request_unreviewed)
    def test_unreviewed(self) -> None:
        enrichment = self.ghsa.get_cve(self.vulnerability.cve)
        self.assertEqual(0, self.ghsa.cve_quality_score(enrichment))

    @mock.patch("platforms.ghsa.GHSA._request", _mock_request_success)
    def test_is_available(self) -> None:
        self.assertTrue(self.ghsa.is_available())

    @mock.patch("platforms.ghsa.GHSA._request", _mock_request_empty)
    def test_is_not_available(self) -> None:
        self.assertFalse(self.ghsa.is_available())
        self.assertIsNone(self.ghsa.get_cve(self.vulnerability.cve))

    def test_no_data(self) -> None:
        self.assertIsNone(self.ghsa._parse_cve("CVE-2021-44228", {}))

    def test_parse_cve_skips_zero_cvss_score(self) -> None:
        enrichment = self.ghsa._parse_cve(
            "CVE-2021-44228",
            [
                {
                    **data,
                    "cvss_severities": {
                        # Version 4 has no score, so it must be skipped in favor of version 3
                        "cvss_v4": {"score": 0, "vector_string": ""},
                        "cvss_v3": {"score": 10.0, "vector_string": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H"},
                    },
                }
            ],
        )
        self.assertEqual(10.0, enrichment.cvss_base_score)
        self.assertEqual("3.1", enrichment.cvss_version)
