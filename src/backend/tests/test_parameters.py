from functools import cached_property

from parameters.models import InputTechnology, InputVulnerability
from security.authorization.roles import Role
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase, PostApiTestCase
from tools.enums import Intensity

# pytype: disable=wrong-arg-types


class ParameterTest(ApiTest):
    model = None
    valid: dict[str, str] | None = None
    invalid: dict[str, str] | None = None
    setup_entities = ["target"]

    @cached_property
    def cases(self) -> list[ApiTestCase]:
        field = "input_technologies" if self.model == InputTechnology else "input_vulnerabilities"
        return (
            [
                ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
                PostApiTestCase([Role.READER], 403),
                PostApiTestCase([Role.ADMIN, Role.AUDITOR], 400, self.invalid),
                PostApiTestCase([Role.ADMIN, Role.AUDITOR], data=self.valid, expected={"id": 1, **self.valid}),
                PostApiTestCase(["admin1"], data={"target_id": 1, "process_id": 1, field: [1]}, endpoint="/api/tasks/"),
                ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
                PostApiTestCase(
                    ["auditor1"], data={"target_id": 1, "configuration_id": 1, field: [1]}, endpoint="/api/tasks/"
                ),
                ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
                PostApiTestCase(
                    ["auditor1"],
                    data={
                        "target_id": 1,
                        # 26: SearchSploit (per technology)
                        # 27: Metasploit (per CVE)
                        "configuration_id": 26 if self.model == InputTechnology else 27,
                        "intensity": Intensity.SNEAKY.name.capitalize(),
                        field: [1],
                    },
                    endpoint="/api/tasks/",
                ),
                ApiTestCase(["admin2", "auditor2", "reader2"]),
                ApiTestCase(["admin1", "auditor1", "reader1"], expected=[{"id": 1, **self.valid}]),
                ApiTestCase(["admin2", "auditor2", "reader2"], 404, endpoint="1"),
                ApiTestCase(["admin1", "auditor1", "reader1"], expected={"id": 1, **self.valid}, endpoint="1"),
                ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 404, endpoint="2"),
            ]
            if self.valid is not None and self.invalid is not None
            else []
        )

    @cached_property
    def object(self) -> InputTechnology | InputVulnerability | None:
        return self.model.objects.create(**self.valid) if self.model and self.valid else None


class InputTechnologyTest(ParameterTest):
    model = InputTechnology
    endpoint = "/api/parameters/technologies/"
    expected_string = "WordPress - 1.0.0"
    valid = {"name": "WordPress", "version": "1.0.0"}
    invalid = {"name": "Word;Press", "version": "1.0;0"}


class InputVulnerabilityTest(ParameterTest):
    model = InputVulnerability
    endpoint = "/api/parameters/vulnerabilities/"
    expected_string = "CVE-2023-1111"
    valid = {"cve": "CVE-2023-1111"}
    invalid = {"cve": "anything"}
