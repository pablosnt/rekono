from functools import cached_property

from django.test import TestCase

from http_headers.models import HttpHeader
from security.authorization.roles import Role
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase, PutApiTestCase
from tests.framework.data import SetupProject
from tools.models import Input

# pytype: disable=wrong-arg-types

valid_data = {"key": "User-Agent", "value": "Firefox", "user": None, "target": None}
new_data = {**valid_data, "value": "Chrome"}
target = {**valid_data, "target": 1}
user = {**valid_data, "user": 4}
invalid_data = {**valid_data, "key": "User;Agent", "value": "Fire;fox"}


class HttpHeaderTest(ApiTest, TestCase):
    endpoint = "/api/http-headers/"
    expected_string = "10.10.10.10 - User-Agent"
    data = [SetupProject(executions_per_task=0)]
    cases = [
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
        PostApiTestCase(["admin2", "auditor2", Role.READER], 403, target),
        PostApiTestCase(["auditor1"], 400, {**target, **invalid_data}),
        PostApiTestCase(["auditor1"], data=target, expected={"id": 1, **target}),
        PostApiTestCase(["admin1", "auditor1"], 400, target),
        PostApiTestCase(["auditor1", "auditor2", Role.READER], 403, valid_data),
        PostApiTestCase(["admin2"], data=valid_data, expected={"id": 2, **valid_data}),
        PostApiTestCase(["admin1"], 400, valid_data),
        PostApiTestCase([Role.ADMIN, "auditor1", Role.READER], 403, user),
        PostApiTestCase(["auditor2"], data=user, expected={"id": 3, **user}),
        PostApiTestCase(["auditor2"], 400, user),
        ApiTestCase(["admin2"], expected=[{"id": 2, **valid_data}]),
        ApiTestCase(["auditor2"], expected=[{"id": 3, **user}, {"id": 2, **valid_data}]),
        ApiTestCase(["admin1", "auditor1"], expected=[{"id": 2, **valid_data}, {"id": 1, **target}]),
        PutApiTestCase([Role.AUDITOR, Role.READER], 403, new_data, endpoint="2"),
        PutApiTestCase([Role.ADMIN, "auditor1"], 404, new_data, endpoint="3"),
        PutApiTestCase(["admin1"], data=new_data, expected={"id": 2, **new_data}, endpoint="2"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR], expected={"id": 2, **new_data}, endpoint="2"),
        DeleteApiTestCase(["auditor1"], endpoint="1"),
        ApiTestCase(["admin1", "auditor1"], 404, endpoint="1"),
        DeleteApiTestCase([Role.AUDITOR, Role.READER], 403, endpoint="2"),
        DeleteApiTestCase(["admin1"], endpoint="2"),
        DeleteApiTestCase([Role.ADMIN, "auditor1"], 404, endpoint="3"),
        DeleteApiTestCase(["auditor2"], endpoint="3"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], expected=[]),
    ]

    def test_base_input_filter(self) -> None:
        header = HttpHeader(key="Authorization")
        self.assertTrue(header.filter(Input(filter="authorization")))
        self.assertFalse(header.filter(Input(filter="auth")))
        self.assertFalse(header.filter(Input(filter="cookie")))
        # OR
        self.assertTrue(header.filter(Input(filter="cookie or authorization")))
        # Negation
        self.assertTrue(header.filter(Input(filter="!cookie")))
        self.assertFalse(header.filter(Input(filter="!authorization")))
        # Empty filter
        self.assertTrue(header.filter(Input(filter="")))

    @cached_property
    def object(self) -> HttpHeader:
        return HttpHeader(**{**valid_data, "target": self.target, "user": None})

    def test_no_relationships(self) -> None:
        self.assertEqual(0, len(self.object.input_type.parent_input_types))
        self.assertEqual(0, len(self.object.input_type.children_input_types))
