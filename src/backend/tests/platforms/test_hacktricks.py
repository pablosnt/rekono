from typing import Any, Optional
from unittest import mock

from findings.framework.models import Finding
from platforms.hacktricks import HackTricks
from tests.framework import RekonoTest

base_url = "https://book.hacktricks.wiki/en/"


def links(*args: Any, **kwargs: Any) -> list[str]:
    return [
        f"{base_url}pentesting-web/web-vulnerabilities-methodology.html",
        f"{base_url}network-services-pentesting/wordpress.html",
        f"{base_url}network-services-pentesting/pentesting-dns",
        f"{base_url}network-services-pentesting/pentesting-ssh",
    ]


class HackTricksTest(RekonoTest):
    def setUp(self) -> None:
        super().setUp()
        self._setup_tasks_and_executions()
        self._setup_findings(self.execution1)

    @mock.patch("platforms.hacktricks.HackTricks._get_all_hacktricks_links", links)
    def _test_integration(self, expected: dict[Finding, Optional[str]]) -> None:
        client = HackTricks()
        client.process_findings(self.execution1, expected.keys())
        for finding, expected_link in expected.items():
            self.assertEqual(expected_link, finding.hacktricks_link)

    def _get_expected(self) -> dict[Finding, Optional[str]]:
        return {
            self.host: f"{base_url}linux-hardening/privilege-escalation/index.html",
            self.port: f"{base_url}pentesting-web/web-vulnerabilities-methodology.html",
            self.technology: f"{base_url}network-services-pentesting/wordpress",
            self.vulnerability: None,
            self.exploit: None,
        }

    def test_integration_with_http_service(self) -> None:
        self._test_integration(self._get_expected())

    def test_integration_with_dns_service(self) -> None:
        self.port.port = 53
        self.port.service = "domain"
        self.port.save(update_fields=["port", "service"])
        self._test_integration(
            {
                **self._get_expected(),
                self.port: f"{base_url}network-services-pentesting/pentesting-dns",
            }
        )

    def test_integration_with_ssh_service(self) -> None:
        self.port.port = 22
        self.port.service = "ssh"
        self.port.save(update_fields=["port", "service"])
        self._test_integration(
            {
                **self._get_expected(),
                self.port: f"{base_url}network-services-pentesting/pentesting-ssh",
            }
        )
