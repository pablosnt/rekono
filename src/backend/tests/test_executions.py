from functools import cached_property

from django.test import TestCase

from executions.enums import Status
from executions.models import Execution
from security.authorization.roles import Role
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

    @cached_property
    def object(self) -> Execution:
        return self.execution
