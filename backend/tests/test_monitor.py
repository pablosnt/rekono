from functools import cached_property

from django.test import TestCase

from monitor.models import MonitorSettings
from security.authorization.roles import Role
from tests.framework import ApiTestNoData
from tests.framework.cases import ApiTestCase, PutApiTestCase

new_monitor = {"hour_span": 48}
invalid_monitor_1 = {"hour_span": 169}
invalid_monitor_2 = {"hour_span": 23}


class MonitorSettingsTest(ApiTestNoData, TestCase):
    endpoint = "/api/monitor/1/"
    expected_string = "Last monitor was at None. Next one in 24 hours"
    cases = [
        ApiTestCase([Role.AUDITOR, Role.READER], 403),
        ApiTestCase([Role.ADMIN], expected={"id": 1, "last_monitor": None, "hour_span": 24}),
        PutApiTestCase([Role.ADMIN], 400, invalid_monitor_1),
        PutApiTestCase([Role.ADMIN], 400, invalid_monitor_2),
        PutApiTestCase([Role.ADMIN], data=new_monitor, expected={"id": 1, "last_monitor": None, **new_monitor}),
        ApiTestCase([Role.ADMIN], expected={"id": 1, "last_monitor": None, **new_monitor}),
    ]

    @cached_property
    def object(self) -> MonitorSettings:
        return MonitorSettings.objects.first()
