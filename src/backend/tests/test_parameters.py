from typing import Any

from parameters.models import InputTechnology, InputVulnerability
from tests.cases import ApiTestCase
from tests.framework import ApiTest
from tools.enums import Intensity


class ParameterTest(ApiTest):
    model = None
    valid: dict[str, str] | None = None
    invalid: dict[str, str] | None = None

    def setUp(self):
        super().setUp()
        self._setup_target()

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
                ApiTestCase(["reader1", "reader2"], "post", 403),
                ApiTestCase(
                    ["admin1", "admin2", "auditor1", "auditor2"],
                    "post",
                    400,
                    self.invalid,
                ),
                ApiTestCase(
                    ["admin1", "admin2", "auditor1", "auditor2"],
                    "post",
                    201,
                    self.valid,
                    expected={"id": 1, **self.valid},
                ),
                ApiTestCase(
                    ["admin1"],
                    "post",
                    201,
                    {
                        "target_id": 1,
                        "process_id": 1,
                        (
                            "input_technologies"
                            if self.model == InputTechnology
                            else "input_vulnerabilities"
                        ): [1],
                    },
                    endpoint="/api/tasks/",
                ),
                ApiTestCase(
                    ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
                    "get",
                    200,
                    expected=[],
                ),
                ApiTestCase(
                    ["auditor1"],
                    "post",
                    201,
                    {
                        "target_id": 1,
                        "configuration_id": 1,
                        (
                            "input_technologies"
                            if self.model == InputTechnology
                            else "input_vulnerabilities"
                        ): [1],
                    },
                    endpoint="/api/tasks/",
                ),
                ApiTestCase(
                    ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
                    "get",
                    200,
                    expected=[],
                ),
                ApiTestCase(
                    ["auditor1"],
                    "post",
                    201,
                    {
                        "target_id": 1,
                        # 26: SearchSploit (per technology)
                        # 27: Metasploit (per CVE)
                        "configuration_id": 26 if self.model == InputTechnology else 27,
                        "intensity": Intensity.SNEAKY.name.capitalize(),
                        (
                            "input_technologies"
                            if self.model == InputTechnology
                            else "input_vulnerabilities"
                        ): [1],
                    },
                    endpoint="/api/tasks/",
                ),
                ApiTestCase(["admin2", "auditor2", "reader2"], "get", 200, expected=[]),
                ApiTestCase(
                    ["admin1", "auditor1", "reader1"],
                    "get",
                    200,
                    expected=[{"id": 1, **self.valid}],
                ),
                ApiTestCase(
                    ["admin2", "auditor2", "reader2"],
                    "get",
                    404,
                    endpoint="{endpoint}1/",
                ),
                ApiTestCase(
                    ["admin1", "auditor1", "reader1"],
                    "get",
                    200,
                    expected={"id": 1, **self.valid},
                    endpoint="{endpoint}1/",
                ),
                ApiTestCase(
                    ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
                    "get",
                    404,
                    endpoint="{endpoint}2/",
                ),
            ]

    def _get_object(self) -> Any:
        if self.model and self.valid:
            return self.model.objects.create(**self.valid)


class InputTechnologyTest(ParameterTest):
    model = InputTechnology
    endpoint = "/api/parameters/technologies/"
    expected_str = "WordPress - 1.0.0"
    valid = {"name": "WordPress", "version": "1.0.0"}
    invalid = {"name": "Word;Press", "version": "1.0;0"}


class InputVulnerabilityTest(ParameterTest):
    model = InputVulnerability
    endpoint = "/api/parameters/vulnerabilities/"
    expected_str = "CVE-2023-1111"
    valid = {"cve": "CVE-2023-1111"}
    invalid = {"cve": "anything"}
