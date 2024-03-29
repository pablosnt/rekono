from typing import Any

from http_headers.models import HttpHeader
from tests.cases import ApiTestCase
from tests.framework import ApiTest

data = {"key": "User-Agent", "value": "Firefox"}
new_data = {**data, "value": "Chrome"}
target = {"target": 1, **data}
user = {"user": 4, **data}
invalid_data = {"key": "User;Agent", "value": "Fire;fox"}


class HttpHeaderTest(ApiTest):
    endpoint = "/api/http-headers/"
    expected_str = "10.10.10.10 - User-Agent"
    cases = [
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected=[],
        ),
        ApiTestCase(["admin2", "auditor2", "reader1", "reader2"], "post", 403, target),
        ApiTestCase(["auditor1"], "post", 400, {**target, **invalid_data}),
        ApiTestCase(
            ["auditor1"], "post", 201, target, {"id": 1, "user": None, **target}
        ),
        ApiTestCase(["admin1", "auditor1"], "post", 400, target),
        ApiTestCase(["auditor1", "auditor2", "reader1", "reader2"], "post", 403, data),
        ApiTestCase(
            ["admin2"],
            "post",
            201,
            data,
            {"id": 2, "target": None, "user": None, **data},
        ),
        ApiTestCase(["admin1"], "post", 400, data),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "reader1", "reader2"], "post", 403, user
        ),
        ApiTestCase(["auditor2"], "post", 201, user, {"id": 3, "target": None, **user}),
        ApiTestCase(["auditor2"], "post", 400, user),
        ApiTestCase(
            ["admin2", "reader2"],
            "get",
            200,
            expected=[{"id": 2, "target": None, "user": None, **data}],
        ),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected=[
                {"id": 2, "target": None, "user": None, **data},
                {"id": 1, "user": None, **target},
            ],
        ),
        ApiTestCase(
            ["auditor2"],
            "get",
            200,
            expected=[
                {"id": 3, "target": None, **user},
                {"id": 2, "target": None, "user": None, **data},
            ],
        ),
        ApiTestCase(
            ["auditor1", "auditor2", "reader1", "reader2"],
            "put",
            403,
            new_data,
            endpoint="{endpoint}2/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1"],
            "put",
            404,
            new_data,
            endpoint="{endpoint}3/",
        ),
        ApiTestCase(
            ["admin1"],
            "put",
            200,
            new_data,
            {"id": 2, "target": None, "user": None, **new_data},
            "{endpoint}2/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected={"id": 2, "target": None, "user": None, **new_data},
            endpoint="{endpoint}2/",
        ),
        ApiTestCase(["auditor1"], "delete", 204, endpoint="{endpoint}1/"),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"], "get", 404, endpoint="{endpoint}1/"
        ),
    ]

    def setUp(self) -> None:
        super().setUp()
        self._setup_target()

    def _get_object(self) -> Any:
        return HttpHeader(**{"target": self.target, "user": None, **data})
