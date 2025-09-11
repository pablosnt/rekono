import hashlib
import shutil
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import cached_property
from pathlib import Path as PathFile
from typing import Any

from authentications.enums import AuthenticationType
from authentications.models import Authentication
from executions.enums import Status
from executions.models import Execution
from findings.enums import HostOS, OSINTDataType, PathType, PortStatus, Protocol, Severity
from findings.models import OSINT, Credential, Exploit, Host, Path, Port, Technology, Vulnerability
from input_types.enums import InputTypeName
from input_types.models import InputType
from parameters.models import InputTechnology, InputVulnerability
from processes.models import Process, Step
from projects.models import Project
from rekono.settings import CONFIG
from security.authorization.roles import Role
from target_ports.models import TargetPort
from targets.enums import TargetType
from targets.models import Target
from tasks.models import Task
from tools.enums import Intensity as IntensityEnum
from tools.enums import Stage
from tools.models import Argument, Configuration, Input, Intensity, Tool
from users.models import User
from wordlists.enums import WordlistType
from wordlists.models import Wordlist

# pytype: disable=attribute-error


class TestingDataMixin:
    data_dir = PathFile(__file__).resolve().parent.parent / "data"
    setup_entities = []

    def setup_testing_data(self) -> None:
        for entity in self.setup_entities:
            method = f"setup_{entity}"
            if hasattr(self, method):
                getattr(self, method)()

    def setup_users(self) -> None:
        self.users = {r: [] for r in Role}
        self.members = []
        self.not_members = []
        for role in [Role.ADMIN, Role.AUDITOR, Role.READER]:
            for index in range(2):
                username = f"{role.name.lower()}{index + 1}"
                new_user = User.objects.create(
                    username=username,
                    first_name=username,
                    last_name=username,
                    email=f"{username}@rekono.com",
                    is_active=True,
                )
                new_user.set_password(username)
                new_user.save(update_fields=["password"])
                User.objects.assign_role(new_user, role)
                setattr(self, username, new_user)
                self.users[role].append(new_user)
                if index + 1 == 1:
                    self.members.append(new_user)
                else:
                    self.not_members.append(new_user)

    def setup_project(self) -> None:
        if not hasattr(self, "users"):
            self.setup_users()
        self.project, _ = Project.objects.get_or_create(name="test", description="test", owner=self.admin1)
        self.project.tags.add("test")
        self.project.members.set([self.admin1, self.auditor1, self.reader1])

    def setup_target(self) -> None:
        if not hasattr(self, "project"):
            self.setup_project()
        self.target = Target.objects.create(project=self.project, target="10.10.10.10", type=TargetType.PRIVATE_IP)

    def setup_tasks(self) -> None:
        if not hasattr(self, "target"):
            self.setup_target()
        self.task1 = Task.objects.create(target=self.target, process=Process.objects.get(pk=1), executor=self.admin1)
        self.task2 = Task.objects.create(
            target=self.target, configuration=Configuration.objects.get(pk=1), executor=self.auditor1
        )

    def setup_executions(self) -> None:
        if not hasattr(self, "task1") or not hasattr(self, "task2"):
            self.setup_tasks()
        process_step = Step.objects.filter(process__id=1).first()
        self.execution11 = Execution.objects.create(
            task=self.task1,
            configuration=process_step.configuration,
            status=Status.COMPLETED,
            output_file="not_found_report.json",
        )
        self.execution12 = Execution.objects.create(
            task=self.task1, configuration=process_step.configuration, status=Status.RUNNING
        )
        report_filename = "nmap.xml"
        shutil.copy(self.data_dir / "reports" / "nmap" / "smb-users.xml", CONFIG.reports / report_filename)
        self.execution21 = Execution.objects.create(
            task=self.task2,
            configuration=self.task2.configuration,
            status=Status.COMPLETED,
            output_file=report_filename,
        )
        self.selected_execution = self.execution21

    def setup_target_and_task_parameters(self) -> None:
        if not hasattr(self, "target"):
            self.setup_target()
        self.target_port = TargetPort.objects.create(target=self.target, port=80, path="/login.php")
        self.authentication = Authentication.objects.create(
            name="root", secret="root", type=AuthenticationType.TOKEN, target_port=self.target_port
        )
        self.input_vulnerability = InputVulnerability.objects.create(cve="CVE-2023-2222")
        self.input_technology = InputTechnology.objects.create(name="Joomla", version="2.0.0")
        path = self.data_dir / "wordlists" / "endpoints_wordlist.txt"
        self.wordlist = Wordlist.objects.create(
            name="test", type=WordlistType.ENDPOINT, path=path, checksum=hashlib.sha512(path.read_bytes()).hexdigest()
        )

    def setup_fake_tool(self) -> None:
        self.fake_tool = Tool.objects.create(
            name="fake", command="fake", is_installed=True, version="1.0.0", version_argument="--version"
        )
        for index, value in enumerate(IntensityEnum):
            Intensity.objects.create(tool=self.fake_tool, argument=f"-i {index}", value=value)
        configuration_arguments = []
        for pattern, required, multiple, input_type_names in [
            ("host", False, False, [InputTypeName.OSINT, InputTypeName.HOST]),
            ("url", True, False, [InputTypeName.PATH, InputTypeName.PORT, InputTypeName.HOST]),
            ("ports_commas", True, True, [InputTypeName.PORT]),
            ("endpoint", False, False, [InputTypeName.PATH]),
            ("technology", True, False, [InputTypeName.TECHNOLOGY]),
            ("secret", False, False, [InputTypeName.CREDENTIAL]),
            ("cve", True, False, [InputTypeName.VULNERABILITY]),
            ("exploit", False, False, [InputTypeName.EXPLOIT]),
            ("token", False, False, [InputTypeName.AUTHENTICATION]),
            ("wordlist", False, False, [InputTypeName.WORDLIST]),
        ]:
            format_pattern = "{" + pattern + "}"
            configuration_arguments.append(format_pattern)
            argument = Argument.objects.create(
                tool=self.fake_tool, name=pattern, argument=f"-p {format_pattern}", required=required, multiple=multiple
            )
            for index, input_type_name in enumerate(input_type_names):
                Input.objects.create(
                    argument=argument, type=InputType.objects.get(name=input_type_name), order=index + 1
                )
        self.fake_configuration = Configuration.objects.create(
            name="fake",
            tool=self.fake_tool,
            arguments=" ".join(configuration_arguments),
            stage=Stage.ENUMERATION,
            default=True,
        )

    def setup_fake_execution(self) -> None:
        if not hasattr(self, "target"):
            self.setup_target()
        if not hasattr(self, "fake_configuration"):
            self.setup_fake_tool()
        self.fake_task = Task.objects.create(
            target=self.target, configuration=self.fake_configuration, executor=self.auditor1
        )
        self.fake_execution = Execution.objects.create(
            task=self.fake_task, configuration=self.fake_configuration, status=Status.REQUESTED
        )
        self.selected_execution = self.fake_execution

    def setup_findings(self) -> None:
        if not hasattr(self, "selected_execution"):
            self.setup_executions()
        self.raw_findings = {
            OSINT: {"data": "admin", "data_type": OSINTDataType.USER, "source": "Google"},
            Host: {"ip": "10.10.10.10", "os": "some type of Linux", "os_type": HostOS.LINUX},
            Port: {"host": 1, "port": 80, "status": PortStatus.OPEN, "protocol": Protocol.TCP, "service": "http"},
            Path: {
                "port": 1,
                "path": "/index.php",
                "status": 200,
                "extra_info": "Main path",
                "type": PathType.ENDPOINT,
            },
            Technology: {
                "port": 1,
                "name": "WordPress",
                "version": "1.0.0",
                "description": "Typical CMS",
                "reference": "https://wordpress.org",
            },
            Credential: {
                "technology": 1,
                "email": "admin@shop.com",
                "username": "admin",
                "secret": "admin",
                "context": "Default admin credentials",
            },
            Vulnerability: {
                "technology": 1,
                "name": "Test",
                "description": "Test",
                "severity": Severity.CRITICAL,
                "cve": "CVE-2023-1111",
                "cwe": "CWE-200",
                "reference": "https://nvd.nist.gov/vuln/detail/CVE-2023-1111",
            },
            Exploit: {
                "vulnerability": 1,
                "title": "ReverseShell",
                "edb_id": 1,
                "reference": "https://www.exploit-db.com/exploits/1",
            },
        }
        self.findings = []
        for finding_model, finding_data in self.raw_findings.items():
            finding = finding_model.objects.create(
                **{
                    k: (getattr(self, k) if isinstance(v, int) and hasattr(self, k) and getattr(self, k).id == v else v)
                    for k, v in finding_data.items()
                }
            )
            finding.executions.add(self.selected_execution)
            setattr(self, finding_model.__name__.lower(), finding)
            self.findings.append(finding)


