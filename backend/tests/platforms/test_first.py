from typing import Any
from unittest import mock

from django.test import TestCase

from findings.enums import Severity
from findings.models import Vulnerability
from platforms.first import First
from tests.framework import BaseTest
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types

data = {"cve": "CVE-2021-44228", "epss": "0.97565", "percentile": "0.99999", "date": "2023-03-03"}


def _mock_success(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"status": "OK", "data": [data]}


def _mock_not_found(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"status": "OK", "data": []}


class FirstTest(BaseTest, TestCase):
    data = [SetupProject()]

    def setUp(self) -> None:
        super().setUp()
        self.vulnerability = Vulnerability.objects.create(
            name="test", description="test", cve=data["cve"], severity=Severity.LOW
        )
        self.vulnerability.executions.add(self.execution)
        self.first = First()

    @mock.patch("platforms.first.First._request", _mock_success)
    def test_process_finding(self) -> None:
        self.first.process_finding(self.execution, self.vulnerability)
        vuln = Vulnerability.objects.get(pk=self.vulnerability.pk)
        self.assertAlmostEqual(float(data["epss"]) * 100, vuln.epss_score)
        self.assertAlmostEqual(float(data["percentile"]) * 100, vuln.epss_percentile)

    @mock.patch("platforms.first.First._request", _mock_success)
    def test_monitor(self) -> None:
        self.first.monitor()
        vuln = Vulnerability.objects.get(pk=self.vulnerability.pk)
        self.assertAlmostEqual(float(data["epss"]) * 100, vuln.epss_score)
        self.assertAlmostEqual(float(data["percentile"]) * 100, vuln.epss_percentile)

    @mock.patch("platforms.first.First._request", _mock_not_found)
    def test_not_found(self) -> None:
        self.assertFalse(self.first.is_available())

        self.first.process_finding(self.execution, self.vulnerability)
        vuln = Vulnerability.objects.get(pk=self.vulnerability.pk)
        self.assertIsNone(vuln.epss_score)
        self.assertIsNone(vuln.epss_percentile)

        self.first.monitor()
        vuln = Vulnerability.objects.get(pk=self.vulnerability.pk)
        self.assertIsNone(vuln.epss_score)
        self.assertIsNone(vuln.epss_percentile)

    @mock.patch("platforms.first.First._request", _mock_success)
    def test_is_available(self) -> None:
        self.assertTrue(self.first.is_available())
