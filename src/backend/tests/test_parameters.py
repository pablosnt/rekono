from typing import Any

from parameters.models import InputTechnology, InputVulnerability
from tests.cases import ApiTestCase
from tests.framework import ApiTest


class ParameterTest(ApiTest):
    model = None
    valid = []
    invalid = []

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        if self.valid and self.invalid:
            self.cases = [
                ApiTestCase(
                    ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
                    "get",
                    200,
                    expected=[],
                ),
                ApiTestCase(
                    ["admin2", "auditor2", "reader1", "reader2"],
                    "post",
                    403,
                    self.valid[0],
                ),
                ApiTestCase(
                    ["admin1"],
                    "post",
                    201,
                    self.valid[0],
                    expected={"id": 1, **self.valid[0]},
                ),
                ApiTestCase(["admin1", "auditor1"], "post", 400, self.valid[0]),
                ApiTestCase(["admin2", "auditor2", "reader2"], "get", 200, expected=[]),
                ApiTestCase(
                    ["admin1", "auditor1", "reader1"],
                    "get",
                    200,
                    expected=[{"id": 1, **self.valid[0]}],
                ),
                ApiTestCase(
                    ["admin1", "auditor1", "reader1"],
                    "get",
                    200,
                    expected={"id": 1, **self.valid[0]},
                    endpoint="{endpoint}1/",
                ),
                ApiTestCase(
                    ["admin2", "auditor2", "reader2"],
                    "get",
                    404,
                    endpoint="{endpoint}1/",
                ),
                ApiTestCase(
                    ["auditor1"],
                    "post",
                    201,
                    self.valid[1],
                    expected={"id": 2, **self.valid[1]},
                ),
                ApiTestCase(
                    ["admin1", "auditor1", "reader1"],
                    "get",
                    200,
                    expected={"id": 2, **self.valid[1]},
                    endpoint="{endpoint}2/",
                ),
                ApiTestCase(
                    ["admin2", "auditor2", "reader2"],
                    "get",
                    404,
                    endpoint="{endpoint}2/",
                ),
                ApiTestCase(
                    ["admin1", "auditor1", "reader1"],
                    "get",
                    200,
                    expected=[{"id": 2, **self.valid[1]}, {"id": 1, **self.valid[0]}],
                ),
                ApiTestCase(["admin2", "auditor2", "reader2"], "get", 200, expected=[]),
                ApiTestCase(
                    ["reader1", "reader2"], "delete", 403, endpoint="{endpoint}1/"
                ),
                ApiTestCase(
                    ["admin2", "auditor2"], "delete", 404, endpoint="{endpoint}2/"
                ),
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
            self.cases.extend(
                [
                    ApiTestCase(["admin1", "auditor1"], "post", 400, i)
                    for i in self.invalid
                ]
            )

    def setUp(self) -> None:
        super().setUp()
        self._setup_target()

    def _get_object(self) -> Any:
        if self.model and self.valid:
            return self.model.objects.create(**{**self.valid[0], "target": self.target})


class InputTechnologyTest(ParameterTest):
    model = InputTechnology
    endpoint = "/api/parameters/technologies/"
    expected_str = f"10.10.10.10 - WordPress - 1.0.0"
    valid = [
        {"target": 1, "name": "WordPress", "version": "1.0.0"},
        {"target": 1, "name": "Joomla", "version": "1.0.0"},
    ]
    invalid = [
        {"target": 1, "name": "Word;Press", "version": "1.0.0"},
        {"target": 1, "name": "WordPress", "version": "1.0;0"},
    ]


class InputVulnerabilityTest(ParameterTest):
    model = InputVulnerability
    endpoint = "/api/parameters/vulnerabilities/"
    expected_str = f"10.10.10.10 - CVE-2023-1111"
    valid = [
        {"target": 1, "cve": "CVE-2023-1111"},
        {"target": 1, "cve": "CVE-2023-1112"},
    ]
    invalid = [{"target": 1, "cve": "anything"}]
