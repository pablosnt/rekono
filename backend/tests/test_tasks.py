from functools import cached_property

from django.test import TestCase

from executions.enums import Status
from executions.models import Execution
from security.authorization.roles import Role
from tasks.models import Task
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase
from tests.framework.data import SetupProject
from tools.enums import Intensity

# pytype: disable=wrong-arg-types

task1 = {"target_id": 1, "configuration_id": 1, "intensity": Intensity.HARD.name.capitalize()}
task2 = {"target_id": 1, "process_id": 1}
invalid_task1 = {"target_id": 1, "intensity": 1}
invalid_task2 = {"target_id": 1}
invalid_task3 = {**task1, "configuration_id": 25, "intensity": Intensity.SNEAKY.name.capitalize()}
invalid_task4 = {"target_id": 1, "configuration_id": 36}  # Deprecated configuration


class TaskTest(ApiTest, TestCase):
    endpoint = "/api/tasks/"
    expected_string = "10.10.10.10 - Nmap - TCP ports"
    data = [SetupProject(executions_per_task=2), SetupProject(), SetupProject(executions_per_task=0)]
    cases = [
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
        ApiTestCase(
            ["members"],
            expected=[
                {
                    "id": 3,
                    "target": {"id": 3, "target": "10.10.10.30"},
                    "configuration": {"id": 1},
                    "process": None,
                    "executor": {"id": 3, "username": "auditor1"},
                    "intensity": Intensity.NORMAL.name.capitalize(),
                    "executions": [],
                },
                {
                    "id": 2,
                    "target": {"id": 2, "target": "10.10.10.20"},
                    "configuration": {"id": 1},
                    "process": None,
                    "executor": {"id": 3, "username": "auditor1"},
                    "intensity": Intensity.NORMAL.name.capitalize(),
                    "executions": [3],
                },
                {
                    "id": 1,
                    "target": {"id": 1, "target": "10.10.10.10"},
                    "configuration": {"id": 1},
                    "process": None,
                    "executor": {"id": 3, "username": "auditor1"},
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
                "configuration": {"id": 1},
                "process": None,
                "executor": {"id": 3, "username": "auditor1"},
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
                "id": 4,
                "target": {"id": 2, "target": "10.10.10.20"},
                "configuration": {"id": 1},
                "process": None,
                "executor": {"id": 3, "username": "auditor1"},
                "intensity": Intensity.NORMAL.name.capitalize(),
            },
            endpoint="2/repeat",
        ),
        DeleteApiTestCase(["admin2", "auditor2"], 404, endpoint="2"),
        DeleteApiTestCase([Role.READER], 403, endpoint="2"),
        DeleteApiTestCase(["admin1", "auditor1"], 400, endpoint="2"),
        DeleteApiTestCase(["admin1"], endpoint="1"),
        DeleteApiTestCase(["auditor1"], 400, endpoint="1"),
        DeleteApiTestCase(["admin1"], endpoint="3"),
        ApiTestCase(["members"], expected={"id": 1, "status": Status.CANCELLED}, endpoint="/api/executions/1/"),
        ApiTestCase(["members"], expected={"id": 2, "status": Status.CANCELLED}, endpoint="/api/executions/2/"),
        PostApiTestCase(["admin1", "auditor1"], 400, invalid_task1),
        PostApiTestCase(["admin1", "auditor1"], 400, invalid_task2),
        PostApiTestCase(["admin1", "auditor1"], 400, invalid_task3),
        PostApiTestCase(["admin1", "auditor1"], 400, invalid_task4),
        PostApiTestCase(["admin2", "auditor2", Role.READER], 403, task1),
        PostApiTestCase(
            ["admin1"],
            data=task1,
            expected={
                "id": 5,
                "target": {"id": 1, "target": "10.10.10.10"},
                "configuration": {"id": 1},
                "process": None,
                "executor": {"id": 1, "username": "admin1"},
                "intensity": Intensity.HARD.name.capitalize(),
            },
        ),
        PostApiTestCase(
            ["auditor1"],
            data=task2,
            expected={
                "id": 6,
                "target": {"id": 1, "target": "10.10.10.10"},
                "configuration": None,
                "process": {"id": 1, "name": "All tools"},
                "executor": {"id": 3, "username": "auditor1"},
                "intensity": Intensity.NORMAL.name.capitalize(),
            },
        ),
    ]

    def test_cases(self):
        Execution.objects.filter(id=3).update(status=Status.COMPLETED)
        super().test_cases()

    def test_status(self):
        execution = Execution.objects.get(pk=3)
        for status, task_status in [
            (Status.RUNNING, Status.RUNNING),
            (Status.CANCELLED, Status.CANCELLED),
            (Status.ERROR, Status.ERROR),
            (Status.COMPLETED, Status.COMPLETED),
            (Status.SKIPPED, Status.COMPLETED),
            (Status.REQUESTED, Status.REQUESTED),
        ]:
            execution.status = status
            execution.save(update_fields=["status"])
            ApiTestCase(["members"], expected={"id": 2, "status": task_status.value}, endpoint="2").test_case(
                0, self, self.endpoint
            )

    @cached_property
    def object(self) -> Task:
        return self.task


class LatestTasksTest(ApiTest, TestCase):
    endpoint = "/api/tasks/latest/"
    data = [SetupProject(1, 0), SetupProject(6, 0)]
    cases = [
        ApiTestCase(["members"], expected=[{"id": value, "target": {"id": value}} for value in range(1, 6)]),
        ApiTestCase(["not_members"]),
        ApiTestCase(["members"], expected=[{"id": 1, "target": {"id": 1}}], endpoint="{endpoint}?project=1"),
        ApiTestCase(["not_members"], endpoint="{endpoint}?project=1"),
        ApiTestCase(["members"], expected=[{"id": 1, "target": {"id": 1}}], endpoint="{endpoint}?target=1"),
        ApiTestCase(
            ["members"],
            expected=[{"id": value, "target": {"id": value}} for value in range(2, 7)],
            endpoint="{endpoint}?project=2",
        ),
        ApiTestCase(["members"], expected=[{"id": 2, "target": {"id": 2}}], endpoint="{endpoint}?target=2"),
    ]
