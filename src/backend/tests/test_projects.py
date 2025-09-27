from functools import cached_property

from django.test import TestCase

from projects.models import Project
from security.authorization.roles import Role
from tests.framework import ApiTestNoData
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase, PutApiTestCase

# pytype: disable=wrong-arg-types

project1 = {"name": "test1", "description": "test1", "tags": ["test"]}
new_project1 = {"name": "new test1", "description": "test1", "tags": ["test"]}
project2 = {"name": "test2", "description": "test2", "tags": ["test"]}
invalid_project = {"name": "invalid name;", "description": "test1", "tags": ["test"]}


class ProjectTest(ApiTestNoData, TestCase):
    endpoint = "/api/projects/"
    expected_string = project1.get("name")
    cases = [
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
        PostApiTestCase([Role.AUDITOR, Role.READER], 403, project1),
        PostApiTestCase([Role.ADMIN], 400, invalid_project),
        PostApiTestCase(["admin1"], data=project1, expected={"id": 1, **project1}),
        ApiTestCase(["admin1"], expected=[{"id": 1, **project1}]),
        ApiTestCase(["admin2", Role.AUDITOR, Role.READER]),
        ApiTestCase(["admin1"], expected={"id": 1, **project1}, endpoint="1"),
        ApiTestCase(["admin2", Role.AUDITOR, Role.READER], 404, endpoint="1"),
        PostApiTestCase(["admin2"], 400, project1),
        PostApiTestCase(["admin2"], 404, endpoint="1/members/3"),
        PostApiTestCase([Role.AUDITOR, Role.READER], 403, endpoint="1/members/3"),
        PostApiTestCase(["admin1"], 204, endpoint="1/members/3"),
        ApiTestCase(["auditor1"], expected={"id": 1, **project1}, endpoint="1"),
        ApiTestCase(["admin2", "auditor2", Role.READER], 404, endpoint="1"),
        DeleteApiTestCase(["admin1"], endpoint="1/members/3"),
        PostApiTestCase(["admin1"], 204, endpoint="1/members/5"),
        ApiTestCase(["admin2", Role.AUDITOR, "reader2"], 404, endpoint="1"),
        ApiTestCase(["admin1", "reader1"], expected={"id": 1, **project1}, endpoint="1"),
        PostApiTestCase(["admin1"], 404, endpoint="1/members/100"),
        DeleteApiTestCase(["admin1"], 400, endpoint="1/members/1"),
        PutApiTestCase(["admin2"], 404, new_project1, endpoint="1"),
        PutApiTestCase([Role.AUDITOR, Role.READER], 403, new_project1, endpoint="1"),
        PutApiTestCase(["admin1"], data=new_project1, expected={"id": 1, **new_project1}, endpoint="1"),
        ApiTestCase(["admin1", "reader1"], expected={"id": 1, **new_project1}, endpoint="1"),
        DeleteApiTestCase(["admin2"], 404, endpoint="1"),
        DeleteApiTestCase([Role.AUDITOR, Role.READER], 403, endpoint="1"),
        DeleteApiTestCase(["admin1"], endpoint="1"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 404, endpoint="1"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
    ]

    @cached_property
    def object(self) -> Project:
        return Project.objects.create(**project1)
