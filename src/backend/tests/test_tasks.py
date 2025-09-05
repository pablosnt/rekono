from functools import cached_property

from executions.enums import Status
from security.authorization.roles import Role
from tasks.models import Task
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase
from tools.enums import Intensity

# pytype: disable=wrong-arg-types

task1 = {"target_id": 1, "configuration_id": 1, "intensity": Intensity.HARD.name.capitalize()}
task2 = {"target_id": 1, "process_id": 1}
invalid_task1 = {"target_id": 1, "intensity": 1}
invalid_task2 = {"target_id": 1}
invalid_task3 = {**task1, "configuration_id": 25, "intensity": Intensity.SNEAKY.name.capitalize()}


class TaskTest(ApiTest):
    endpoint = "/api/tasks/"
    expected_string = "10.10.10.10 - All tools"
    setup_entities = ["executions"]
    cases = [
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
        ApiTestCase(
            ["members"],
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
        ApiTestCase(["not_members"], 404, endpoint="1"),
        ApiTestCase(
            ["members"],
            expected={
                "id": 1,
                "target": {"id": 1, "target": "10.10.10.10"},
                "configuration": None,
                "process": {"id": 1, "name": "All tools"},
                "executor": {"id": 1, "username": "admin1"},
                "intensity": Intensity.NORMAL.name.capitalize(),
                "executions": [1, 2],
            },
            endpoint="1",
        ),
        PostApiTestCase(["admin2", "auditor2"], 404, endpoint="1/repeat"),
        PostApiTestCase([Role.READER], 403, endpoint="1/repeat"),
        PostApiTestCase(["admin1", "auditor1"], 400, endpoint="1/repeat"),
        PostApiTestCase(
            ["auditor1"],
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
            endpoint="2/repeat",
        ),
        DeleteApiTestCase(["admin2", "auditor2"], 404, endpoint="2"),
        DeleteApiTestCase([Role.READER], 403, endpoint="2"),
        DeleteApiTestCase(["admin1", "auditor1"], 400, endpoint="2"),
        DeleteApiTestCase(["admin1"], endpoint="1"),
        DeleteApiTestCase(["auditor1"], 400, endpoint="1"),
        ApiTestCase(
            ["members"],
            expected={"id": 1, "status": Status.COMPLETED},
            endpoint="/api/executions/1/",
        ),
        ApiTestCase(
            ["members"],
            expected={"id": 2, "status": Status.CANCELLED},
            endpoint="/api/executions/2/",
        ),
        PostApiTestCase(["admin1", "auditor1"], 400, invalid_task1),
        PostApiTestCase(["admin1", "auditor1"], 400, invalid_task2),
        PostApiTestCase(["admin1", "auditor1"], 400, invalid_task3),
        PostApiTestCase(["admin2", "auditor2", Role.READER], 403, task1),
        PostApiTestCase(
            ["admin1"],
            data=task1,
            expected={
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
        PostApiTestCase(
            ["auditor1"],
            data=task2,
            expected={
                "id": 5,
                "target": {"id": 1, "target": "10.10.10.10"},
                "configuration": None,
                "process": {"id": 1, "name": "All tools"},
                "executor": {"id": 3, "username": "auditor1"},
                "intensity": Intensity.NORMAL.name.capitalize(),
            },
        ),
    ]

    @cached_property
    def object(self) -> Task:
        return self.task1
