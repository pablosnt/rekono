from functools import cached_property

from authentications.enums import AuthenticationType
from authentications.models import Authentication
from security.authorization.roles import Role
from target_ports.models import TargetPort
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase

# pytype: disable=wrong-arg-types

authentication = {"name": "admin", "secret": "admin", "type": AuthenticationType.BASIC, "target_port": 1}
invalid_authentication1 = {
    "name": "invalid;name",
    "secret": "admin",
    "type": AuthenticationType.TOKEN,
    "target_port": 1,
}
invalid_authentication2 = {
    "name": "admin",
    "secret": "invalid;secret",
    "type": AuthenticationType.BEARER,
    "target_port": 1,
}
invalid_authentication3 = {"name": "newadmin", "secret": "newadmin", "type": AuthenticationType.BASIC, "target_port": 1}


class AuthenticationTest(ApiTest):
    endpoint = "/api/authentications/"
    expected_string = "10.10.10.10 - 80 - admin"
    setup_entities = ["target"]
    cases = [
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 404, endpoint="1"),
        PostApiTestCase(["admin1", "auditor1"], 400, invalid_authentication1),
        PostApiTestCase(["admin1", "auditor1"], 400, invalid_authentication2),
        PostApiTestCase(["admin2", "auditor2", Role.READER], 403, authentication),
        PostApiTestCase(
            ["admin1"],
            data=authentication,
            expected={"id": 1, **authentication, "secret": "*" * len(authentication["secret"])},
        ),
        PostApiTestCase(["admin1", "auditor1"], 400, authentication),
        PostApiTestCase(["admin1", "auditor1"], 400, invalid_authentication3),
        ApiTestCase(["members"], expected=[{"id": 1, **authentication, "secret": "*" * len(authentication["secret"])}]),
        ApiTestCase(
            ["members"],
            expected={"id": 1, **authentication, "secret": "*" * len(authentication["secret"])},
            endpoint="1",
        ),
        ApiTestCase(["not_members"]),
        ApiTestCase(["not_members"], 404, endpoint="1"),
        DeleteApiTestCase([Role.READER], 403, endpoint="1"),
        DeleteApiTestCase(["admin2", "auditor2"], 404, endpoint="1"),
        DeleteApiTestCase(["auditor1"], endpoint="1"),
        DeleteApiTestCase(["admin1"], 404, endpoint="1"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 404, endpoint="1"),
    ]

    def setUp(self) -> None:
        super().setUp()
        # We need a clean target_port without any related authentication
        self.target_port = TargetPort.objects.create(target=self.target, port=80, path=None)

    @cached_property
    def object(self) -> Authentication:
        return Authentication(**{**authentication, "target_port": self.target_port})
