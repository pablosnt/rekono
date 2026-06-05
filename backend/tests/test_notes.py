from functools import cached_property

from django.test import TestCase

from notes.models import Note
from security.authorization.roles import Role
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase, PutApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types

# Model field values for direct DB creation
private_note = {
    "project": 1,
    "target": None,
    "task": None,
    "osint": None,
    "host": None,
    "port": None,
    "path": None,
    "credential": None,
    "technology": None,
    "vulnerability": None,
    "exploit": None,
    "title": "Title",
    "body": "Important things to remember",
    "tags": ["test"],
    "public": False,
}

# API request data for write operations: entity associations use *_id fields
private_note_data = {
    "project": 1,
    "target_id": None,
    "task_id": None,
    "osint_id": None,
    "host_id": None,
    "port_id": None,
    "path_id": None,
    "credential_id": None,
    "technology_id": None,
    "vulnerability_id": None,
    "exploit_id": None,
    "title": "Title",
    "body": "Important things to remember",
    "tags": ["test"],
    "public": False,
}
public_note_data = {**private_note_data, "public": True, "target_id": 1}
invalid_note_data = {**private_note_data, "title": "Invalid;content"}

# Expected API response data for read operations: entity associations are nested objects
private_note_expected = {k.replace("_id", ""): v for k, v in private_note_data.items()}
public_note_expected = {**private_note_expected, "public": True, "target": {"id": 1}}


