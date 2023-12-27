from typing import Any

from authentications.enums import AuthenticationType
from authentications.models import Authentication
from target_ports.models import TargetPort
from tests.cases import ApiTestCase
from tests.framework import ApiTest

authentication = {
    "name": "admin",
    "secret": "admin",
    "type": AuthenticationType.BASIC,
    "target_port": 1,
}
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
invalid_authentication3 = {
    "name": "newadmin",
    "secret": "newadmin",
    "type": AuthenticationType.BASIC,
    "target_port": 1,
}


class AuthenticationTest(ApiTest):
    endpoint = "/api/authentications/"
    expected_str = "10.10.10.10 - 80 - admin"
    cases = [
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
        ApiTestCase(["admin1", "auditor1"], "post", 400, invalid_authentication1),
        ApiTestCase(["admin1", "auditor1"], "post", 400, invalid_authentication2),
        ApiTestCase(
            ["admin2", "auditor2", "reader1", "reader2"], "post", 403, authentication
        ),
        ApiTestCase(
            ["admin1"],
            "post",
            201,
            authentication,
            {"id": 1, **authentication, "secret": "*" * len(authentication["secret"])},
        ),
        ApiTestCase(["admin1", "auditor1"], "post", 400, authentication),
        ApiTestCase(["admin1", "auditor1"], "post", 400, invalid_authentication3),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected=[
                {
                    "id": 1,
                    **authentication,
                    "secret": "*" * len(authentication["secret"]),
                }
            ],
        ),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected={
                "id": 1,
                **authentication,
                "secret": "*" * len(authentication["secret"]),
            },
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(["admin2", "auditor2", "reader2"], "get", 200, expected=[]),
        ApiTestCase(
            ["admin2", "auditor2", "reader2"], "get", 404, endpoint="{endpoint}1/"
        ),
        ApiTestCase(["reader1", "reader2"], "delete", 403, endpoint="{endpoint}1/"),
        ApiTestCase(["admin2", "auditor2"], "delete", 404, endpoint="{endpoint}1/"),
        ApiTestCase(["auditor1"], "delete", 204, endpoint="{endpoint}1/"),
        ApiTestCase(["admin1"], "delete", 404, endpoint="{endpoint}1/"),
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
        self._setup_target()
        self.target_port = TargetPort.objects.create(
            target=self.target, port=80, path=None
        )
        TargetPort.objects.create(target=self.target, port=22, path=None)
        TargetPort.objects.create(target=self.target, port=443, path=None)

    def _get_object(self) -> Any:
        return Authentication(**{**authentication, "target_port": self.target_port})
