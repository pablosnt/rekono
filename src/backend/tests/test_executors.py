from typing import List

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
from tests.framework import RekonoTest
from tools.enums import Intensity as IntensityEnum
from tools.enums import Stage
from tools.models import Argument, Configuration, Input, Intensity, Tool
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
            arguments="{host} {url} {ports_commas} {endpoint} {technology} {secret} {cve} {exploit}",
            stage=Stage.ENUMERATION,
            default=True,
        )
        for value, required, multiple, input_type_names in [
            ("host", True, False, [InputTypeName.OSINT]),
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
        # scanme.nmap.org: connectivity is needed to build a valid URL from host, port and path
        self.host.address = "45.33.32.156"
        self.host.save(update_fields=["address"])
        self.path.path = "/images"
        self.path.save(update_fields=["path"])
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

    def test_get_arguments_only_findings(self) -> None:
        self._success_get_arguments(
            "-p 10.10.10.11 -p http://45.33.32.156:80/images -p 80 -p /images -p WordPress -p admin -p CVE-2023-1111 -p ReverseShell",
            self.findings,
        )

    def test_get_arguments_only_required_findings(self) -> None:
        self._success_get_arguments(
            "-p 10.10.10.11 -p http://45.33.32.156:80/ -p 80 -p WordPress -p CVE-2023-1111",
            [self.osint, self.host, self.port, self.technology, self.vulnerability],
        )

    def test_get_arguments_multiple_ports(self) -> None:
        self._success_get_arguments(
            "-p 10.10.10.11 -p http://45.33.32.156:80/ -p 80,443 -p WordPress -p CVE-2023-1111",
            [
                self.osint,
                self.host,
                self.port,
                self._create_finding(
                    Port, {**self.raw_findings[Port], "port": 443}, self.execution
                ),
                self.technology,
                self.vulnerability,
            ],
        )

    # TODO: test with target ports, user-provided parameters, wordlists and authentication

    def test_get_arguments_no_findings(self) -> None:
        self.assertFalse(self.executor.check_arguments([], [], [], [], []))

    def test_get_arguments_missing_one_required_finding(self) -> None:
        self.assertFalse(
            self.executor.check_arguments(
                [self.osint, self.host, self.port, self.technology], [], [], [], []
            )
        )


# TODO: Test Gobuster executor
