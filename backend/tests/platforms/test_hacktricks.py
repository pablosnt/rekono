from typing import Any
from unittest import mock

from django.test import TestCase

from platforms.hacktricks import HackTricks
from tests.framework import BaseTest
from tests.framework.data import SetupProject

base_url = "https://book.hacktricks.wiki/en/"


def links(*args: Any, **kwargs: Any) -> list[str]:
    return [
        f"{base_url}pentesting-web/web-vulnerabilities-methodology.html",
        f"{base_url}network-services-pentesting/wordpress.html",
        f"{base_url}network-services-pentesting/pentesting-dns",
        f"{base_url}network-services-pentesting/pentesting-ssh",
    ]


class HackTricksTest(BaseTest, TestCase):
    data = [SetupProject()]

    def setUp(self):
        super().setUp()
        self.expected = {
            self.host: f"{base_url}linux-hardening/privilege-escalation/index.html",
            self.port: f"{base_url}pentesting-web/web-vulnerabilities-methodology.html",
            self.technology: f"{base_url}network-services-pentesting/wordpress.html",
            self.vulnerability: None,
            self.exploit: None,
        }

    @mock.patch("platforms.hacktricks.HackTricks._get_all_hacktricks_links", links)
    def _assert_links(self) -> None:
        self.client = HackTricks()
        self.client.process_findings(self.execution, list(self.expected.keys()))
        for finding, expected_link in self.expected.items():
            self.assertEqual(expected_link, finding.hacktricks_link)

    def test_integration_with_http_service(self) -> None:
        self._assert_links()

    def test_integration_with_dns_service(self) -> None:
        self.port.port = 53
        self.port.service = "domain"
        self.port.save(update_fields=["port", "service"])
        self.expected[self.port] = f"{base_url}network-services-pentesting/pentesting-dns"
        self._assert_links()

    def test_integration_with_ssh_service(self) -> None:
        self.port.port = 22
        self.port.service = "ssh"
        self.port.save(update_fields=["port", "service"])
        self.expected[self.port] = f"{base_url}network-services-pentesting/pentesting-ssh"
        self._assert_links()
