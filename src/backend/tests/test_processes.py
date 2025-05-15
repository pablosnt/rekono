from typing import Any

from processes.models import Process, Step
from tests.cases import ApiTestCase
from tests.framework import ApiTest

# pytype: disable=wrong-arg-types

first_process_name = "All tools"

process1 = {"name": "test1", "description": "test", "tags": ["test"]}
new_process1 = {"name": "new test1", "description": "test", "tags": ["test"]}
process2 = {"name": "test2", "description": "test", "tags": ["newtest"]}
new_process2 = {"name": "test2", "description": "test", "tags": ["newtest"]}
invalid_process1 = {"name": "invalid ; test", "description": "test", "tags": ["test"]}
invalid_process2 = {"name": "test", "description": "invalid ; test", "tags": ["test"]}


class ProcessTest(ApiTest):
    endpoint = "/api/processes/"
    expected_str = first_process_name
    cases = [
        ApiTestCase(["reader1", "reader2"], "get", 403),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            200,
            expected={
                "id": 1,
                "name": first_process_name,
                "owner": None,
                "liked": False,
                "likes": 0,
            },
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(["admin1", "admin2", "auditor1", "auditor2"], "post", 400, invalid_process1),
        ApiTestCase(["admin1", "admin2", "auditor1", "auditor2"], "post", 400, invalid_process2),
        ApiTestCase(
            ["admin1"],
            "post",
            201,
            process1,
            {
                "id": 8,
                **process1,
                "owner": {"id": 1, "username": "admin1"},
                "liked": False,
                "likes": 0,
            },
        ),
        ApiTestCase(["admin1", "admin2", "auditor1", "auditor2"], "post", 400, process1),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            200,
            expected={
                "id": 8,
                **process1,
                "owner": {"id": 1, "username": "admin1"},
                "liked": False,
                "likes": 0,
            },
            endpoint="{endpoint}8/",
        ),
        ApiTestCase(["reader1", "reader2"], "get", 403, endpoint="{endpoint}8/"),
        ApiTestCase(
            ["auditor1"],
            "post",
            201,
            process2,
            {
                "id": 9,
                **process2,
                "owner": {"id": 3, "username": "auditor1"},
                "liked": False,
                "likes": 0,
            },
        ),
        ApiTestCase(["admin1", "admin2", "auditor1", "auditor2"], "post", 400, process2),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            200,
            expected={
                "id": 9,
                **process2,
                "owner": {"id": 3, "username": "auditor1"},
                "liked": False,
                "likes": 0,
            },
            endpoint="{endpoint}9/",
        ),
        ApiTestCase(["reader1", "reader2"], "get", 403, endpoint="{endpoint}9/"),
        ApiTestCase(
            ["admin1", "admin2"],
            "put",
            200,
            new_process1,
            {
                "id": 8,
                **new_process1,
                "owner": {"id": 1, "username": "admin1"},
                "liked": False,
                "likes": 0,
            },
            endpoint="{endpoint}8/",
        ),
        ApiTestCase(
            ["auditor1", "auditor2", "reader1", "reader2"],
            "put",
            403,
            new_process1,
            endpoint="{endpoint}8/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1"],
            "put",
            200,
            new_process2,
            {
                "id": 9,
                **new_process2,
                "owner": {"id": 3, "username": "auditor1"},
                "liked": False,
                "likes": 0,
            },
            endpoint="{endpoint}9/",
        ),
        ApiTestCase(
            ["auditor2", "reader1", "reader2"],
            "put",
            403,
            new_process2,
            endpoint="{endpoint}9/",
        ),
        ApiTestCase(["reader1", "reader2"], "post", 403, endpoint="{endpoint}8/like/"),
        ApiTestCase(["reader1", "reader2"], "delete", 403, endpoint="{endpoint}9/like/"),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            200,
            endpoint="{endpoint}?like=true",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "post",
            204,
            endpoint="{endpoint}8/like/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            200,
            expected={
                "id": 8,
                **new_process1,
                "owner": {"id": 1, "username": "admin1"},
                "liked": True,
                "likes": 4,
            },
            endpoint="{endpoint}8/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            200,
            expected=[
                {
                    "id": 8,
                    **new_process1,
                    "owner": {"id": 1, "username": "admin1"},
                    "liked": True,
                    "likes": 4,
                }
            ],
            endpoint="{endpoint}?like=true",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "delete",
            204,
            endpoint="{endpoint}8/like/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            200,
            expected={
                "id": 8,
                **new_process1,
                "owner": {"id": 1, "username": "admin1"},
                "liked": False,
                "likes": 0,
            },
            endpoint="{endpoint}8/",
        ),
        ApiTestCase(
            ["auditor1", "auditor2", "reader1", "reader2"],
            "delete",
            403,
            endpoint="{endpoint}8/",
        ),
        ApiTestCase(["auditor2", "reader1", "reader2"], "delete", 403, endpoint="{endpoint}9/"),
        ApiTestCase(["admin2"], "delete", 204, endpoint="{endpoint}8/"),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            404,
            endpoint="{endpoint}8/",
        ),
        ApiTestCase(["reader1", "reader2"], "get", 403, endpoint="{endpoint}9/"),
        ApiTestCase(["auditor1"], "delete", 204, endpoint="{endpoint}9/"),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            404,
            endpoint="{endpoint}9/",
        ),
        ApiTestCase(["reader1", "reader2"], "get", 403, endpoint="{endpoint}9/"),
    ]

    def _get_object(self) -> Any:
        return Process.objects.first()


step1 = {"process_id": 8, "configuration_id": 1}
expected_step1 = {
    "process": {"id": step1["process_id"]},
    "configuration": {"id": step1["configuration_id"]},
}


class StepTest(ApiTest):
    endpoint = "/api/steps/"
    expected_str = f"{first_process_name} - theHarvester - All available sources"
    cases = [
        ApiTestCase(["reader1", "reader2"], "get", 403),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            200,
            expected={
                "id": 1,
                "process": {"id": 1},
                "configuration": {"id": 19},
            },
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(["auditor1", "auditor2", "reader1", "reader2"], "post", 403, step1),
        ApiTestCase(["admin1"], "post", 201, step1, {"id": 73, **expected_step1}),
        ApiTestCase(["admin2"], "post", 400, step1),
        ApiTestCase(["reader1", "reader2"], "get", 403, endpoint="{endpoint}73/"),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            200,
            expected={"id": 73, **expected_step1},
            endpoint="{endpoint}73/",
        ),
        ApiTestCase(
            ["auditor1", "auditor2", "reader1", "reader2"],
            "delete",
            403,
            endpoint="{endpoint}73/",
        ),
        ApiTestCase(["admin2"], "delete", 204, endpoint="{endpoint}73/"),
        ApiTestCase(["admin1"], "delete", 404, endpoint="{endpoint}73/"),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            404,
            endpoint="{endpoint}73/",
        ),
    ]

    def setUp(self) -> None:
        super().setUp()
        self.process = Process.objects.create(name="test", description="test")

    def _get_object(self) -> Any:
        return Step.objects.first()
