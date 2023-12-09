import base64
from typing import List
from unittest import mock

from authentications.enums import AuthenticationType
from findings.enums import OSINTDataType
from findings.framework.models import Finding
from findings.models import Port
from parameters.models import InputTechnology, InputVulnerability
from target_ports.models import TargetPort
from tests.executors.mock import get_url
from tests.framework import RekonoTest
from wordlists.models import Wordlist


class ToolExecutorTest(RekonoTest):
    def setUp(self) -> None:
        super().setUp()
        self._setup_fake_tool()
        self._setup_findings(self.execution)
        self.osint.data = "10.10.10.11"
        self.osint.data_type = OSINTDataType.IP
        self.osint.save(update_fields=["data", "data_type"])
        self.executor = self.fake_tool.get_executor_class()(self.execution)

    def test_get_environment(self) -> None:
        expected_env = [("KEY1", "value1"), ("KEY2", "value2")]
        self.executor.arguments = [f"{k}={v}" for k, v in expected_env] + [
            self.fake_tool.command,
            "--foo=bar",
        ]
        environment = self.executor._get_environment()
        for key, value in expected_env:
            self.assertIsNotNone(environment.get(key))
            self.assertEqual(value, environment.get(key))

    def _success_get_arguments(
        self,
        expected: str,
        findings: List[Finding],
        target_ports: List[TargetPort] = [],
        input_vulnerabilities: List[InputVulnerability] = [],
        input_technologies: List[InputTechnology] = [],
        wordlists: List[Wordlist] = [],
    ) -> None:
        arguments = self.executor._get_arguments(
            findings, target_ports, input_vulnerabilities, input_technologies, wordlists
        )
        self.assertEqual(expected, " ".join(arguments))
        self.assertTrue(
            self.executor.check_arguments(
                findings,
                target_ports,
                input_vulnerabilities,
                input_technologies,
                wordlists,
            )
        )

    @mock.patch("framework.models.BaseInput._get_url", get_url)
    def test_get_arguments_only_findings(self) -> None:
        self._success_get_arguments(
            "-p 10.10.10.11 -p http://10.10.10.10:80/index.php -p 80 -p /index.php -p WordPress -p admin -p CVE-2023-1111 -p ReverseShell",
            self.findings,
        )

    @mock.patch("framework.models.BaseInput._get_url", get_url)
    def test_get_arguments_only_required_findings(self) -> None:
        self._success_get_arguments(
            "-p 10.10.10.10 -p http://10.10.10.10:80/ -p 80 -p WordPress -p CVE-2023-1111",
            [self.host, self.port, self.technology, self.vulnerability],
        )

    @mock.patch("framework.models.BaseInput._get_url", get_url)
    def test_get_arguments_multiple_ports(self) -> None:
        self._success_get_arguments(
            "-p 10.10.10.10 -p http://10.10.10.10:80/ -p 80,443 -p WordPress -p CVE-2023-1111",
            [
                self.host,
                self.port,
                self._create_finding(
                    Port, {**self.raw_findings[Port], "port": 443}, self.execution
                ),
                self.technology,
                self.vulnerability,
            ],
        )

    def _test_get_arguments_no_findings(self) -> None:
        self.target.target = "10.10.10.12"
        self.target.save(update_fields=["target"])
        self._success_get_arguments(
            f"-p 10.10.10.10 -p http://10.10.10.12:80/login.php -p 80 -p /login.php -p Joomla -p CVE-2023-2222 -p {base64.b64encode('root:root'.encode()).decode() if self.authentication.type == AuthenticationType.BASIC else 'root'} -p {self.wordlist.path}",
            [],
            [self.target_port],
            [self.input_vulnerability],
            [self.input_technology],
            [self.wordlist],
        )

    @mock.patch("framework.models.BaseInput._get_url", get_url)
    def test_get_arguments_no_findings(self) -> None:
        self._setup_task_user_provided_entities()
        self._test_get_arguments_no_findings()
        self.authentication.type = AuthenticationType.BASIC
        self.authentication.save(update_fields=["type"])
        self._test_get_arguments_no_findings()

    def test_get_arguments_no_base_inputs(self) -> None:
        self.assertFalse(self.executor.check_arguments([], [], [], [], []))

    @mock.patch("framework.models.BaseInput._get_url", get_url)
    def test_get_arguments_missing_one_required_finding(self) -> None:
        self.assertFalse(
            self.executor.check_arguments(
                [self.osint, self.host, self.port, self.technology], [], [], [], []
            )
        )
