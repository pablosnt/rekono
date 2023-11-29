from typing import Any

from authentications.enums import AuthenticationType
from target_ports.models import TargetPort
from tests.cases import ApiTestCase
from tests.framework import RekonoTest

target_port1 = {"target": 1, "port": 80, "path": "/webapp/"}
target_port2 = {"target": 1, "port": 22}
authentication = {
    "name": "admin",
    "secret": "admin",
    "type": AuthenticationType.BASIC,
    "target_port": 2,
}
invalid_target_port1 = {"target": 1, "port": 99999999999, "path": "/webapp/"}
invalid_target_port2 = {"target": 1, "port": 443, "path": "/webapp;"}


class TargetPortTest(RekonoTest):
    endpoint = "/api/target-ports/"
    expected_str = "10.10.10.10 - 80"
    cases = [
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected=[],
        ),
        ApiTestCase(
            ["admin2", "auditor2", "reader1", "reader2"], "post", 403, target_port1
        ),
        ApiTestCase(["admin1", "auditor1"], "post", 400, invalid_target_port1),
        ApiTestCase(["admin1", "auditor1"], "post", 400, invalid_target_port2),
        ApiTestCase(
            ["admin1"],
            "post",
            201,
            target_port1,
            expected={"id": 1, "authentication": None, **target_port1},
        ),
        ApiTestCase(["admin1", "auditor1"], "post", 400, target_port1),
        ApiTestCase(["admin2", "auditor2", "reader2"], "get", 200, expected=[]),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected=[{"id": 1, "authentication": None, **target_port1}],
        ),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected={"id": 1, "authentication": None, **target_port1},
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin2", "auditor2", "reader2"], "get", 404, endpoint="{endpoint}1/"
        ),
        ApiTestCase(
            ["auditor1"],
            "post",
            201,
            target_port2,
            expected={
                "id": 2,
                "authentication": None,
                **target_port2,
            },
        ),
        ApiTestCase(
            ["auditor1"],
            "post",
            201,
            authentication,
            expected={
                "id": 1,
                **authentication,
                "secret": "*" * len(authentication["secret"]),
            },
            endpoint="/api/authentications/",
        ),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected={
                "id": 2,
                "authentication": {
                    "id": 1,
                    **authentication,
                    "secret": "*" * len(authentication["secret"]),
                },
                **target_port2,
            },
            endpoint="{endpoint}2/",
        ),
        ApiTestCase(
            ["admin2", "auditor2", "reader2"], "get", 404, endpoint="{endpoint}2/"
        ),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
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
        ApiTestCase(["admin2", "auditor2", "reader2"], "get", 200, expected=[]),
        ApiTestCase(["reader1", "reader2"], "delete", 403, endpoint="{endpoint}1/"),
        ApiTestCase(["admin2", "auditor2"], "delete", 404, endpoint="{endpoint}2/"),
        ApiTestCase(["admin1"], "delete", 204, endpoint="{endpoint}1/"),
        ApiTestCase(["auditor1"], "delete", 204, endpoint="{endpoint}2/"),
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
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            404,
            endpoint="{endpoint}2/",
        ),
    ]

    def setUp(self) -> None:
        super().setUp()
        self._setup_target()

    def _get_object(self) -> Any:
        return TargetPort(target=self.target, port=80)
