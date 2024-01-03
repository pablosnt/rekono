from typing import Any
from notes.models import Note
from tests.cases import ApiTestCase
from tests.framework import ApiTest


private_note = {
    "project": 1,
    "target": None,
    "title": "Title",
    "body": "Important things to remember",
    "tags": ["test"],
    "public": False,
}
public_note = {
    **private_note,
    "public": True,
    "project": None,
    "target": 1,
}
invalid_note = {**private_note, "body": "Invalid;content"}


class NoteTest(ApiTest):
    endpoint = "/api/notes/"
    expected_str = "test - Title"
    cases = [
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected=[],
        ),
        ApiTestCase(
            ["admin2", "auditor2", "reader1", "reader2"], "post", 403, private_note
        ),
        ApiTestCase(
            ["admin2", "auditor2", "reader1", "reader2"], "post", 403, public_note
        ),
        ApiTestCase(["admin1", "auditor1"], "post", 400, invalid_note),
        ApiTestCase(
            ["admin1"],
            "post",
            201,
            private_note,
            {
                "id": 1,
                **private_note,
                "forked_from": None,
                "forks": [],
                "owner": {"id": 1, "username": "admin1"},
            },
        ),
        ApiTestCase(
            ["auditor1"],
            "post",
            201,
            public_note,
            {
                "id": 2,
                **public_note,
                "forked_from": None,
                "forks": [],
                "owner": {"id": 3, "username": "auditor1"},
            },
        ),
        ApiTestCase(["admin2", "auditor2", "reader2"], "get", 200, expected=[]),
        ApiTestCase(
            ["admin1"],
            "get",
            200,
            expected=[
                {
                    "id": 2,
                    **public_note,
                    "forked_from": None,
                    "forks": [],
                    "owner": {"id": 3, "username": "auditor1"},
                },
                {
                    "id": 1,
                    **private_note,
                    "forked_from": None,
                    "forks": [],
                    "owner": {"id": 1, "username": "admin1"},
                },
            ],
        ),
        ApiTestCase(
            ["auditor1", "reader1"],
            "get",
            200,
            expected=[
                {
                    "id": 2,
                    **public_note,
                    "forked_from": None,
                    "forks": [],
                    "owner": {"id": 3, "username": "auditor1"},
                }
            ],
        ),
        ApiTestCase(["reader1", "reader2"], "post", 403, endpoint=f"{endpoint}2/fork/"),
        ApiTestCase(["admin2", "auditor2"], "post", 404, endpoint=f"{endpoint}2/fork/"),
        ApiTestCase(["auditor1"], "post", 404, endpoint=f"{endpoint}1/fork/"),
        ApiTestCase(
            ["admin1"],
            "post",
            201,
            expected={
                "id": 3,
                **public_note,
                "public": False,
                "forked_from": 2,
                "forks": [],
                "owner": {"id": 1, "username": "admin1"},
            },
            endpoint=f"{endpoint}2/fork/",
        ),
        ApiTestCase(
            ["admin1"],
            "get",
            200,
            expected=[
                {
                    "id": 3,
                    **public_note,
                    "public": False,
                    "forked_from": 2,
                    "forks": [],
                    "owner": {"id": 1, "username": "admin1"},
                },
                {
                    "id": 2,
                    **public_note,
                    "forked_from": None,
                    "forks": [3],
                    "owner": {"id": 3, "username": "auditor1"},
                },
                {
                    "id": 1,
                    **private_note,
                    "forked_from": None,
                    "forks": [],
                    "owner": {"id": 1, "username": "admin1"},
                },
            ],
        ),
        ApiTestCase(
            ["auditor1", "reader1"],
            "get",
            200,
            expected=[
                {
                    "id": 2,
                    **public_note,
                    "forked_from": None,
                    "forks": [3],
                    "owner": {"id": 3, "username": "auditor1"},
                },
            ],
        ),
        ApiTestCase(
            ["admin2", "auditor1", "auditor2"], "delete", 404, endpoint="{endpoint}1/"
        ),
        ApiTestCase(["reader1", "reader2"], "delete", 403, endpoint="{endpoint}1/"),
        ApiTestCase(
            ["admin1", "reader1", "reader2"], "delete", 403, endpoint="{endpoint}2/"
        ),
        ApiTestCase(["auditor1"], "delete", 204, endpoint="{endpoint}2/"),
        ApiTestCase(["admin1"], "delete", 204, endpoint="{endpoint}3/"),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            404,
            endpoint="{endpoint}2/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            404,
            endpoint="{endpoint}3/",
        ),
        ApiTestCase(
            ["auditor1", "admin2", "auditor2"],
            "put",
            404,
            public_note,
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["reader1", "reader2"], "put", 403, public_note, endpoint="{endpoint}1/"
        ),
        ApiTestCase(
            ["admin1"],
            "put",
            200,
            public_note,
            {
                "id": 1,
                **public_note,
                "forked_from": None,
                "forks": [],
                "owner": {"id": 1, "username": "admin1"},
            },
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin2", "auditor2", "reader2"], "get", 404, endpoint="{endpoint}1/"
        ),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected={
                "id": 1,
                **public_note,
                "forked_from": None,
                "forks": [],
                "owner": {"id": 1, "username": "admin1"},
            },
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(["admin2", "auditor2"], "delete", 404, endpoint="{endpoint}1/"),
        ApiTestCase(
            ["auditor1", "reader1", "reader2"], "delete", 403, endpoint="{endpoint}1/"
        ),
        ApiTestCase(["admin1"], "delete", 204, endpoint="{endpoint}1/"),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            404,
            endpoint="{endpoint}1/",
        ),
    ]

    def setUp(self) -> None:
        super().setUp()
        self._setup_target()

    def _get_object(self) -> Any:
        return Note.objects.create(**{**private_note, "project": self.project})
