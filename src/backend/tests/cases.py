import json
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from django.db import transaction
from django.test import TestCase
from findings.framework.models import Finding
from rest_framework.test import APIClient


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
    tool: str
    report: str
    expected: List[Finding]
    stdout: bool

    def test_case(self, *args: Any, **kwargs: Any) -> None:
        return super().test_case()
