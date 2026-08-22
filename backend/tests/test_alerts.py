from functools import cached_property

from django.test import TestCase

from alerts.enums import AlertItem
from alerts.models import Alert
from security.authorization.roles import Role
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase, PutApiTestCase

# pytype: disable=wrong-arg-types

new_alert = {
    "project": 1,
    "item": AlertItem.HOST.value,
    "value": None,
    "subscribe_all_members": True,
}
filter_alert = {
    "project": 1,
    "item": AlertItem.SERVICE.value,
    "value": "ssh",
    "subscribe_all_members": False,
}
invalid_filter_alert = {**filter_alert, "value": "inv;alid"}
monitor_alert = {
    "project": 1,
    "item": AlertItem.TRENDING_CVE.value,
    "value": str(True),
    "subscribe_all_members": False,
}


class AlertTest(ApiTest, TestCase):
    endpoint = "/api/alerts/"
    expected_string = "Project 1 - CVE - CVE-2020-1111"
    cases = [
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
        PostApiTestCase(["not_members"], 403, new_alert),
        PostApiTestCase(
            ["admin1"],
            data=new_alert,
            expected={
                "id": 1,
                **new_alert,
                "subscribe_all_members": None,
                "subscribed": True,
                "enabled": True,
                "owner": {"id": 1, "username": "admin1"},
            },
        ),
        ApiTestCase(
            ["members"],
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
        ApiTestCase(["not_members"]),
        PostApiTestCase(["auditor1", "reader1"], 403, endpoint="1/enable"),
        PostApiTestCase(["admin1"], 400, endpoint="1/enable"),
        DeleteApiTestCase(
            ["admin1"],
            200,
            expected={
                "id": 1,
                **new_alert,
                "subscribe_all_members": None,
                "subscribed": True,
                "enabled": False,
                "owner": {"id": 1, "username": "admin1"},
            },
            endpoint="1/enable",
        ),
        DeleteApiTestCase(["admin1"], status_code=400, endpoint="1/enable"),
        PostApiTestCase(
            ["admin1"],
            200,
            expected={
                "id": 1,
                **new_alert,
                "subscribe_all_members": None,
                "subscribed": True,
                "enabled": True,
                "owner": {"id": 1, "username": "admin1"},
            },
            endpoint="1/enable",
        ),
        ApiTestCase(
            ["members"],
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
        DeleteApiTestCase(["auditor1", "reader1"], 403, endpoint="1"),
        DeleteApiTestCase(["admin1"], endpoint="1"),
        PostApiTestCase(["members"], 400, invalid_filter_alert),
        PostApiTestCase(
            ["auditor1"],
            data=filter_alert,
            expected={
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
            expected=[
                {
                    "id": 2,
                    **filter_alert,
                    "subscribe_all_members": None,
                    "subscribed": False,
                    "enabled": True,
                    "owner": {"id": 3, "username": "auditor1"},
                }
            ],
        ),
        ApiTestCase(
            ["auditor1"],
            expected=[
                {
                    "id": 2,
                    **filter_alert,
                    "subscribe_all_members": None,
                    "subscribed": True,
                    "enabled": True,
                    "owner": {"id": 3, "username": "auditor1"},
                }
            ],
        ),
        PostApiTestCase(["admin1", "reader1"], 204, endpoint="2/subscription"),
        PostApiTestCase(["admin1", "reader1"], 400, endpoint="2/subscription"),
        ApiTestCase(
            ["members"],
            expected=[
                {
                    "id": 2,
                    **filter_alert,
                    "subscribe_all_members": None,
                    "subscribed": True,
                    "enabled": True,
                    "owner": {"id": 3, "username": "auditor1"},
                }
            ],
        ),
        DeleteApiTestCase(["members"], endpoint="2/subscription"),
        DeleteApiTestCase(["members"], 400, endpoint="2/subscription"),
        ApiTestCase(
            ["members"],
            expected=[
                {
                    "id": 2,
                    **filter_alert,
                    "subscribe_all_members": None,
                    "subscribed": False,
                    "enabled": True,
                    "owner": {"id": 3, "username": "auditor1"},
                }
            ],
        ),
        PutApiTestCase(["reader1"], 403, {"value": "http"}, endpoint="2"),
        PutApiTestCase(
            ["auditor1"],
            data={"value": "http"},
            expected={
                "id": 2,
                **filter_alert,
                "subscribe_all_members": None,
                "value": "http",
                "subscribed": False,
                "enabled": True,
                "owner": {"id": 3, "username": "auditor1"},
            },
            endpoint="2",
        ),
        PutApiTestCase(
            ["admin1"],
            data={"value": "https"},
            expected={
                "id": 2,
                **filter_alert,
                "subscribe_all_members": None,
                "value": "https",
                "subscribed": False,
                "enabled": True,
                "owner": {"id": 3, "username": "auditor1"},
            },
            endpoint="2",
        ),
        DeleteApiTestCase(["reader1"], 403, endpoint="2"),
        DeleteApiTestCase(["auditor1"], endpoint="2"),
        PostApiTestCase(
            ["reader1"],
            data=monitor_alert,
            expected={
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
            expected=[
                {
                    "id": 3,
                    **monitor_alert,
                    "subscribe_all_members": None,
                    "subscribed": False,
                    "enabled": True,
                    "owner": {"id": 5, "username": "reader1"},
                }
            ],
        ),
        ApiTestCase(
            ["reader1"],
            expected=[
                {
                    "id": 3,
                    **monitor_alert,
                    "subscribe_all_members": None,
                    "subscribed": True,
                    "enabled": True,
                    "owner": {"id": 5, "username": "reader1"},
                }
            ],
        ),
        DeleteApiTestCase(["auditor1"], 403, endpoint="3"),
        DeleteApiTestCase(["admin1"], endpoint="3"),
    ]

    @cached_property
    def object(self) -> Alert:
        return Alert.objects.create(project=self.project, item=AlertItem.CVE, value="CVE-2020-1111")

    def test_must_be_triggered(self) -> None:
        for alert, finding, expected in [
            (
                Alert.objects.create(project=self.project, item=AlertItem.TRENDING_CVE, value=str(True)),
                self.vulnerability,
                False,
            ),
            (Alert.objects.create(project=self.project, item=AlertItem.HOST), self.host, True),
            (
                Alert.objects.create(project=self.project, item=AlertItem.OPEN_PORT),
                self.host,
                False,
            ),
            (
                Alert.objects.create(project=self.project, item=AlertItem.SERVICE, value="ssh"),
                self.port,
                False,
            ),
            (
                Alert.objects.create(project=self.project, item=AlertItem.SERVICE, value="http"),
                self.port,
                True,
            ),
        ]:
            self.assertEqual(expected, alert.must_be_triggered(self.execution, finding))