@dataclass
class SetupProject:
    targets_and_tasks: int = 1
    executions_per_task: int = 1
    _hosts_fields: list[dict[str, Any]] | None = None
    _ports_fields: list[dict[str, Any]] | None = None
    _technologies_fields: list[dict[str, Any]] | None = None
    _vulnerabilities_fields: list[dict[str, Any]] | None = None

    @cached_property
    def hosts_fields(self) -> list[dict[str, Any]]:
        return self._hosts_fields or [{"os_type": HostOS.LINUX}]

    @cached_property
    def ports_fields(self) -> list[dict[str, Any]]:
        return self._ports_fields or [{"port": 80, "service": "http", "protocol": Protocol.TCP}]

    @cached_property
    def technologies_fields(self) -> list[dict[str, Any]]:
        return self._technologies_fields or [{"name": "WordPress"}]

    @cached_property
    def vulnerabilities_fields(self) -> list[dict[str, Any]]:
        return self._vulnerabilities_fields or [{"is_fixed": False}]


class StatsTestingDataMixin:
    # TODO: Use this approach for the TestingDataMixin?
    data = []

    def setup_multiple_data(self) -> None:
        self.configuration = Configuration.objects.get(pk=1)
        for index, config in enumerate(self.data):
            self.setup_data(index + 1, config)

    def setup_data(self, project_number: int, config: SetupProject) -> None:
        project = Project.objects.create(
            name=f"Project {project_number}",
            description=f"Project {project_number} for testing filters",
            owner=self.admin1,
        )
        project.members.set(self.members)
        for target_index in range(config.targets_and_tasks):
            t__index = 10 * project_number + target_index
            target = Target.objects.create(project=project, target=f"10.10.10.{t__index}", type=TargetType.PRIVATE_IP)
            task = Task.objects.create(
                target=target,
                configuration=self.configuration,
                executor=self.auditor1,
                start=datetime.now() - timedelta(days=t__index + 1),
            )
            for executions_index in range(config.executions_per_task):
                e___index = t__index + executions_index
                execution = Execution.objects.create(
                    task=task, configuration=self.configuration, start=task.start - timedelta(minutes=executions_index)
                )
                findings = []
                for host_fields in config.hosts_fields:
                    host = Host.objects.create(**{"ip": f"10.10.10.{e___index}", **host_fields})
                    findings.append(host)
                    for port_fields in config.ports_fields:
                        port = Port.objects.create(**{**port_fields, "host": host})
                        findings.append(port)
                        for technologies_index, technology_fields in enumerate(config.technologies_fields):
                            t____index = e___index + technologies_index
                            technology = Technology.objects.create(
                                **{"version": f"1.0.{t____index}", **technology_fields, "port": port}
                            )
                            findings.append(technology)
                            for vulnerability_index, vulnerability_fields in enumerate(config.vulnerabilities_fields):
                                v_____index = t____index + vulnerability_index
                                vulnerability = Vulnerability.objects.create(
                                    **{
                                        "severity": Severity.MEDIUM,
                                        "name": f"Vulnerability {v_____index}",
                                        "description": f"Vulnerability {v_____index}",
                                        "cve": f"CVE-2025-{3000 + v_____index}",
                                        "cwe": "CWE-200",
                                        **vulnerability_fields,
                                        "technology": technology,
                                    }
                                )
                                findings.append(vulnerability)
                for finding in findings:
                    finding.executions.add(execution)
