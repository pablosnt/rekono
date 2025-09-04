from functools import cached_property

from http_headers.models import HttpHeader
from security.authorization.roles import Role
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase, PutApiTestCase

# pytype: disable=wrong-arg-types

data = {"key": "User-Agent", "value": "Firefox", "user": None, "target": None}
new_data = {**data, "value": "Chrome"}
target = {**data, "target": 1}
user = {**data, "user": 4}
invalid_data = {**data, "key": "User;Agent", "value": "Fire;fox"}


class HttpHeaderTest(ApiTest):
    endpoint = "/api/http-headers/"
    expected_string = "10.10.10.10 - User-Agent"
    setup_entities = ["target"]
    cases = [
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
        PostApiTestCase(["admin2", "auditor2", Role.READER], 403, target),
        PostApiTestCase(["auditor1"], 400, {**target, **invalid_data}),
        PostApiTestCase(["auditor1"], data=target, expected={"id": 1, **target}),
        PostApiTestCase(["admin1", "auditor1"], 400, target),
        PostApiTestCase(["auditor1", "auditor2", Role.READER], 403, data),
        PostApiTestCase(["admin2"], data=data, expected={"id": 2, **data}),
        PostApiTestCase(["admin1"], 400, data),
        PostApiTestCase([Role.ADMIN, "auditor1", Role.READER], 403, user),
        PostApiTestCase(["auditor2"], data=user, expected={"id": 3, **user}),
        PostApiTestCase(["auditor2"], 400, user),
        ApiTestCase(["admin2"], expected=[{"id": 2, **data}]),
        ApiTestCase(["auditor2"], expected=[{"id": 3, **user}, {"id": 2, **data}]),
        ApiTestCase(["admin1", "auditor1"], expected=[{"id": 2, **data}, {"id": 1, **target}]),
        PutApiTestCase([Role.AUDITOR, Role.READER], 403, new_data, endpoint="2"),
        PutApiTestCase([Role.ADMIN, "auditor1"], 404, new_data, endpoint="3"),
        PutApiTestCase(["admin1"], data=new_data, expected={"id": 2, **new_data}, endpoint="2"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR], expected={"id": 2, **new_data}, endpoint="2"),
        DeleteApiTestCase(["auditor1"], endpoint="1"),
        ApiTestCase(["admin1", "auditor1"], 404, endpoint="1"),
    ]

    @cached_property
    def object(self) -> HttpHeader:
        return HttpHeader(**{**data, "target": self.target, "user": None})
