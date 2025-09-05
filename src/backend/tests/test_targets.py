from functools import cached_property

from security.authorization.roles import Role
from targets.enums import TargetType
from targets.models import Target
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase
from tests.framework.data import TestingDataMixin

# pytype: disable=wrong-arg-types

target1 = {"project": 1, "target": "10.10.10.10"}
target2 = {"project": 1, "target": "scanme.nmap.org"}
target3 = {"project": 1, "target": "10.10.10.1-24"}
target4 = {"project": 1, "target": "10.10.10.0/24"}
target5 = {"project": 1, "target": "8.8.8.8"}
invalid_target = {"project": 1, "target": "domain-not-found"}


class TargetTest(ApiTest, TestingDataMixin):
    endpoint = "/api/targets/"
    expected_string = target1.get("target")
    setup_entities = ["project"]
    cases = [
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
        PostApiTestCase(["admin2", "auditor2", "reader1", "reader2"], 403, target1),
        PostApiTestCase(["admin1", "auditor1"], 400, invalid_target),
        PostApiTestCase(["admin1"], data=target1, expected={"id": 1, "type": TargetType.PRIVATE_IP, **target1}),
        PostApiTestCase(["auditor1"], data=target2, expected={"id": 2, "type": TargetType.DOMAIN, **target2}),
        PostApiTestCase(["auditor1"], data=target3, expected={"id": 3, "type": TargetType.IP_RANGE, **target3}),
        PostApiTestCase(["admin1"], data=target4, expected={"id": 4, "type": TargetType.NETWORK, **target4}),
        PostApiTestCase(["auditor1"], data=target5, expected={"id": 5, "type": TargetType.PUBLIC_IP, **target5}),
        PostApiTestCase(["admin1", "auditor1"], 400, target1),
        ApiTestCase(
            ["members"],
            expected=[
                {"id": 5, "type": TargetType.PUBLIC_IP, **target5},
                {"id": 4, "type": TargetType.NETWORK, **target4},
                {"id": 3, "type": TargetType.IP_RANGE, **target3},
                {"id": 2, "type": TargetType.DOMAIN, **target2},
                {"id": 1, "type": TargetType.PRIVATE_IP, **target1},
            ],
        ),
        ApiTestCase(["members"], expected={"id": 2, "type": TargetType.DOMAIN, **target2}, endpoint="2"),
        ApiTestCase(["not_members"]),
        ApiTestCase(["not_members"], 404, endpoint="1"),
        DeleteApiTestCase(["reader1", "reader2"], 403, endpoint="1"),
        DeleteApiTestCase(["admin2", "auditor2"], 404, endpoint="1"),
        DeleteApiTestCase(["auditor1"], endpoint="1"),
        DeleteApiTestCase(["admin1"], 404, endpoint="1"),
        DeleteApiTestCase(["admin1"], endpoint="2"),
        DeleteApiTestCase(["auditor1"], endpoint="3"),
        DeleteApiTestCase(["admin1"], endpoint="4"),
        DeleteApiTestCase(["auditor1"], endpoint="5"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 404, endpoint="1"),
    ]

    @cached_property
    def object(self) -> Target:
        self.setup_target()
        return self.target
