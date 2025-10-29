import base64
from typing import Any
from unittest import mock

from django.test import TestCase

from authentications.enums import AuthenticationType
from findings.enums import OSINTDataType, TransportProtocol
from findings.models import Port
from settings.models import Settings
from target_ports.models import TargetPort
from tests.framework import BaseTest
from tests.framework.data import SetupProject

# pytype: disable=attribute-error


def get_url(self, target: Any, host: str, port: int | None = None, endpoint: str | None = None, *args: Any) -> str:
    return f"http://{host}" + (f":{port}" if port else "") + (endpoint or "/")


class ToolExecutorTest(BaseTest, TestCase):
    data = [SetupProject(osint_fields=[{"data": "10.10.10.11", "data_type": OSINTDataType.IP}])]
    fake_tool_flag = True
    target_parameters_flag = True
    task_parameters_flag = True

    def setUp(self) -> None:
        super().setUp()
        self.execution.configuration = self.fake_configuration
        self.execution.save(update_fields=["configuration"])
        self.executor = self.fake_tool.executor_class(self.execution)

    def _test_environment(self, expected: dict[str, Any]) -> None:
        environment = self.executor.get_environment()
        for key, value in expected.items():
            self.assertIsNotNone(environment.get(key))
            self.assertEqual(value, environment.get(key))

    def test_get_environment(self) -> None:
        expected_env = {"KEY1": "value1", "KEY2": "value2"}
        self.executor.arguments = [f"{k}={v}" for k, v in expected_env.items()] + [self.fake_tool.command, "--foo=bar"]
        self._test_environment(expected_env)

    def test_get_environment_with_proxies(self) -> None:
        proxy = "10.10.10.10:80"
        expected_env = {f"{key.upper()}_PROXY": proxy for key in ["all", "http", "https", "ftp", "no"]}
        settings = Settings.objects.first()
        for field, value in expected_env.items():
            setattr(settings, field.lower(), value)
        settings.save(update_fields=[f.lower() for f in expected_env.keys()])
        self.executor.arguments = [self.fake_tool.command, "--foo=bar"]
        self._test_environment(expected_env)

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_get_arguments_only_findings(self) -> None:
        expected = "-p 10.10.10.11 -p http://10.10.10.10:80/index.html -p 80 -p /index.html -p WordPress -p admin -p CVE-2025-3010 -p ReverseShell 10 -p root"
        self.assertEqual(expected, " ".join(self.executor.get_arguments(self.findings, [], [], [], [])))
        self.vulnerability.technology = None
        self.vulnerability.port = self.port
        self.vulnerability.save(update_fields=["port", "technology"])
        self.exploit.vulnerability = None
        self.exploit.technology = self.technology
        self.exploit.save(update_fields=["vulnerability", "technology"])
        self.assertEqual(expected, " ".join(self.executor.get_arguments(self.findings, [], [], [], [])))

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_get_arguments_only_required_findings(self) -> None:
        self.assertEqual(
            "-p 10.10.10.10 -p http://10.10.10.10:80/ -p 80 -p WordPress -p CVE-2025-3010 -p root",
            " ".join(
                self.executor.get_arguments([self.host, self.port, self.technology, self.vulnerability], [], [], [], [])
            ),
        )

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_get_arguments_multiple_ports(self) -> None:
        new_port = Port.objects.create(host=self.host, port=443, service="http", protocol=TransportProtocol.TCP)
        new_port.executions.add(self.execution)
        self.assertEqual(
            "-p 10.10.10.10 -p http://10.10.10.10:80/ -p 80,443 -p WordPress -p CVE-2025-3010 -p root",
            " ".join(
                self.executor.get_arguments(
                    [self.host, self.port, new_port, self.technology, self.vulnerability], [], [], [], []
                )
            ),
        )

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_get_arguments_with_path_filter(self) -> None:
        self.assertEqual(
            "-p 10.10.10.10 -p http://10.10.10.10:80/index.html -p 80 -p /index.html -p WordPress -p CVE-2025-3010 -p root",
            " ".join(
                self.executor.get_arguments([self.port, self.path, self.technology, self.vulnerability], [], [], [], [])
            ),
        )
        self.path.path = "rootpath/test"
        self.path.save(update_fields=["path"])
        self.targetport.path = "rootpath"
        self.targetport.save(update_fields=["path"])
        self.assertEqual(
            "-p 10.10.10.10 -p http://10.10.10.10:80/rootpath/test -p 80 -p /rootpath/test -p WordPress -p CVE-2025-3010 -p root",
            " ".join(
                self.executor.get_arguments([self.port, self.path, self.technology, self.vulnerability], [], [], [], [])
            ),
        )

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def _test_get_arguments_no_findings(self) -> None:
        self.target.target = "10.10.10.12"
        self.target.save(update_fields=["target"])
        self.assertEqual(
            f"-p 10.10.10.10 -p http://10.10.10.12:80/ -p 80 -p -p Joomla -p CVE-2023-2222 -p root -p {self.wordlist.path}",
            " ".join(
                self.executor.get_arguments(
                    [], [self.targetport], [self.input_vulnerability], [self.input_technology], [self.wordlist]
                )
            ),
        )

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_get_arguments_no_findings(self) -> None:
        self.target.target = "10.10.10.12"
        self.target.save(update_fields=["target"])
        expected = f"-p 10.10.10.12 -p http://10.10.10.12:80/ -p 80 -p -p Joomla -p CVE-2023-2222 -p {{secret}} -p {self.wordlist.path}"
        self.assertEqual(
            expected.format(secret="root"),
            " ".join(
                self.executor.get_arguments(
                    [], [self.targetport], [self.input_vulnerability], [self.input_technology], [self.wordlist]
                )
            ),
        )
        self.authentication.type = AuthenticationType.BASIC
        self.authentication.save(update_fields=["type"])
        self.assertEqual(
            expected.format(secret=base64.b64encode("root10:root".encode()).decode()),
            " ".join(
                self.executor.get_arguments(
                    [],
                    [TargetPort.objects.get(pk=self.targetport.id)],
                    [self.input_vulnerability],
                    [self.input_technology],
                    [self.wordlist],
                )
            ),
        )

    def test_check_arguments_no_base_inputs(self) -> None:
        self.assertFalse(self.executor.check_arguments([], [], [], [], []))

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_check_arguments_missing_one_required_finding(self) -> None:
        self.assertFalse(
            self.executor.check_arguments([self.osint, self.host, self.port, self.technology], [], [], [], [])
        )
