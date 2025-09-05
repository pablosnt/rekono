from functools import cached_property

from executions.enums import Status
from executions.models import Execution
from security.authorization.roles import Role
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase

# pytype: disable=wrong-arg-types


class ExecutionTest(ApiTest):
    endpoint = "/api/executions/"
    expected_string = "10.10.10.10 - Nmap - TCP ports"
    setup_entities = ["executions"]
    cases = [
        ApiTestCase(["not_members"]),
        ApiTestCase(
            ["members"],
            expected=[
                {
                    "id": 3,
                    "task": 2,
                    "configuration": {"id": 1, "name": "TCP ports", "tool": {"id": 1, "name": "Nmap"}},
                    "status": Status.COMPLETED.value,
                },
                {
                    "id": 2,
                    "task": 1,
                    "configuration": {"id": 19, "name": "Simple scan", "tool": {"id": 3, "name": "theHarvester"}},
                    "status": Status.RUNNING.value,
                },
                {
                    "id": 1,
                    "task": 1,
                    "configuration": {"id": 19, "name": "Simple scan", "tool": {"id": 3, "name": "theHarvester"}},
                    "status": Status.COMPLETED.value,
                },
            ],
        ),
        ApiTestCase(["not_members"], 404, endpoint="3"),
        ApiTestCase(
            ["members"],
            expected={
                "id": 3,
                "task": 2,
                "configuration": {"id": 1, "name": "TCP ports", "tool": {"id": 1, "name": "Nmap"}},
                "status": Status.COMPLETED.value,
            },
            endpoint="3",
        ),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], status_code=404, endpoint="1/report"),
        ApiTestCase(["not_members"], status_code=404, endpoint="2/report"),
        ApiTestCase(["members"], status_code=400, endpoint="2/report"),
        ApiTestCase(["not_members"], status_code=404, endpoint="3/report"),
        ApiTestCase(["members"], endpoint="3/report"),
    ]

    @cached_property
    def object(self) -> Execution:
        return self.execution21
