from functools import cached_property
from typing import Any
from unittest import mock

from django.test import TestCase

from alerts.enums import AlertItem
from alerts.models import Alert
from findings.enums import Severity
from findings.models import Vulnerability
from integrations.models import Integration
from platforms.cvecrowd.integrations import CveCrowd
from platforms.cvecrowd.models import CveCrowdSettings
from security.authorization.roles import Role
from tests.framework import ApiTestNoData, BaseTest
from tests.framework.cases import ApiTestCase, PutApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types


def success(*args: Any, **kwargs: Any) -> list[str]:
    return ["CVE-2020-1111", "CVE-2021-1112", "CVE-2022-1113"]


def not_found(*args: Any, **kwargs: Any) -> list[str]:
    return []


def exception(*args: Any, **kwargs: Any) -> list[str]:
    raise Exception("test")


class CveCrowdTest(BaseTest, TestCase):
    data = [SetupProject()]

    def setUp(self) -> None:
        super().setUp()
        self.not_trending = Vulnerability.objects.create(
            name="not trending", description="not trending", cve="CVE-2023-9999", severity=Severity.LOW
        )
        self.trending = Vulnerability.objects.create(
            name="trending", description="trending", cve="CVE-2022-1113", severity=Severity.HIGH
        )
        self.not_trending.executions.add(self.execution)
        self.trending.executions.add(self.execution)
        integration = Integration.objects.get(key="cvecrowd")
        integration.enabled = True
        integration.save(update_fields=["enabled"])
        self.settings = CveCrowdSettings.objects.first()
        self.settings.secret = "fake-token"
        self.settings.save(update_fields=["_api_token"])
        Alert.objects.create(project=self.project, item=AlertItem.TRENDING_CVE, value=str(True), enabled=True)
        self.cvecrowd = CveCrowd()

    @mock.patch("platforms.cvecrowd.integrations.CveCrowd._request", success)
    def test_process_findings(self) -> None:
        self.cvecrowd.process_findings(self.execution, [self.trending, self.not_trending])
        self.assertTrue(Vulnerability.objects.get(pk=self.trending.id).trending)
        self.assertFalse(Vulnerability.objects.get(pk=self.not_trending.id).trending)
        # Rerun to force cache usage
        CveCrowd().process_findings(self.execution, [self.trending, self.not_trending])

    @mock.patch("platforms.cvecrowd.integrations.CveCrowd._request", not_found)
    def test_process_findings_not_found(self) -> None:
        self.cvecrowd.process_findings(self.execution, [self.trending, self.not_trending])
        self.assertFalse(Vulnerability.objects.get(pk=self.trending.id).trending)
        self.assertFalse(Vulnerability.objects.get(pk=self.not_trending.id).trending)

    @mock.patch("platforms.cvecrowd.integrations.CveCrowd._request", success)
    def test_process_findings_not_enabled(self) -> None:
        self.settings.execute_per_execution = False
        self.settings.save(update_fields=["execute_per_execution"])
        self.cvecrowd = CveCrowd()
        self.cvecrowd.process_findings(self.execution, [self.trending, self.not_trending])
        self.assertFalse(Vulnerability.objects.get(pk=self.trending.id).trending)
        self.assertFalse(Vulnerability.objects.get(pk=self.not_trending.id).trending)

    @mock.patch("platforms.cvecrowd.integrations.CveCrowd._request", success)
    def test_monitor(self) -> None:
        self.cvecrowd.monitor()
        self.assertTrue(Vulnerability.objects.get(pk=self.trending.id).trending)
        self.assertFalse(Vulnerability.objects.get(pk=self.not_trending.id).trending)

    @mock.patch("platforms.cvecrowd.integrations.CveCrowd._request", not_found)
    def test_monitor_not_found(self) -> None:
        self.cvecrowd.monitor()
        self.assertFalse(Vulnerability.objects.get(pk=self.trending.id).trending)
        self.assertFalse(Vulnerability.objects.get(pk=self.not_trending.id).trending)

    @mock.patch("platforms.cvecrowd.integrations.CveCrowd._request", success)
    def test_is_available(self) -> None:
        self.assertTrue(self.cvecrowd.live_is_available())

    @mock.patch("platforms.cvecrowd.integrations.CveCrowd._request", not_found)
    def test_is_not_available_1(self) -> None:
        self.assertFalse(self.cvecrowd.live_is_available())

    @mock.patch("platforms.cvecrowd.integrations.CveCrowd._request", exception)
    def test_is_not_available_2(self) -> None:
        self.assertFalse(self.cvecrowd.live_is_available())

    def test_cached_is_available(self) -> None:
        self.assertFalse(self.cvecrowd.is_available())


new_settings = {"api_token": "cve-crowd-token", "trending_span_days": 7, "execute_per_execution": False}
invalid_settings = {**new_settings, "trending_span_days": 50}


class CveCrowdSettingsTest(ApiTestNoData, TestCase):
    endpoint = "/api/cvecrowd/1/"
    expected_string = "CVE Crowd"
    cases = [
        ApiTestCase([Role.AUDITOR, Role.READER], 403),
        ApiTestCase(
            [Role.ADMIN],
            expected={"id": 1, "api_token": None, "trending_span_days": 1, "execute_per_execution": True},
        ),
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
            [Role.ADMIN],
            expected={
                "id": 1,
                **new_settings,
                "api_token": "*" * len(str(new_settings.get("api_token", ""))),
                "is_available": False,
            },
        ),
    ]

    @cached_property
    def object(self) -> CveCrowdSettings:
        return CveCrowdSettings.objects.first()
