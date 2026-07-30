from functools import cached_property
from typing import Any
from unittest import mock

from django.test import TestCase

from findings.models import Host
from integrations.models import Integration
from platforms.virustotal.integrations import VirusTotal
from platforms.virustotal.models import VirusTotalSettings
from security.authorization.roles import Role
from tests.framework import ApiTestNoData, BaseTest
from tests.framework.cases import ApiTestCase, PutApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types


def return_true(*args: Any, **kwargs: Any) -> bool:
    return True


def success(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"data": {"attributes": {"last_analysis_stats": {"harmless": 1}, "whois": "Admin: Me", "reputation": 1}}}


def exception(*args: Any, **kwargs: Any):
    raise Exception("test")


class VirusTotalTest(BaseTest, TestCase):
    data = [SetupProject()]

    def setUp(self) -> None:
        super().setUp()
        integration = Integration.objects.get(key="virustotal")
        integration.enabled = True
        integration.save(update_fields=["enabled"])
        self.settings = VirusTotalSettings.objects.first()
        self.settings.secret = "fake-token"
        self.settings.save(update_fields=["_api_token"])
        self.virustotal = VirusTotal()
        self.host.ip = "8.8.8.8"
        self.host.save(update_fields=["ip"])

    def _test_success(self) -> None:
        self.virustotal.process_findings(self.execution, [self.host])
        self.host = Host.objects.get(pk=self.host.id)
        self.assertEqual(1, self.host.reputation)
        self.assertEqual(0, self.host.malicious_analysis)
        self.assertEqual(0, self.host.suspicious_analysis)
        self.assertEqual(1, self.host.total_analysis)
        self.assertEqual("Admin: Me", self.host.whois)

    @mock.patch("platforms.virustotal.integrations.VirusTotal.is_available", return_true)
    @mock.patch("platforms.virustotal.integrations.VirusTotal._request", success)
    def test_process_findings(self) -> None:
        self._test_success()
        self.host.domain = "rekono.com"
        self.host.save(update_fields=["domain"])
        self._test_success()

    def _test_no_data(self) -> None:
        self.virustotal.process_findings(self.execution, [self.host])
        self.host = Host.objects.get(pk=self.host.id)
        self.assertIsNone(self.host.reputation)
        self.assertIsNone(self.host.malicious_analysis)
        self.assertIsNone(self.host.suspicious_analysis)
        self.assertIsNone(self.host.total_analysis)
        self.assertIsNone(self.host.whois)

    @mock.patch("platforms.virustotal.integrations.VirusTotal._request", exception)
    def test_process_findings_not_found(self) -> None:
        self._test_no_data()

    @mock.patch("platforms.virustotal.integrations.VirusTotal._request", success)
    def test_not_processable(self) -> None:
        self.host.ip = "10.10.10.10"
        self.host.save(update_fields=["ip"])
        self._test_no_data()

    @mock.patch("platforms.virustotal.integrations.VirusTotal.is_available", return_true)
    @mock.patch("platforms.virustotal.integrations.VirusTotal._request", success)
    def test_private_ip_with_domain_not_processed(self) -> None:
        self.host.ip = "10.10.10.10"
        self.host.domain = "internal.local"
        self.host.save(update_fields=["ip", "domain"])
        self._test_no_data()

    @mock.patch("platforms.virustotal.integrations.VirusTotal._request", success)
    def test_is_available(self) -> None:
        self.assertTrue(self.virustotal.live_is_available())

    @mock.patch("platforms.virustotal.integrations.VirusTotal._request", exception)
    def test_is_not_available(self) -> None:
        self.assertFalse(self.virustotal.live_is_available())

        self.settings.secret = None
        self.settings.save(update_fields=["_api_token"])
        self.assertFalse(self.virustotal.live_is_available())

    def test_cached_is_available(self) -> None:
        self.assertFalse(self.virustotal.is_available())

    @mock.patch("platforms.virustotal.integrations.VirusTotal._process_finding", exception)
    @mock.patch("platforms.virustotal.integrations.VirusTotal.is_available", return_true)
    def test_handled_exception(self) -> None:
        self.virustotal.process_findings(self.execution, [self.host])
        self.assertTrue(True)


new_settings = {"api_token": "cve-crowd-token"}
invalid_settings = {"api_token": "x" * 70}


class VirusTotalSettingsTest(ApiTestNoData, TestCase):
    endpoint = "/api/virustotal/1/"
    expected_string = "Virus Total"
    cases = [
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], expected={"id": 1, "api_token": None}),
        PutApiTestCase([Role.AUDITOR, Role.READER], 403, new_settings),
        PutApiTestCase([Role.ADMIN], 400, invalid_settings),
        PutApiTestCase(
            [Role.ADMIN],
            data=new_settings,
            expected={
                "id": 1,
                **new_settings,
                "api_token": "*" * len(str(new_settings.get("api_token", ""))),
                "is_available": False,
            },
        ),
        ApiTestCase(
            [Role.ADMIN, Role.AUDITOR, Role.READER],
            expected={
                "id": 1,
                **new_settings,
                "api_token": "*" * len(str(new_settings.get("api_token", ""))),
                "is_available": False,
            },
        ),
    ]

    @cached_property
    def object(self) -> VirusTotalSettings:
        return VirusTotalSettings.objects.first()
