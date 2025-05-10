from projects.models import Project
from tests.cases import ApiTestCase
from tests.framework import ApiTest

project1 = {"name": "test1", "description": "test1", "tags": ["test"]}
new_project1 = {"name": "new test1", "description": "test1", "tags": ["test"]}
project2 = {"name": "test2", "description": "test2", "tags": ["test"]}
invalid_project = {
    "name": "invalid name;",
    "description": "test1",
    "tags": ["test"],
}


class ProjectTest(ApiTest):
    endpoint = "/api/projects/"
    expected_str = project1.get("name")
    cases = [
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected=[],
        ),
        ApiTestCase(["auditor1", "auditor2", "reader1", "reader2"], "post", 403, project1),
        ApiTestCase(["admin1", "admin2"], "post", 400, invalid_project),
        ApiTestCase(["admin1"], "post", 201, project1, {"id": 1, **project1}),
        ApiTestCase(["admin1"], "get", 200, expected=[{"id": 1, **project1}]),
        ApiTestCase(
            ["admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected=[],
        ),
        ApiTestCase(
            ["admin1"],
            "get",
            200,
            expected={"id": 1, **project1},
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            404,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(["admin2"], "post", 400, project1),
        ApiTestCase(
            ["admin2"],
            "post",
            404,
            {"user": 3},
            endpoint="{endpoint}1/members/",
        ),
        ApiTestCase(
            ["auditor1", "auditor2", "reader1", "reader2"],
            "post",
            403,
            {"user": 3},
            endpoint="{endpoint}1/members/",
        ),
        ApiTestCase(["admin1"], "post", 201, {"user": 3}, endpoint="{endpoint}1/members/"),
        ApiTestCase(
            ["auditor1"],
            "get",
            200,
            expected={"id": 1, **project1},
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin2", "auditor2", "reader1", "reader2"],
            "get",
            404,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(["admin1"], "delete", 204, endpoint="{endpoint}1/members/3/"),
        ApiTestCase(["admin1"], "post", 201, {"user": 5}, endpoint="{endpoint}1/members/"),
        ApiTestCase(
            ["admin2", "auditor1", "auditor2", "reader2"],
            "get",
            404,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin1", "reader1"],
            "get",
            200,
            expected={"id": 1, **project1},
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(["admin1"], "post", 404, {"user": 100}, endpoint="{endpoint}1/members/"),
        ApiTestCase(["admin1"], "delete", 400, endpoint="{endpoint}1/members/1/"),
        ApiTestCase(
            ["admin2"],
            "put",
            404,
            new_project1,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["auditor1", "auditor2", "reader1", "reader2"],
            "put",
            403,
            new_project1,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin1"],
            "put",
            200,
            new_project1,
            {"id": 1, **new_project1},
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin1", "reader1"],
            "get",
            200,
            expected={"id": 1, **new_project1},
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin2"],
            "delete",
            404,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["auditor1", "auditor2", "reader1", "reader2"],
            "delete",
            403,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(["admin1"], "delete", 204, endpoint="{endpoint}1/"),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            404,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected=[],
        ),
    ]

    def _get_object(self) -> Project:
        return Project.objects.create(**project1)
