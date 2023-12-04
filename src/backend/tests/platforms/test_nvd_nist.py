from unittest import mock

from findings.enums import Severity
from findings.models import Vulnerability
from platforms.nvd_nist import NvdNist
from tests.framework import RekonoTest
from tests.platforms.mocks.nvd_nist import not_found, success_cvss_2, success_cvss_3


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
        reference: str = None,
        cwe: str = "CWE-200",
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