class NoteTest(ApiTest, TestCase):
    endpoint = "/api/notes/"
    expected_string = "Project 1 - Title"
    data = [SetupProject(executions_per_task=0), SetupProject(executions_per_task=0)]
    cases = [
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
        PostApiTestCase(["admin2", "auditor2", Role.READER], 403, private_note_data),
        PostApiTestCase(["admin2", "auditor2", Role.READER], 403, public_note_data),
        PostApiTestCase(["admin1", "auditor1"], 400, invalid_note_data),
        PostApiTestCase(["admin1"], 400, {**private_note_data, "project": None}),
        PostApiTestCase(["admin1"], 400, {**public_note_data, "project": None, "target_id": None}),
        PostApiTestCase(
            ["admin1"],
            data=private_note_data,
            expected={
                "id": 1,
                **private_note_expected,
                "forked_from": None,
                "forks": [],
                "owner": {"id": 1, "username": "admin1"},
            },
        ),
        PostApiTestCase(
            ["auditor1"],
            data=public_note_data,
            expected={
                "id": 2,
                **public_note_expected,
                "forked_from": None,
                "forks": [],
                "owner": {"id": 3, "username": "auditor1"},
            },
        ),
        ApiTestCase(["not_members"]),
        ApiTestCase(
            ["admin1"],
            expected=[
                {
                    "id": 2,
                    **public_note_expected,
                    "forked_from": None,
                    "forks": [],
                    "owner": {"id": 3, "username": "auditor1"},
                },
                {
                    "id": 1,
                    **private_note_expected,
                    "forked_from": None,
                    "forks": [],
                    "owner": {"id": 1, "username": "admin1"},
                },
            ],
        ),
        ApiTestCase(
            ["auditor1", "reader1"],
            expected=[
                {
                    "id": 2,
                    **public_note_expected,
                    "forked_from": None,
                    "forks": [],
                    "owner": {"id": 3, "username": "auditor1"},
                }
            ],
        ),
        PostApiTestCase([Role.READER], 403, endpoint="2/fork"),
        PostApiTestCase(["admin2", "auditor2"], 404, endpoint="2/fork"),
        PostApiTestCase(["admin1", "auditor1"], 404, endpoint="1/fork"),
        PostApiTestCase(
            ["admin1"],
            expected={
                "id": 3,
                **public_note_expected,
                "public": False,
                "forked_from": 2,
                "forks": [],
                "owner": {"id": 1, "username": "admin1"},
            },
            endpoint="2/fork",
        ),
        ApiTestCase(
            ["admin1"],
            expected=[
                {
                    "id": 3,
                    **public_note_expected,
                    "public": False,
                    "forked_from": 2,
                    "forks": [],
                    "owner": {"id": 1, "username": "admin1"},
                },
                {
                    "id": 2,
                    **public_note_expected,
                    "forked_from": None,
                    "forks": [3],
                    "owner": {"id": 3, "username": "auditor1"},
                },
                {
                    "id": 1,
                    **private_note_expected,
                    "forked_from": None,
                    "forks": [],
                    "owner": {"id": 1, "username": "admin1"},
                },
            ],
        ),
        ApiTestCase(
            ["auditor1", "reader1"],
            expected=[
                {
                    "id": 2,
                    **public_note_expected,
                    "forked_from": None,
                    "forks": [3],
                    "owner": {"id": 3, "username": "auditor1"},
                },
            ],
        ),
        PutApiTestCase(["admin2", Role.AUDITOR], 404, public_note_data, endpoint="1"),
        PutApiTestCase([Role.READER], 403, public_note_data, endpoint="1"),
        PutApiTestCase(["admin1"], 400, {**public_note_data, "target_id": 2}, endpoint="1"),
        PutApiTestCase(
            ["admin1"],
            data=public_note_data,
            expected={
                "id": 1,
                **public_note_expected,
                "forked_from": None,
                "forks": [],
                "owner": {"id": 1, "username": "admin1"},
            },
            endpoint="1",
        ),
        ApiTestCase(["not_members"], 404, endpoint="1"),
        ApiTestCase(
            ["members"],
            expected={
                "id": 1,
                **public_note_expected,
                "forked_from": None,
                "forks": [],
                "owner": {"id": 1, "username": "admin1"},
            },
            endpoint="1",
        ),
        PutApiTestCase(
            ["admin1"],
            data={**public_note_data, "public": True},
            expected={
                "id": 3,
                **public_note_expected,
                "public": False,
                "forked_from": 2,
                "forks": [],
                "owner": {"id": 1, "username": "admin1"},
            },
            endpoint="3",
        ),
        PutApiTestCase(
            ["auditor1"],
            data={**public_note_data, "public": False},
            expected={
                "id": 2,
                **public_note_expected,
                "public": False,
                "forked_from": None,
                "forks": [],
                "owner": {"id": 3, "username": "auditor1"},
            },
            endpoint="2",
        ),
        ApiTestCase(
            ["admin1"],
            expected={
                "id": 3,
                **public_note_expected,
                "public": False,
                "forked_from": None,
                "forks": [],
                "owner": {"id": 1, "username": "admin1"},
            },
            endpoint="3",
        ),
        PutApiTestCase(
            ["admin1"],
            data={**public_note_data, "public": True},
            expected={
                "id": 3,
                **public_note_expected,
                "public": True,
                "forked_from": None,
                "forks": [],
                "owner": {"id": 1, "username": "admin1"},
            },
            endpoint="3",
        ),
        ApiTestCase(
            ["members"],
            expected={
                "id": 3,
                **public_note_expected,
                "public": True,
                "forked_from": None,
                "forks": [],
                "owner": {"id": 1, "username": "admin1"},
            },
            endpoint="3",
        ),
        DeleteApiTestCase(["admin2", "auditor2"], 404, endpoint="1"),
        DeleteApiTestCase(["auditor1", Role.READER], 403, endpoint="1"),
        ApiTestCase(["admin1"], endpoint="1"),
        DeleteApiTestCase(["admin1"], endpoint="1"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 404, endpoint="1"),
        DeleteApiTestCase(["admin2", Role.AUDITOR], 404, endpoint="1"),
        DeleteApiTestCase([Role.READER], 403, endpoint="1"),
        DeleteApiTestCase([Role.ADMIN, "auditor2"], 404, endpoint="2"),
        DeleteApiTestCase([Role.READER], 403, endpoint="2"),
        DeleteApiTestCase(["auditor1"], endpoint="2"),
        DeleteApiTestCase(["admin1"], endpoint="3"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 404, endpoint="2"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 404, endpoint="3"),
    ]

    @cached_property
    def object(self) -> Note:
        return Note.objects.create(**{**private_note, "project": self.project})
