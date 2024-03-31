from typing import Any

from executions.enums import Status
from tasks.enums import TimeUnit
from tests.cases import ApiTestCase
from tests.framework import ApiTest
from tools.enums import Intensity

task1 = {
    "target_id": 1,
    "configuration_id": 1,
    "intensity": Intensity.HARD.name.capitalize(),
}
task2 = {"target_id": 1, "process_id": 1}
invalid_task1 = {"target_id": 1, "intensity": 1}
invalid_task2 = {"target_id": 1}
invalid_task3 = {
    **task1,
    "configuration_id": 25,
    "intensity": Intensity.SNEAKY.name.capitalize(),
}


class TaskTest(ApiTest):
    endpoint = "/api/tasks/"
    expected_str = "10.10.10.10 - All tools"
    cases = [
        ApiTestCase(["admin2", "auditor2", "reader2"], "get", 200),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected=[
                {
                    "id": 2,
                    "target": {"id": 1, "target": "10.10.10.10"},
                    "configuration": {
                        "id": 1,
                        "tool": {"id": 1, "name": "Nmap"},
                        "name": "TCP ports",
                    },
                    "process": None,
                    "executor": {"id": 3, "username": "auditor1"},
                    "intensity": Intensity.NORMAL.name.capitalize(),
                    "executions": [3],
                },
                {
                    "id": 1,
                    "target": {"id": 1, "target": "10.10.10.10"},
                    "configuration": None,
                    "process": {"id": 1, "name": "All tools"},
                    "executor": {"id": 1, "username": "admin1"},
                    "intensity": Intensity.NORMAL.name.capitalize(),
                    "executions": [1, 2],
                },
            ],
        ),
        ApiTestCase(
            ["admin2", "auditor2", "reader2"], "get", 404, endpoint="{endpoint}1/"
        ),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected={
                "id": 1,
                "target": {"id": 1, "target": "10.10.10.10"},
                "configuration": None,
                "process": {"id": 1, "name": "All tools"},
                "executor": {"id": 1, "username": "admin1"},
                "intensity": Intensity.NORMAL.name.capitalize(),
                "executions": [1, 2],
            },
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin2", "auditor2"], "post", 404, endpoint="{endpoint}1/repeat/"
        ),
        ApiTestCase(
            ["reader1", "reader2"], "post", 403, endpoint="{endpoint}1/repeat/"
        ),
        ApiTestCase(
            ["admin1", "auditor1"], "post", 400, endpoint="{endpoint}1/repeat/"
        ),
        ApiTestCase(
            ["auditor1"],
            "post",
            201,
            expected={
                "id": 3,
                "target": {"id": 1, "target": "10.10.10.10"},
                "configuration": {
                    "id": 1,
                    "tool": {"id": 1, "name": "Nmap"},
                    "name": "TCP ports",
                },
                "process": None,
                "intensity": Intensity.NORMAL.name.capitalize(),
            },
            endpoint="{endpoint}2/repeat/",
        ),
        ApiTestCase(["admin2", "auditor2"], "delete", 404, endpoint="{endpoint}2/"),
        ApiTestCase(["reader1", "reader2"], "delete", 403, endpoint="{endpoint}2/"),
        ApiTestCase(["admin1", "auditor1"], "delete", 400, endpoint="{endpoint}2/"),
        ApiTestCase(["admin1"], "delete", 204, endpoint="{endpoint}1/"),
        ApiTestCase(["auditor1"], "delete", 400, endpoint="{endpoint}1/"),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected={"id": 1, "status": Status.COMPLETED},
            endpoint="/api/executions/1/",
        ),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected={"id": 2, "status": Status.CANCELLED},
            endpoint="/api/executions/2/",
        ),
        ApiTestCase(["admin1", "auditor1"], "post", 400, invalid_task1),
        ApiTestCase(["admin1", "auditor1"], "post", 400, invalid_task2),
        ApiTestCase(["admin1", "auditor1"], "post", 400, invalid_task3),
        ApiTestCase(["admin2", "auditor2", "reader1", "reader2"], "post", 403, task1),
        ApiTestCase(
            ["admin1"],
            "post",
            201,
            task1,
            {
                "id": 4,
                "target": {"id": 1, "target": "10.10.10.10"},
                "configuration": {
                    "id": 1,
                    "tool": {"id": 1, "name": "Nmap"},
                    "name": "TCP ports",
                },
                "process": None,
                "executor": {"id": 1, "username": "admin1"},
                "intensity": Intensity.HARD.name.capitalize(),
            },
        ),
        ApiTestCase(
            ["auditor1"],
            "post",
            201,
            task2,
            {
                "id": 5,
                "target": {"id": 1, "target": "10.10.10.10"},
                "configuration": None,
                "process": {"id": 1, "name": "All tools"},
                "executor": {"id": 3, "username": "auditor1"},
                "intensity": Intensity.NORMAL.name.capitalize(),
            },
        ),
    ]

    def setUp(self) -> None:
        super().setUp()
        self._setup_tasks_and_executions()

    def _get_object(self) -> Any:
        return self.running_task
