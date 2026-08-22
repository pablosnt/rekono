from typing import Any
from unittest import mock

from django.test import TestCase

from findings.enums import Severity
from findings.models import Vulnerability
from platforms.euvd import EUVD
from tests.framework import BaseTest
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types

_CVE = "CVE-2021-44228"

data = {
    "id": "EUVD-2024-46955",
    "aliases": f"{_CVE}\nCVE-2021-45046",
    "description": "Remote code execution in Apache Log4j2 via JNDI lookup",
    "baseScore": 10.0,
    "baseScoreVector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
    "baseScoreVersion": "3.1",
    "epss": 0.97543,
    "enisaIdProduct": [{"id": "cpe:2.3:a:apache:log4j:*:*:*:*:*:*:*:*"}],
}

_euvd_item_no_match = {
    "id": "EUVD-2024-00001",
    "aliases": "CVE-2021-99999",
    "description": "Unrelated vulnerability",
    "baseScore": 5.0,
    "enisaIdProduct": [],
}


def _mock_request_success(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"items": [data]}


def _mock_request_no_match(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"items": [_euvd_item_no_match]}


class EuvdTest(BaseTest, TestCase):
    data = [SetupProject()]

    def setUp(self) -> None:
        super().setUp()
        self.vulnerability = Vulnerability.objects.create(
            name="test", description="test", cve=_CVE, severity=Severity.LOW
        )
        self.vulnerability.executions.add(self.execution)
        self.euvd = EUVD()

    @mock.patch("platforms.euvd.EUVD._request", _mock_request_success)
    def test_enrichment(self) -> None:
        # Retrieval
        enrichment = self.euvd.get_cve(_CVE)
        self.assertIsNotNone(enrichment)
        self.assertEqual(data["id"], enrichment.name)
        self.assertEqual(data["description"], enrichment.description)
        self.assertEqual(data["baseScore"], enrichment.cvss_base_score)
        self.assertEqual(data["baseScoreVector"], enrichment.cvss_vector)
        self.assertEqual(data["baseScoreVersion"], enrichment.cvss_version)
        self.assertIsNone(enrichment.cwes)
        self.assertEqual(data["id"], enrichment.euvd_id)
        self.assertEqual(data["epss"], enrichment.epss_score)
        self.assertIsNone(enrichment.epss_percentile)
        self.assertEqual([data["enisaIdProduct"][0]["id"]], enrichment.technologies)
        self.assertEqual(self.euvd.reference.format(euvd=data["id"]), enrichment.reference)
        self.assertIsNone(enrichment.status)

        # Quality Score
        self.assertEqual(8, self.euvd.cve_quality_score(enrichment))

        # Save
        self.euvd.save(self.vulnerability, enrichment)
        vuln = Vulnerability.objects.get(pk=self.vulnerability.pk)
        self.assertEqual(Severity.CRITICAL, vuln.severity)
        self.assertEqual(enrichment.name, vuln.name)
        self.assertEqual(enrichment.description, vuln.description)
        self.assertEqual(enrichment.cvss_base_score, vuln.cvss_base_score)
        self.assertEqual(enrichment.cvss_vector, vuln.cvss_vector)
        self.assertEqual(enrichment.cvss_version, vuln.cvss_version)
        self.assertEqual([], vuln.cwes)
        self.assertEqual(data["id"], vuln.euvd_id)
        self.assertEqual(enrichment.epss_score, vuln.epss_score)
        self.assertIsNone(vuln.epss_percentile)
        self.assertEqual(enrichment.reference, vuln.reference)

    @mock.patch("platforms.euvd.EUVD._request", _mock_request_success)
    def test_is_available(self) -> None:
        self.assertTrue(self.euvd.is_available())

    @mock.patch("platforms.euvd.EUVD._request", _mock_request_no_match)
    def test_is_not_available(self) -> None:
        self.assertFalse(self.euvd.is_available())
        self.assertIsNone(self.euvd.get_cve(_CVE))

    def test_no_data(self) -> None:
        self.assertIsNone(self.euvd._parse_cve(_CVE, []))
