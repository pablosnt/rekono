from functools import cached_property

from django.test import TestCase

from executions.enums import Status
from executions.models import Execution
from security.authorization.roles import Role
from tasks.models import Task
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types


class ExecutionTest(ApiTest, TestCase):
    endpoint = "/api/executions/"
    expected_string = "10.10.10.10 - Nmap - TCP ports"
    data = [SetupProject(executions_per_task=2), SetupProject()]
    cases = [
        ApiTestCase(["not_members"]),
        ApiTestCase(
            ["members"],
            expected=[
                {"id": 3, "task": 2, "configuration": {"id": 1}, "status": Status.COMPLETED.value},
                {"id": 2, "task": 1, "configuration": {"id": 1}, "status": Status.REQUESTED.value},
                {"id": 1, "task": 1, "configuration": {"id": 1}, "status": Status.COMPLETED.value},
            ],
        ),
        ApiTestCase(["not_members"], 404, endpoint="3"),
        ApiTestCase(
            ["members"],
            expected={"id": 3, "task": 2, "configuration": {"id": 1}, "status": Status.COMPLETED.value},
            endpoint="3",
        ),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], status_code=404, endpoint="1/report"),
        ApiTestCase(["not_members"], status_code=404, endpoint="2/report"),
        ApiTestCase(["members"], status_code=400, endpoint="2/report"),
        ApiTestCase(["not_members"], status_code=404, endpoint="3/report"),
        ApiTestCase(["members"], endpoint="3/report"),
    ]

    def test_cases(self):
        Execution.objects.filter(id__in=[1, 3]).update(status=Status.COMPLETED)
        Execution.objects.filter(id=3).update(
            output_file=self.data_dir / "reports" / "nmap" / "enumeration-vulners.xml"
        )
        return super().test_cases()

    def test_lifecycle(self) -> None:
        # Reset status
        Execution.objects.update(status=Status.REQUESTED, start=None, end=None)
        Task.objects.update(start=None, end=None)
        execution1 = Execution.objects.get(pk=1)
        execution2 = Execution.objects.get(pk=2)
        # Task 1 owns executions 1 and 2
        task = self.execution.task

        # Start execution 1
        execution1.started()
        execution1.refresh_from_db()
        task.refresh_from_db()
        self.assertEqual(Status.RUNNING.value, execution1.status)
        self.assertIsNotNone(execution1.start)
        self.assertEqual(execution1.start, task.start)

        # Start execution 2
        execution2.started()
        task.refresh_from_db()
        self.assertEqual(execution1.start, task.start)

        # Complete execution 1
        execution1.completed("hash-value")
        execution1.refresh_from_db()
        task.refresh_from_db()
        self.assertEqual(Status.COMPLETED.value, execution1.status)
        self.assertEqual("hash-value", execution1.hash)
        self.assertIsNotNone(execution1.end)
        self.assertIsNone(task.end)

        # Error execution 2
        execution2.error()
        execution2.refresh_from_db()
        task.refresh_from_db()
        self.assertEqual(Status.ERROR.value, execution2.status)
        self.assertEqual(execution2.end, task.end)

        # Task 2 owns execution 3
        # Skipped execution 3
        execution3 = Execution.objects.get(pk=3)
        execution3.skipped("tool is not installed")
        execution3.refresh_from_db()
        self.assertEqual(Status.SKIPPED.value, execution3.status)
        self.assertEqual("tool is not installed", execution3.skipped_reason)
        self.assertIsNotNone(execution3.end)
        self.assertEqual(execution3.end, execution3.task.end)

    @cached_property
    def object(self) -> Execution:
        return self.execution
