import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Type

from authentications.models import Authentication
from django.db import transaction
from django.test import TestCase
from executions.models import Execution
from rest_framework.test import APIClient
from tools.parsers.base import BaseParser


class RekonoTestCase:
    tc = TestCase()

    def test_case(self) -> None:
        pass


@dataclass
class ApiTestCase(RekonoTestCase):
    executors: list[str]
    method: str
    status_code: int
    data: Optional[dict[str, Any]] = None
    expected: Optional[dict[str, Any]] = None
    endpoint: str = "{endpoint}"
    format: str = "json"

    def _login(self, username: str, password: str) -> tuple[str, str]:
        content = json.loads(
            (
                APIClient()
                .post(
                    "/api/security/login/",
                    data={"username": username, "password": password},
                )
                .content
                or "{}".encode()
            ).decode()
        )
        return content.get("access"), content.get("refresh")

    def _check_response_content(
        self, expected: dict[str, Any], response: dict[str, Any]
    ) -> None:
        for key, value in expected.items():
            if isinstance(value, dict):
                self._check_response_content(value, response.get(key, {}))
            elif isinstance(value, list):
                self.tc.assertEqual(len(value), len(response.get(key, [])))
                if len(value) > 0 and isinstance(value[0], dict):
                    for index, item in enumerate(value):
                        self._check_response_content(item, response.get(key, [])[index])
            else:
                self.tc.assertEqual(value, response.get(key))

    def test_case(self, *args: Any, **kwargs: Any) -> None:
        for executor in self.executors:
            with transaction.atomic():
                credentials = {"username": executor, "password": executor}
                if isinstance(executor, tuple):
                    credentials = {"username": executor[0], "password": executor[1]}
                access, _ = self._login(**credentials)
                api_client = APIClient(HTTP_AUTHORIZATION=f"Bearer {access}")
                response = getattr(api_client, self.method.lower())(
                    self.endpoint.format(endpoint=kwargs.get("endpoint", "")),
                    data=self.data,
                    format=self.format,
                )
                try:
                    self.tc.assertEqual(self.status_code, response.status_code)
                except Exception as ex:
                    print(self.endpoint)
                    input(response.content)
                    raise ex
                if self.expected is not None:
                    content = json.loads((response.content or "{}".encode()).decode())
                    if isinstance(self.expected, dict):
                        self._check_response_content(self.expected, content)
                    elif isinstance(self.expected, list):
                        content = content.get("results", [])
                        try:
                            self.tc.assertEqual(len(self.expected), len(content))
                        except Exception as ex:
                            print(self.__dict__)
                            input(response.content)
                            raise ex
                        for index, item in enumerate(self.expected):
                            self._check_response_content(item, content[index])
                    elif self.expected:
                        self.tc.assertTrue(False)


@dataclass
class ToolTestCase(RekonoTestCase):
    report: str
    expected: Optional[list[dict[str, Any]]] = None

    def _get_parser(
        self,
        execution: Execution,
        authentication: Authentication,
        executor_arguments: list[str],
        reports: Path,
    ) -> BaseParser:
        report = reports / self.report
        executor = execution.configuration.tool.get_executor_class()(execution)
        executor.authentication = authentication
        executor.arguments = executor_arguments
        parser = execution.configuration.tool.get_parser_class()(
            executor,
            (
                report.read_text()
                if not execution.configuration.tool.output_format
                else None
            ),
        )
        if execution.configuration.tool.output_format:
            parser.report = report
        return parser

    def test_case(self, *args: Any, **kwargs: Any) -> None:
        parser = self._get_parser(
            kwargs["execution"],
            kwargs["authentication"],
            kwargs["executor_arguments"],
            kwargs["reports"] / kwargs["tool"].lower().replace(" ", "_"),
        )
        parser.parse()
        self.tc.assertEqual(len(self.expected or []), len(parser.findings))
        if self.expected:
            for index, finding in enumerate(parser.findings):
                expected = self.expected[index]
                self.tc.assertTrue(
                    isinstance(finding, expected.get("model", Type[None]))
                )
                for field, value in expected.items():
                    if field != "model":
                        self.tc.assertEqual(value, getattr(finding, field))
