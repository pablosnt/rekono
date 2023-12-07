from typing import List
from unittest import mock

from authentications.enums import AuthenticationType
from authentications.models import Authentication
from executions.enums import Status
from executions.models import Execution
from findings.enums import OSINTDataType
from findings.framework.models import Finding
from findings.models import Port
from input_types.enums import InputTypeName
from input_types.models import InputType
from parameters.models import InputTechnology, InputVulnerability
from target_ports.models import TargetPort
from tasks.models import Task
from tests.executors.mock import get_url
from tests.framework import RekonoTest
from tools.enums import Intensity as IntensityEnum
from tools.enums import Stage
from tools.models import Argument, Configuration, Input, Intensity, Tool
from wordlists.enums import WordlistType
from wordlists.models import Wordlist


class ToolExecutorTest(RekonoTest):
    def setUp(self) -> None:
        super().setUp()
        self._setup_target()
        self.fake_tool = Tool.objects.create(
            name="fake",
            command="fake",
            is_installed=True,
            version="1.0.0",
            version_argument="--version",
        )
        for index, value in enumerate(IntensityEnum):
            Intensity.objects.create(
                tool=self.fake_tool, argument=f"-i {index}", value=value
            )
        self.fake_configuration = Configuration.objects.create(
            name="fake",
            tool=self.fake_tool,
            arguments="{host} {url} {ports_commas} {endpoint} {technology} {secret} {cve} {exploit} {username} {wordlist}",
            stage=Stage.ENUMERATION,
            default=True,
        )
        for value, required, multiple, input_type_names in [
            ("host", False, False, [InputTypeName.OSINT]),
            (
                "url",
                True,
                False,
                [InputTypeName.PATH, InputTypeName.PORT, InputTypeName.HOST],
            ),
            ("ports_commas", True, True, [InputTypeName.PORT]),
            ("endpoint", False, False, [InputTypeName.PATH]),
            ("technology", True, False, [InputTypeName.TECHNOLOGY]),
            ("secret", False, False, [InputTypeName.CREDENTIAL]),
            ("cve", True, False, [InputTypeName.VULNERABILITY]),
            ("exploit", False, False, [InputTypeName.EXPLOIT]),
            ("username", False, False, [InputTypeName.AUTHENTICATION]),
            ("wordlist", False, False, [InputTypeName.WORDLIST]),
        ]:
            new_argument = Argument.objects.create(
                tool=self.fake_tool,
                name=value,
                argument="-p {" + value + "}",
                required=required,
                multiple=multiple,
            )
            for index, input_type_name in enumerate(input_type_names):
                Input.objects.create(
                    argument=new_argument,
                    type=InputType.objects.get(name=input_type_name),
                    order=index + 1,
                )
        self.task = Task.objects.create(
            target=self.target,
            configuration=self.fake_configuration,
            executor=self.auditor1,
        )
        self.execution = Execution.objects.create(
            task=self.task,
            configuration=self.fake_configuration,
            status=Status.REQUESTED,
        )
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
            "-p http://10.10.10.10:80/ -p 80 -p WordPress -p CVE-2023-1111",
            [self.host, self.port, self.technology, self.vulnerability],
        )

    @mock.patch("framework.models.BaseInput._get_url", get_url)
    def test_get_arguments_multiple_ports(self) -> None:
        self._success_get_arguments(
            "-p http://10.10.10.10:80/ -p 80,443 -p WordPress -p CVE-2023-1111",
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

    @mock.patch("framework.models.BaseInput._get_url", get_url)
    def test_get_arguments_no_findings(self) -> None:
        self.target.target = "10.10.10.12"
        self.target.save(update_fields=["target"])
        self._setup_task_user_provided_entities()
        self._success_get_arguments(
            f"-p http://10.10.10.12:80/login.php -p 80 -p /login.php -p Joomla -p CVE-2023-2222 -p root -p {self.wordlist.path}",
            [],
            [self.target_port],
            [self.input_vulnerability],
            [self.input_technology],
            [self.wordlist],
        )

    def test_get_arguments_no_base_inputs(self) -> None:
        self.assertFalse(self.executor.check_arguments([], [], [], [], []))

    @mock.patch("framework.models.BaseInput._get_url", get_url)
    def test_get_arguments_missing_one_required_finding(self) -> None:
        self.assertFalse(
            self.executor.check_arguments(
                [self.osint, self.host, self.port, self.technology], [], [], [], []
            )
        )
