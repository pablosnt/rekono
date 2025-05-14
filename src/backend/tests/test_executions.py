from typing import Any

from executions.enums import Status
from tests.cases import ApiTestCase
from tests.framework import ApiTest

# pytype: disable=wrong-arg-types


class ExecutionTest(ApiTest):
    endpoint = "/api/executions/"
    expected_str = "10.10.10.10 - Nmap - TCP ports"
    cases = [
        ApiTestCase(["admin2", "auditor2", "reader2"], "get", 200),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected=[
                {
                    "id": 3,
                    "task": 2,
                    "configuration": {
                        "id": 1,
                        "name": "TCP ports",
                        "tool": {"id": 1, "name": "Nmap"},
                    },
                    "status": Status.COMPLETED.value,
                },
                {
                    "id": 2,
                    "task": 1,
                    "configuration": {
                        "id": 19,
                        "name": "All available sources",
                        "tool": {"id": 3, "name": "theHarvester"},
                    },
                    "status": Status.RUNNING.value,
                },
                {
                    "id": 1,
                    "task": 1,
                    "configuration": {
                        "id": 19,
                        "name": "All available sources",
                        "tool": {"id": 3, "name": "theHarvester"},
                    },
                    "status": Status.COMPLETED.value,
                },
            ],
        ),
        ApiTestCase(["admin2", "auditor2", "reader2"], "get", 404, endpoint="{endpoint}3/"),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected={
                "id": 3,
                "task": 2,
                "configuration": {
                    "id": 1,
                    "name": "TCP ports",
                    "tool": {"id": 1, "name": "Nmap"},
                },
                "status": Status.COMPLETED.value,
            },
            endpoint="{endpoint}3/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            404,
            endpoint="{endpoint}1/report/",
        ),
        ApiTestCase(
            ["admin2", "auditor2", "reader2"],
            "get",
            404,
            endpoint="{endpoint}2/report/",
        ),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            400,
            endpoint="{endpoint}2/report/",
        ),
        ApiTestCase(
            ["admin2", "auditor2", "reader2"],
            "get",
            404,
            endpoint="{endpoint}3/report/",
        ),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            endpoint="{endpoint}3/report/",
        ),
    ]

    def setUp(self) -> None:
        super().setUp()
        self._setup_tasks_and_executions()

    def _get_object(self) -> Any:
        return self.execution3
