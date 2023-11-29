from targets.enums import TargetType
from targets.models import Target
from tests.cases import ApiTestCase
from tests.framework import RekonoTest

target1 = {"project": 1, "target": "10.10.10.10"}
target2 = {"project": 1, "target": "scanme.nmap.org"}
target3 = {"project": 1, "target": "10.10.10.1-24"}
target4 = {"project": 1, "target": "10.10.10.0/24"}
target5 = {"project": 1, "target": "8.8.8.8"}
invalid_target = {"project": 1, "target": "domain-not-found"}


class TargetTest(RekonoTest):
    endpoint = "/api/targets/"
    expected_str = target1.get("target")
    cases = [
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected=[],
        ),
        ApiTestCase(["admin2", "auditor2", "reader1", "reader2"], "post", 403, target1),
        ApiTestCase(["admin1", "auditor1"], "post", 400, invalid_target),
        ApiTestCase(
            ["admin1"],
            "post",
            201,
            target1,
            {"id": 1, "type": TargetType.PRIVATE_IP, **target1},
        ),
        ApiTestCase(
            ["auditor1"],
            "post",
            201,
            target2,
            {"id": 2, "type": TargetType.DOMAIN, **target2},
        ),
        ApiTestCase(
            ["auditor1"],
            "post",
            201,
            target3,
            {"id": 3, "type": TargetType.IP_RANGE, **target3},
        ),
        ApiTestCase(
            ["admin1"],
            "post",
            201,
            target4,
            {"id": 4, "type": TargetType.NETWORK, **target4},
        ),
        ApiTestCase(
            ["auditor1"],
            "post",
            201,
            target5,
            {"id": 5, "type": TargetType.PUBLIC_IP, **target5},
        ),
        ApiTestCase(["admin1", "auditor1"], "post", 400, target1),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected=[
                {"id": 5, "type": TargetType.PUBLIC_IP, **target5},
                {"id": 4, "type": TargetType.NETWORK, **target4},
                {"id": 3, "type": TargetType.IP_RANGE, **target3},
                {"id": 2, "type": TargetType.DOMAIN, **target2},
                {"id": 1, "type": TargetType.PRIVATE_IP, **target1},
            ],
        ),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected={"id": 2, "type": TargetType.DOMAIN, **target2},
            endpoint="{endpoint}2/",
        ),
        ApiTestCase(["admin2", "auditor2", "reader2"], "get", 200, expected=[]),
        ApiTestCase(
            ["admin2", "auditor2", "reader2"], "get", 404, endpoint="{endpoint}1/"
        ),
        ApiTestCase(["reader1", "reader2"], "delete", 403, endpoint="{endpoint}1/"),
        ApiTestCase(["admin2", "auditor2"], "delete", 404, endpoint="{endpoint}1/"),
        ApiTestCase(["auditor1"], "delete", 204, endpoint="{endpoint}1/"),
        ApiTestCase(["admin1"], "delete", 404, endpoint="{endpoint}1/"),
        ApiTestCase(["admin1"], "delete", 204, endpoint="{endpoint}2/"),
        ApiTestCase(["auditor1"], "delete", 204, endpoint="{endpoint}3/"),
        ApiTestCase(["admin1"], "delete", 204, endpoint="{endpoint}4/"),
        ApiTestCase(["auditor1"], "delete", 204, endpoint="{endpoint}5/"),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected=[],
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            404,
            endpoint="{endpoint}1/",
        ),
    ]

    def setUp(self) -> None:
        super().setUp()
        self._setup_project()

    def _get_object(self) -> Target:
        return Target.objects.create(
            **{**target1, "project": self.project, "type": TargetType.PRIVATE_IP}
        )
