from functools import cached_property

from authentications.enums import AuthenticationType
from security.authorization.roles import Role
from target_ports.models import TargetPort
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase

# pytype: disable=wrong-arg-types

target_port1 = {"target": 1, "port": 80, "path": "/webapp/"}
target_port2 = {"target": 1, "port": 22}
invalid_target_port1 = {"target": 1, "port": 99999999999, "path": "/webapp/"}
invalid_target_port2 = {"target": 1, "port": 443, "path": "/webapp;"}
authentication = {"name": "admin", "secret": "admin", "type": AuthenticationType.BASIC, "target_port": 2}


class TargetPortTest(ApiTest):
    endpoint = "/api/target-ports/"
    expected_string = "10.10.10.10 - 80"
    setup_entities = ["target"]
    cases = [
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
        PostApiTestCase(["admin2", "auditor2", Role.READER], 403, target_port1),
        PostApiTestCase(["admin1", "auditor1"], 400, invalid_target_port1),
        PostApiTestCase(["admin1", "auditor1"], 400, invalid_target_port2),
        PostApiTestCase(["admin1"], data=target_port1, expected={"id": 1, "authentication": None, **target_port1}),
        PostApiTestCase(["admin1", "auditor1"], 400, target_port1),
        ApiTestCase(["not_members"]),
        ApiTestCase(["members"], expected=[{"id": 1, "authentication": None, **target_port1}]),
        ApiTestCase(["members"], expected={"id": 1, "authentication": None, **target_port1}, endpoint="1"),
        ApiTestCase(["not_members"], 404, endpoint="1"),
        PostApiTestCase(["auditor1"], data=target_port2, expected={"id": 2, "authentication": None, **target_port2}),
        PostApiTestCase(
            ["auditor1"],
            data=authentication,
            expected={"id": 1, **authentication, "secret": "*" * len(authentication["secret"])},
            endpoint="/api/authentications/",
        ),
        ApiTestCase(
            ["members"],
            expected={
                "id": 2,
                "authentication": {
                    "id": 1,
                    **authentication,
                    "secret": "*" * len(authentication["secret"]),
                },
                **target_port2,
            },
            endpoint="2",
        ),
        ApiTestCase(["not_members"], 404, endpoint="2"),
        ApiTestCase(
            ["members"],
            expected=[
                {
                    "id": 2,
                    "authentication": {
                        "id": 1,
                        **authentication,
                        "secret": "*" * len(authentication["secret"]),
                    },
                    **target_port2,
                },
                {"id": 1, "authentication": None, **target_port1},
            ],
        ),
        ApiTestCase(["not_members"]),
        DeleteApiTestCase([Role.READER], 403, endpoint="1"),
        DeleteApiTestCase(["admin2", "auditor2"], 404, endpoint="2"),
        DeleteApiTestCase(["admin1"], endpoint="1"),
        DeleteApiTestCase(["auditor1"], endpoint="2"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 404, endpoint="1"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 404, endpoint="2"),
    ]

    @cached_property
    def object(self) -> TargetPort:
        return TargetPort(target=self.target, port=80)
