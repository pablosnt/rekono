import base64
from functools import cached_property

from django.test import TestCase

from authentications.enums import AuthenticationType
from authentications.models import Authentication
from security.authorization.roles import Role
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase

# pytype: disable=wrong-arg-types

authentication = {"name": "admin", "secret": "admin", "type": AuthenticationType.BASIC, "target_port": 1}
invalid_authentication1 = {
    **authentication,
    "name": "invalid;name",
    "type": AuthenticationType.TOKEN,
}
invalid_authentication2 = {**authentication, "secret": "invalid;secret", "type": AuthenticationType.BEARER}
invalid_authentication3 = {**authentication, "name": "newadmin", "secret": "newadmin"}
env_injection_authentication = {**authentication, "secret": "admin LD_PRELOAD=/tmp/evil.so"}


class AuthenticationTest(ApiTest, TestCase):
    endpoint = "/api/authentications/"
    expected_string = "10.10.10.10 - 80 - admin"
    target_parameters_flag = True
    cases = [
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 404, endpoint="1"),
        PostApiTestCase(["admin1", "auditor1"], 400, invalid_authentication1),
        PostApiTestCase(["admin1", "auditor1"], 400, invalid_authentication2),
        PostApiTestCase(["admin1", "auditor1"], 400, env_injection_authentication),
        PostApiTestCase(["admin2", "auditor2", Role.READER], 403, authentication),
        PostApiTestCase(
            ["admin1"],
            data=authentication,
            expected={"id": 2, **authentication, "secret": "*" * len(authentication["secret"])},
        ),
        PostApiTestCase(["admin1", "auditor1"], 400, authentication),
        PostApiTestCase(["admin1", "auditor1"], 400, invalid_authentication3),
        ApiTestCase(["members"], expected=[{"id": 2, **authentication, "secret": "*" * len(authentication["secret"])}]),
        ApiTestCase(
            ["members"],
            expected={"id": 2, **authentication, "secret": "*" * len(authentication["secret"])},
            endpoint="2",
        ),
        ApiTestCase(["not_members"]),
        ApiTestCase(["not_members"], 404, endpoint="2"),
        DeleteApiTestCase([Role.READER], 403, endpoint="2"),
        DeleteApiTestCase(["admin2", "auditor2"], 404, endpoint="2"),
        DeleteApiTestCase(["auditor1"], endpoint="2"),
        DeleteApiTestCase(["admin1"], 404, endpoint="2"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 404, endpoint="2"),
    ]

    @cached_property
    def object(self) -> Authentication:
        return Authentication(**{**authentication, "target_port": self.targetport})

    def test_token(self) -> None:
        self.assertEqual(base64.b64encode("admin:admin".encode()).decode(), self.object.token)

    def setUp(self):
        super().setUp()
        Authentication.objects.all().delete()

    def test_no_relationships(self) -> None:
        self.assertEqual(0, len(self.object.input_type.parent_input_types))
        self.assertEqual(0, len(self.object.input_type.children_input_types))
