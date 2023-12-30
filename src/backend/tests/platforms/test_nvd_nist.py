from typing import Any, Dict, Optional
from unittest import mock

from findings.enums import Severity
from findings.models import Vulnerability
from platforms.nvd_nist import NvdNist
from tests.framework import RekonoTest

success = {
    "result": {
        "CVE_Items": [
            {
                "cve": {
                    "description": {
                        "description_data": [{"lang": "en", "value": "description"}]
                    },
                    "problemtype": {
                        "problemtype_data": [{"description": [{"value": "CWE-200"}]}]
                    },
                }
            }
        ]
    }
}


def _success(impact_value: Dict[str, Any]) -> Dict[str, Any]:
    success["result"]["CVE_Items"][0]["impact"] = impact_value
    return success


def success_cvss_3(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    return _success(
        {
            "baseMetricV3": {"cvssV3": {"baseScore": 9}},
        }
    )


def success_cvss_2(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    return _success(
        {
            "baseMetricV2": {"cvssV2": {"baseScore": 8}},
        }
    )


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
        self.nvd_nist = NvdNist()

    def _test(
        self,
        severity: Severity,
        reference: Optional[str] = None,
        cwe: Optional[str] = "CWE-200",
        description: str = "description",
    ) -> None:
        self.nvd_nist.process_findings(self.execution3, [self.vulnerability])
        self.assertEqual(reference, self.vulnerability.reference)
        self.assertEqual(cwe, self.vulnerability.cwe)
        self.assertEqual(description, self.vulnerability.description)
        self.assertEqual(severity, self.vulnerability.severity)

    @mock.patch("platforms.nvd_nist.NvdNist._request", success_cvss_3)
    def test_integration_cvss_3(self) -> None:
        self._test(
            Severity.CRITICAL,
            self.nvd_nist.reference.format(cve=self.vulnerability.cve),
        )

    @mock.patch("platforms.nvd_nist.NvdNist._request", success_cvss_2)
    def test_integration_cvss_2(self) -> None:
        self._test(
            Severity.HIGH, self.nvd_nist.reference.format(cve=self.vulnerability.cve)
        )

    @mock.patch("platforms.nvd_nist.NvdNist._request", not_found)
    def test_integration_not_found(self) -> None:
        self._test(Severity.LOW, None, None, "test")
