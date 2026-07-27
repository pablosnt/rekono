from functools import cached_property

from django.test import TestCase
from rest_framework.test import APIClient

from processes.models import Process, Step
from security.authorization.roles import Role
from tests.framework import ApiTestNoData
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase, PutApiTestCase
from tools.models import Configuration

# pytype: disable=wrong-arg-types

first_process_name = "All tools"
process1 = {"name": "test1", "description": "test", "tags": ["test"]}
new_process1 = {"name": "new test1", "description": "test", "tags": ["test"]}
process2 = {"name": "test2", "description": "test", "tags": ["newtest"]}
new_process2 = {"name": "test2", "description": "test", "tags": ["newtest"]}
invalid_process1 = {"name": "invalid ; test", "description": "test", "tags": ["test"]}
invalid_process2 = {"name": "test", "description": "invalid ; test", "tags": ["test"]}


class ProcessTest(ApiTestNoData, TestCase):
    endpoint = "/api/processes/"
    expected_string = first_process_name
    cases = [
        ApiTestCase([Role.READER], 403),
        ApiTestCase(
            [Role.ADMIN, Role.AUDITOR],
            expected={"id": 1, "name": first_process_name, "owner": None, "liked": False, "likes": 0},
            endpoint="1",
        ),
        PostApiTestCase([Role.ADMIN, Role.AUDITOR], 400, invalid_process1),
        PostApiTestCase([Role.ADMIN, Role.AUDITOR], 400, invalid_process2),
        PostApiTestCase(
            ["admin1"],
            data=process1,
            expected={"id": 8, **process1, "owner": {"id": 1, "username": "admin1"}},
        ),
        PostApiTestCase([Role.ADMIN, Role.AUDITOR], 400, process1),
        ApiTestCase(
            [Role.ADMIN, Role.AUDITOR],
            expected={"id": 8, **process1, "owner": {"id": 1, "username": "admin1"}, "liked": False, "likes": 0},
            endpoint="8",
        ),
        ApiTestCase([Role.READER], 403, endpoint="8"),
        PostApiTestCase(
            ["auditor1"],
            data=process2,
            expected={"id": 9, **process2, "owner": {"id": 3, "username": "auditor1"}},
        ),
        PostApiTestCase([Role.ADMIN, Role.AUDITOR], 400, process2),
        ApiTestCase(
            [Role.ADMIN, Role.AUDITOR],
            expected={"id": 9, **process2, "owner": {"id": 3, "username": "auditor1"}, "liked": False, "likes": 0},
            endpoint="9",
        ),
        ApiTestCase([Role.READER], 403, endpoint="9"),
        PutApiTestCase(
            [Role.ADMIN],
            data=new_process1,
            expected={"id": 8, **new_process1, "owner": {"id": 1, "username": "admin1"}, "liked": False, "likes": 0},
            endpoint="8",
        ),
        PutApiTestCase([Role.AUDITOR, Role.READER], 403, new_process1, endpoint="8"),
        PutApiTestCase(
            [Role.ADMIN, "auditor1"],
            data=new_process2,
            expected={"id": 9, **new_process2, "owner": {"id": 3, "username": "auditor1"}, "liked": False, "likes": 0},
            endpoint="9",
        ),
        PutApiTestCase(["auditor2", Role.READER], 403, new_process2, endpoint="9"),
        PostApiTestCase([Role.READER], 403, endpoint="8/like"),
        DeleteApiTestCase([Role.READER], 403, endpoint="9/like"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR], endpoint="{endpoint}?like=true"),
        PostApiTestCase([Role.ADMIN, Role.AUDITOR], 204, endpoint="8/like/"),
        ApiTestCase(
            [Role.ADMIN, Role.AUDITOR],
            expected={"id": 8, **new_process1, "owner": {"id": 1, "username": "admin1"}, "liked": True, "likes": 4},
            endpoint="8",
        ),
        ApiTestCase(
            [Role.ADMIN, Role.AUDITOR],
            expected=[{"id": 8, **new_process1, "owner": {"id": 1, "username": "admin1"}, "liked": True, "likes": 4}],
            endpoint="{endpoint}?like=true",
        ),
        DeleteApiTestCase([Role.ADMIN, Role.AUDITOR], endpoint="8/like"),
        ApiTestCase(
            [Role.ADMIN, Role.AUDITOR],
            expected={"id": 8, **new_process1, "owner": {"id": 1, "username": "admin1"}, "liked": False, "likes": 0},
            endpoint="8",
        ),
        DeleteApiTestCase([Role.AUDITOR, Role.READER], 403, endpoint="8"),
        DeleteApiTestCase(["auditor2", Role.READER], 403, endpoint="9"),
        DeleteApiTestCase(["admin2"], endpoint="8"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR], 404, endpoint="8"),
        ApiTestCase([Role.READER], 403, endpoint="9"),
        DeleteApiTestCase(["auditor1"], endpoint="9"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR], 404, endpoint="9"),
        ApiTestCase([Role.READER], 403, endpoint="9"),
    ]

    @cached_property
    def object(self) -> Process:
        return Process.objects.first()

    def test_steps_exclude_deprecated(self) -> None:
        client = APIClient()
        client.force_authenticate(self.admin1)
        step = Step.objects.filter(process_id=1, configuration__deprecated=False).first()
        Configuration.objects.filter(pk=step.configuration_id).update(deprecated=True)
        self.assertNotIn(step.pk, [s["id"] for s in client.get("/api/processes/1/").json()["steps"]])


step1 = {"process_id": 8, "configuration_id": 1}
expected_step1 = {"process": {"id": step1["process_id"]}, "configuration": {"id": step1["configuration_id"]}}


class StepTest(ApiTestNoData, TestCase):
    endpoint = "/api/steps/"
    expected_string = f"{first_process_name} - theHarvester - Simple scan"
    cases = [
        ApiTestCase([Role.READER], 403),
        ApiTestCase(
            [Role.ADMIN, Role.AUDITOR],
            expected={"id": 1, "process": {"id": 1}, "configuration": {"id": 19}},
            endpoint="1",
        ),
        PostApiTestCase([Role.AUDITOR, Role.READER], 403, step1),
        PostApiTestCase(["admin1"], data=step1, expected={"id": 77, **expected_step1}),
        PostApiTestCase(["admin2"], 400, step1),
        ApiTestCase([Role.READER], 403, endpoint="77"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR], expected={"id": 77, **expected_step1}, endpoint="77"),
        DeleteApiTestCase([Role.AUDITOR, Role.READER], 403, endpoint="77"),
        DeleteApiTestCase(["admin2"], endpoint="77"),
        DeleteApiTestCase(["admin1"], 404, endpoint="77"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR], 404, endpoint="77"),
    ]

    def setUp(self) -> None:
        super().setUp()
        self.process = Process.objects.create(name="test", description="test")

    @cached_property
    def object(self) -> Step:
        return Step.objects.first()

    def test_endpoint_excludes_deprecated(self) -> None:
        client = APIClient()
        client.force_authenticate(self.admin1)
        self.assertEqual(0, Step.objects.filter(configuration__deprecated=True).count())
        step = Step.objects.filter(process_id=1, configuration__deprecated=False).first()
        Configuration.objects.filter(pk=step.configuration_id).update(deprecated=True)
        self.assertEqual(404, client.get(f"/api/steps/{step.pk}/").status_code)
        self.assertNotIn(step.pk, [s["id"] for s in client.get("/api/steps/?process=1").json()["results"]])
