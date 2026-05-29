from typing import Any
from unittest import mock

from django.test import TestCase

from findings.enums import Severity
from findings.models import Vulnerability
from platforms.osv import OSV
from tests.framework import BaseTest
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types

data = {
    "id": "CVE-2021-44228",
    "summary": "Remote code execution in Apache Log4j2",
    "details": "Apache Log4j2 does not protect against attacker-controlled LDAP via JNDI lookup",
    "severity": [{"type": "CVSS_V3", "score": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H"}],
    "affected": [{"package": {"purl": "pkg:maven/org.apache.logging.log4j/log4j-core", "name": "log4j-core"}}],
}


def _mock_request_cvss3(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return data


def _mock_request_cvss2(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {**data, "severity": [{"type": "CVSS_V2", "score": "AV:N/AC:L/Au:N/C:C/I:C/A:C"}]}


def _mock_request_empty(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {}


class OsvTest(BaseTest, TestCase):
    data = [SetupProject()]

    def setUp(self) -> None:
        super().setUp()
        self.vulnerability = Vulnerability.objects.create(
            name="test", description="test", cve=data["id"], severity=Severity.LOW
        )
        self.vulnerability.executions.add(self.execution)
        self.osv = OSV()

    @mock.patch("platforms.osv.OSV._request", _mock_request_cvss3)
    def test_enrichment(self) -> None:
        # Retrieval
        enrichment = self.osv.get_cve(self.vulnerability.cve)
        self.assertIsNotNone(enrichment)
        self.assertEqual(data["summary"], enrichment.name)
        self.assertEqual(data["details"], enrichment.description)
        self.assertIsNone(enrichment.cwe)
        self.assertEqual(10.0, enrichment.cvss_base_score)
        self.assertEqual(data["severity"][0]["score"], enrichment.cvss_vector)
        self.assertEqual("3.1", enrichment.cvss_version)
        self.assertIsNone(enrichment.epss_score)
        self.assertIsNone(enrichment.epss_percentile)
        self.assertEqual([data["affected"][0]["package"]["purl"]], enrichment.technologies)
        self.assertEqual(self.osv.reference.format(cve=self.vulnerability.cve), enrichment.reference)
        self.assertIsNone(enrichment.status)

        # Quality Score
        self.assertEqual(7, self.osv.cve_quality_score(enrichment))

        # Save
        self.osv.save(self.vulnerability, enrichment)
        vuln = Vulnerability.objects.get(pk=self.vulnerability.pk)
        self.assertEqual(Severity.CRITICAL, vuln.severity)
        self.assertEqual(enrichment.name, vuln.name)
        self.assertEqual(enrichment.description, vuln.description)
        self.assertEqual(enrichment.cvss_base_score, vuln.cvss_base_score)
        self.assertEqual(enrichment.cvss_vector, vuln.cvss_vector)
        self.assertEqual(enrichment.cvss_version, vuln.cvss_version)
        self.assertIsNone(vuln.cwe)
        self.assertIsNone(vuln.epss_score)
        self.assertIsNone(vuln.epss_percentile)
        self.assertEqual(enrichment.reference, vuln.reference)

    @mock.patch("platforms.osv.OSV._request", _mock_request_cvss2)
    def test_get_cve_cvss2(self) -> None:
        self.assertEqual(5, self.osv.cve_quality_score(self.osv.get_cve(self.vulnerability.cve)))

    @mock.patch("platforms.osv.OSV._request", _mock_request_cvss3)
    def test_is_available(self) -> None:
        self.assertTrue(self.osv.is_available())

    @mock.patch("platforms.osv.OSV._request", _mock_request_empty)
    def test_is_not_available(self) -> None:
        self.assertFalse(self.osv.is_available())
        self.assertIsNone(self.osv.get_cve(self.vulnerability.cve))
