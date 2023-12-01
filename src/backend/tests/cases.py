import json
from dataclasses import dataclass
from pathlib import Path
from sys import stdout
from typing import Any, Dict, List, Tuple

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
    executors: List[str]
    method: str
    status_code: int
    data: Dict[str, Any] = None
    expected: Dict[str, Any] = None
    endpoint: str = "{endpoint}"
    format: str = "json"

    def _login(self, username: str, password: str) -> Tuple[str, str]:
        response = APIClient().post(
            "/api/security/login/",
            data={"username": username, "password": password},
        )
        content = json.loads((response.content or "{}".encode()).decode())
        return content.get("access"), content.get("refresh")

    def _check_response_content(
        self, expected: Dict[str, Any], response: Dict[str, Any]
    ) -> None:
        for key, value in expected.items():
            if isinstance(value, dict):
                self._check_response_content(value, response.get(key, {}))
            else:
                try:
                    self.tc.assertEqual(value, response.get(key))
                except Exception as ex:
                    print(self.__dict__)
                    input(response)
                    raise ex

    def test_case(self, *args: Any, **kwargs: Any) -> None:
        for executor in self.executors:
            with transaction.atomic():
                credentials = {"username": executor, "password": executor}
                if isinstance(executor, tuple):
                    credentials = {"username": executor[0], "password": executor[1]}
                access, _ = self._login(**credentials)
                api_client = APIClient(HTTP_AUTHORIZATION=f"Bearer {access}")
                response = getattr(api_client, self.method.lower())(
                    self.endpoint.format(endpoint=kwargs["endpoint"]),
                    data=self.data or None,
                    format=self.format,
                )
                try:
                    self.tc.assertEqual(self.status_code, response.status_code)
                except Exception as ex:
                    print(self.__dict__)
                    print(response.status_code)
                    input(response.content)
                    raise ex
                content = json.loads((response.content or "{}".encode()).decode())
                if self.expected is not None:
                    if isinstance(self.expected, dict):
                        self._check_response_content(self.expected, content)
                    elif isinstance(self.expected, list):
                        content = content.get("results", [])
                        self.tc.assertEqual(len(self.expected), len(content))
                        for index, item in enumerate(self.expected):
                            self._check_response_content(item, content[index])
                    elif self.expected:
                        self.tc.assertTrue(False)


@dataclass
class ToolTestCase(RekonoTestCase):
    report: str
    expected: List[Dict[str, Any]] = None

    def _get_parser(
        self, execution: Execution, executor_arguments: List[str], reports: Path
    ) -> BaseParser:
        report = reports / self.report
        executor = execution.configuration.tool.get_executor_class()(execution)
        executor.arguments = executor_arguments
        parser = execution.configuration.tool.get_parser_class()(
            executor,
            report.read_text()
            if not execution.configuration.tool.output_format
            else None,
        )
        if execution.configuration.tool.output_format:
            parser.report = report
        return parser

    def test_case(self, *args: Any, **kwargs: Any) -> None:
        parser = self._get_parser(
            kwargs["execution"],
            kwargs["executor_arguments"],
            kwargs["reports"] / kwargs["tool"].lower().replace(" ", "_"),
        )
        parser.parse()
        try:
            self.tc.assertEqual(len(self.expected or []), len(parser.findings))
        except Exception as ex:
            print(self.expected)
            input(parser.findings)
            raise ex
        for index, finding in enumerate(parser.findings):
            expected = self.expected[index]
            self.tc.assertTrue(isinstance(finding, expected.get("model")))
            for field, value in expected.items():
                if field != "model":
                    self.tc.assertEqual(value, getattr(finding, field))
