import json
from dataclasses import dataclass
from typing import Any, Type

from django.db import transaction
from django.test import TestCase
from rest_framework.test import APIClient

from security.authorization.roles import Role
from users.models import User

# pytype: disable=attribute-error


class RekonoTestCase:
    def test_case(self, test_case_number: int, test_case: TestCase) -> None:
        pass


@dataclass
class ApiTestCase(RekonoTestCase):
    executors: list[str | Role] | None = None
    status_code: int = 200
    data: dict[str, Any] | None = None
    expected: dict[str, Any] | None = None
    endpoint: str = "{endpoint}"
    format: str = "json"
    method: str = "GET"

    def assertExpected(
        self, location: str, test_case: TestCase, response: dict[str, Any], expected: Any | None = None, root: str = ""
    ) -> None:
        expected = expected if expected is None else self.expected
        if expected is None:
            return
        if root:
            location = f"{location} - {root}"
        if isinstance(expected, list) and not isinstance(response, list):
            response = response.get("results", [])
        test_case.assertEqual(
            type(expected),
            type(response),
            msg=f"[{location}] Expected type '{type(expected)}' doesn't match '{type(response)}'",
        )
        if isinstance(expected, list):
            test_case.assertEqual(
                len(expected),
                len(response),
                msg=f"[{location}] Number of expected items #{len(expected)} doesn't match #{len(response)}",
            )
            for index, item in enumerate(expected):
                self.assertExpected(
                    location, test_case, response[index], item, f"{root}[#{index}]" if root else f"#{index}"
                )
        elif isinstance(expected, dict):
            for key, value in expected.items():
                if isinstance(value, dict) or isinstance(value, list):
                    self.assertExpected(location, test_case, response[key], value, f"{root}__{key}" if root else key)
                else:
                    test_case.assertEqual(
                        value,
                        response[key],
                        msg=f"[{location}] Expected '{key}' '{value}' doesn't match '{response[key]}'",
                    )
        else:
            test_case.assertEqual(
                expected, response, msg=f"[{location}] Expected '{expected}' doesn't match '{response}'"
            )

    def test_case(self, test_case_number: int, test_case: TestCase, base_endpoint: str | None = None) -> None:
        for executors_or_role in self.executors or [None]:
            executor_list = [None]
            if executors_or_role is not None:
                if isinstance(executors_or_role, Role):
                    executor_list = test_case.users[executors_or_role]
                elif hasattr(test_case, executors_or_role):
                    if isinstance(getattr(test_case, executors_or_role), User):
                        executor_list = [getattr(test_case, executors_or_role)]
                    elif isinstance(getattr(test_case, executors_or_role), list):
                        executor_list = getattr(test_case, executors_or_role)
            for executor in executor_list:
                with transaction.atomic():
                    client = APIClient()
                    location = f"TestCase#{test_case_number}"
                    if executor:
                        location += f" - @{executor.username}"
                        client.force_authenticate(User.objects.get(pk=executor.id))
                    if "{endpoint}" in self.endpoint:
                        endpoint = self.endpoint.format(endpoint=base_endpoint)
                    elif base_endpoint not in self.endpoint and not self.endpoint.startswith("/api/"):
                        endpoint = base_endpoint + self.endpoint
                    else:
                        endpoint = self.endpoint
                    if endpoint[-1] != "/" and "?" not in endpoint:
                        endpoint += "/"
                    location += f" - {self.method.upper()} {endpoint}"
                    response = getattr(client, self.method.lower())(endpoint, data=self.data, format=self.format)
                    test_case.assertEqual(
                        self.status_code,
                        response.status_code,
                        msg=f"[{location}] Expected status code {self.status_code} doesn't match {response.status_code}{f': {response.content}' if hasattr(response, 'content') else ''}",
                    )
                    if self.expected:
                        self.assertExpected(
                            location, test_case, json.loads((response.content or "{}".encode()).decode())
                        )


@dataclass
class PostApiTestCase(ApiTestCase):
    method = "POST"
    status_code: int = 201


class PutApiTestCase(ApiTestCase):
    method = "PUT"


@dataclass
class DeleteApiTestCase(ApiTestCase):
    method = "DELETE"
    status_code: int = 204


@dataclass
class ParserTestCase(RekonoTestCase):
    report: str
    expected: list[dict[str, Any]] | None = None

    def test_case(self, test_case_number: int, test_case: TestCase) -> None:
        executor = test_case.execution.configuration.tool.executor_class(test_case.execution)
        executor.authentication = test_case.authentication
        executor.arguments = test_case.arguments
        report = (
            test_case.data_dir
            / "reports"
            / test_case.execution.configuration.tool.name.lower().replace(" ", "_")
            / self.report
        )
        if test_case.execution.configuration.tool.output_format:
            executor.report = report
            output = None
        else:
            output = report.read_text()
        parser = test_case.execution.configuration.tool.parser_class(executor, output)
        parser.findings = []
        parser.parse()
        location = f"TestCase#{test_case_number}"
        test_case.assertEqual(
            len(self.expected or []),
            len(parser.findings),
            msg=f"[{location}] Number of expected findings #{len(self.expected or [])} doesn't match #{len(parser.findings)}",
        )
        if self.expected:
            for index, finding in enumerate(parser.findings):
                location += f" - #{index}"
                test_case.assertEqual(
                    finding.__class__,
                    self.expected[index].get("model", Type[None]),
                    msg=f"[{location}] Expected finding type '{finding.__class__}' doesn't match '{self.expected[index].get('model', Type[None])}'",
                )
                for field, value in self.expected[index].items():
                    if field != "model":
                        location += f" - {finding.__class__}"
                        test_case.assertEqual(
                            value,
                            getattr(finding, field),
                            msg=f"[{location}] Expected '{field}' '{value}' doesn't match '{getattr(finding, field)}'",
                        )
