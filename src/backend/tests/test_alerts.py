from typing import Any

from alerts.enums import AlertItem, AlertMode
from alerts.models import Alert, MonitorSettings
from tests.cases import ApiTestCase
from tests.framework import ApiTest

new_alert = {
    "project": 1,
    "item": AlertItem.HOST.value,
    "mode": AlertMode.NEW.value,
    "value": None,
    "subscribe_all_members": True,
}
filter_alert = {
    "project": 1,
    "item": AlertItem.SERVICE.value,
    "mode": AlertMode.FILTER.value,
    "value": "ssh",
    "subscribe_all_members": False,
}
invalid_filter_alert = {**filter_alert, "value": None}
monitor_alert = {
    "project": 1,
    "item": AlertItem.CVE.value,
    "mode": AlertMode.MONITOR.value,
    "value": None,
    "subscribe_all_members": False,
}


class AlertTest(ApiTest):
    endpoint = "/api/alerts/"
    expected_str = "test - Filter - CVE - CVE-2020-1111"
    cases = [
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected=[],
        ),
        ApiTestCase(["admin2", "auditor2", "reader2"], "post", 403, new_alert),
        ApiTestCase(
            ["admin1"],
            "post",
            201,
            new_alert,
            {
                "id": 1,
                **new_alert,
                "subscribe_all_members": None,
                "subscribed": True,
                "enabled": True,
                "owner": {"id": 1, "username": "admin1"},
            },
        ),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected=[
                {
                    "id": 1,
                    **new_alert,
                    "subscribe_all_members": None,
                    "subscribed": True,
                    "enabled": True,
                    "owner": {"id": 1, "username": "admin1"},
                }
            ],
        ),
        ApiTestCase(["admin2", "auditor2", "reader2"], "get", 200, expected=[]),
        ApiTestCase(["auditor1", "reader1"], "post", 403, endpoint="{endpoint}1/enable/"),
        ApiTestCase(["admin1"], "post", 400, endpoint="{endpoint}1/enable/"),
        ApiTestCase(
            ["admin1"],
            "delete",
            200,
            expected={
                "id": 1,
                **new_alert,
                "subscribe_all_members": None,
                "subscribed": True,
                "enabled": False,
                "owner": {"id": 1, "username": "admin1"},
            },
            endpoint="{endpoint}1/enable/",
        ),
        ApiTestCase(["admin1"], "delete", 400, endpoint="{endpoint}1/enable/"),
        ApiTestCase(
            ["admin1"],
            "post",
            200,
            expected={
                "id": 1,
                **new_alert,
                "subscribe_all_members": None,
                "subscribed": True,
                "enabled": True,
                "owner": {"id": 1, "username": "admin1"},
            },
            endpoint="{endpoint}1/enable/",
        ),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected=[
                {
                    "id": 1,
                    **new_alert,
                    "subscribe_all_members": None,
                    "subscribed": True,
                    "enabled": True,
                    "owner": {"id": 1, "username": "admin1"},
                }
            ],
        ),
        ApiTestCase(["auditor1", "reader1"], "delete", 403, endpoint="{endpoint}1/"),
        ApiTestCase(["admin1"], "delete", 204, endpoint="{endpoint}1/"),
        ApiTestCase(["admin1", "auditor1", "reader1"], "post", 400, invalid_filter_alert),
        ApiTestCase(
            ["auditor1"],
            "post",
            201,
            filter_alert,
            {
                "id": 2,
                **filter_alert,
                "subscribe_all_members": None,
                "subscribed": True,
                "enabled": True,
                "owner": {"id": 3, "username": "auditor1"},
            },
        ),
        ApiTestCase(
            ["admin1", "reader1"],
            "get",
            200,
            expected=[
                {
                    "id": 2,
                    **filter_alert,
                    "subscribe_all_members": None,
                    "subscribed": False,
                    "enabled": True,
                    "owner": {"id": 3, "username": "auditor1"},
                },
            ],
        ),
        ApiTestCase(
            ["auditor1"],
            "get",
            200,
            expected=[
                {
                    "id": 2,
                    **filter_alert,
                    "subscribe_all_members": None,
                    "subscribed": True,
                    "enabled": True,
                    "owner": {"id": 3, "username": "auditor1"},
                },
            ],
        ),
        ApiTestCase(["admin1", "reader1"], "post", 204, endpoint="{endpoint}2/subscription/"),
        ApiTestCase(["admin1", "reader1"], "post", 400, endpoint="{endpoint}2/subscription/"),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected=[
                {
                    "id": 2,
                    **filter_alert,
                    "subscribe_all_members": None,
                    "subscribed": True,
                    "enabled": True,
                    "owner": {"id": 3, "username": "auditor1"},
                },
            ],
        ),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "delete",
            204,
            endpoint="{endpoint}2/subscription/",
        ),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "delete",
            400,
            endpoint="{endpoint}2/subscription/",
        ),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected=[
                {
                    "id": 2,
                    **filter_alert,
                    "subscribe_all_members": None,
                    "subscribed": False,
                    "enabled": True,
                    "owner": {"id": 3, "username": "auditor1"},
                },
            ],
        ),
        ApiTestCase(["reader1"], "put", 403, {"value": "http"}, endpoint="{endpoint}2/"),
        ApiTestCase(
            ["auditor1"],
            "put",
            200,
            {"value": "http"},
            {
                "id": 2,
                **filter_alert,
                "subscribe_all_members": None,
                "value": "http",
                "subscribed": False,
                "enabled": True,
                "owner": {"id": 3, "username": "auditor1"},
            },
            "{endpoint}2/",
        ),
        ApiTestCase(
            ["admin1"],
            "put",
            200,
            {"value": "https"},
            {
                "id": 2,
                **filter_alert,
                "subscribe_all_members": None,
                "value": "https",
                "subscribed": False,
                "enabled": True,
                "owner": {"id": 3, "username": "auditor1"},
            },
            "{endpoint}2/",
        ),
        ApiTestCase(["reader1"], "delete", 403, endpoint="{endpoint}2/"),
        ApiTestCase(["auditor1"], "delete", 204, endpoint="{endpoint}2/"),
        ApiTestCase(
            ["reader1"],
            "post",
            201,
            monitor_alert,
            {
                "id": 3,
                **monitor_alert,
                "subscribe_all_members": None,
                "subscribed": True,
                "enabled": True,
                "owner": {"id": 5, "username": "reader1"},
            },
        ),
        ApiTestCase(
            ["admin1", "auditor1"],
            "get",
            200,
            expected=[
                {
                    "id": 3,
                    **monitor_alert,
                    "subscribe_all_members": None,
                    "subscribed": False,
                    "enabled": True,
                    "owner": {"id": 5, "username": "reader1"},
                },
            ],
        ),
        ApiTestCase(
            ["reader1"],
            "get",
            200,
            expected=[
                {
                    "id": 3,
                    **monitor_alert,
                    "subscribe_all_members": None,
                    "subscribed": True,
                    "enabled": True,
                    "owner": {"id": 5, "username": "reader1"},
                },
            ],
        ),
        ApiTestCase(["auditor1"], "delete", 403, endpoint="{endpoint}3/"),
        ApiTestCase(["admin1"], "delete", 204, endpoint="{endpoint}3/"),
    ]

    def setUp(self) -> None:
        super().setUp()
        self._setup_tasks_and_executions()
        self._setup_findings(self.execution3)

    def _get_object(self) -> Any:
        return Alert.objects.create(
            project=self.project,
            mode=AlertMode.FILTER,
            item=AlertItem.CVE,
            value="CVE-2020-1111",
        )

    def test_must_be_triggered(self) -> None:
        for alert, finding, expected in [
            (
                Alert.objects.create(
                    project=self.execution3.task.target.project,
                    mode=AlertMode.MONITOR,
                    item=AlertItem.CVE,
                ),
                self.vulnerability,
                False,
            ),
            (
                Alert.objects.create(
                    project=self.execution3.task.target.project,
                    mode=AlertMode.NEW,
                    item=AlertItem.HOST,
                ),
                self.host,
                True,
            ),
            (
                Alert.objects.create(
                    project=self.execution3.task.target.project,
                    mode=AlertMode.NEW,
                    item=AlertItem.OPEN_PORT,
                ),
                self.host,
                False,
            ),
            (
                Alert.objects.create(
                    project=self.execution3.task.target.project,
                    mode=AlertMode.FILTER,
                    item=AlertItem.SERVICE,
                    value="ssh",
                ),
                self.port,
                False,
            ),
            (
                Alert.objects.create(
                    project=self.execution3.task.target.project,
                    mode=AlertMode.FILTER,
                    item=AlertItem.SERVICE,
                    value="http",
                ),
                self.port,
                True,
            ),
        ]:
            self.assertEqual(expected, alert.must_be_triggered(self.execution3, finding))


new_monitor = {"hour_span": 48}
invalid_monitor_1 = {"hour_span": 169}
invalid_monitor_2 = {"hour_span": 23}


class MonitorSettingsTest(ApiTest):
    endpoint = "/api/monitor/1/"
    expected_str = "Last monitor was at None. Next one in 24 hours"
    cases = [
        ApiTestCase(["auditor1", "auditor2", "reader1", "reader2"], "get", 403),
        ApiTestCase(
            ["admin1", "admin2"],
            "get",
            200,
            expected={"id": 1, "last_monitor": None, "hour_span": 24},
        ),
        ApiTestCase(["admin1", "admin2"], "put", 400, invalid_monitor_1),
        ApiTestCase(["admin1", "admin2"], "put", 400, invalid_monitor_2),
        ApiTestCase(
            ["admin1", "admin2"],
            "put",
            200,
            new_monitor,
            expected={"id": 1, "last_monitor": None, **new_monitor},
        ),
        ApiTestCase(
            ["admin1", "admin2"],
            "get",
            200,
            expected={"id": 1, "last_monitor": None, **new_monitor},
        ),
    ]

    def _get_object(self) -> Any:
        return MonitorSettings.objects.first()
