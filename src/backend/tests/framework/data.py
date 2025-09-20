import hashlib
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path as PathFile
from typing import Any

from django.utils import timezone

from authentications.enums import AuthenticationType
from authentications.models import Authentication
from executions.models import Execution
from findings.enums import HostOS, OSINTDataType, PathType, Protocol, Severity
from findings.framework.models import Finding
from findings.models import OSINT, Credential, Exploit, Host, Path, Port, Technology, Vulnerability
from input_types.enums import InputTypeName
from input_types.models import InputType
from parameters.models import InputTechnology, InputVulnerability
from projects.models import Project
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


@dataclass
class SetupProject:
    targets_and_tasks: int = 1
    executions_per_task: int = 1
    osint_fields: list[dict[str, Any]] | None = None
    hosts_fields: list[dict[str, Any]] | None = None
    ports_fields: list[dict[str, Any]] | None = None
    paths_fields: list[dict[str, Any]] | None = None
    technologies_fields: list[dict[str, Any]] | None = None
    credentials_fields: list[dict[str, Any]] | None = None
    vulnerabilities_fields: list[dict[str, Any]] | None = None
    exploits_fields: list[dict[str, Any]] | None = None


class TestingDataMixin:
    data_dir = PathFile(__file__).resolve().parent.parent / "data"
    data = []
    users = True
    target_parameters = False
    task_parameters = False
    fake_tool = False

    def setup_testing_data(self) -> None:
        self.configuration = Configuration.objects.get(pk=1)
        if self.users:
            self.setup_users()
            for index, project in enumerate(self.data):
                self.setup_project(index + 1, project)
        if self.fake_tool:
            self.setup_fake_tool()
        if self.task_parameters:
            self.setup_task_parameters()

    def setup_project(self, project_number: int, config: SetupProject) -> None:
        project = Project.objects.create(
            name=f"Project {project_number}",
            description=f"Project {project_number} for testing filters",
            owner=self.admin1,
        )
        project.members.set(self.members)
        for target_index in range(config.targets_and_tasks):
            _target_index = 10 * project_number + target_index
            target = Target.objects.create(
                project=project, target=f"10.10.10.{_target_index}", type=TargetType.PRIVATE_IP
            )
            if self.target_parameters:
                target_port = TargetPort.objects.create(target=target, port=80 + target_index, path=None)
                Authentication.objects.create(
                    name=f"root{_target_index}", secret="root", type=AuthenticationType.TOKEN, target_port=target_port
                )
            task = Task.objects.create(
                target=target,
                configuration=self.configuration,
                executor=self.auditor1,
                start=timezone.now() - timedelta(days=_target_index + 1),
            )
            for executions_index in range(config.executions_per_task):
                _executions_index = _target_index + executions_index
                execution = Execution.objects.create(
                    task=task, configuration=self.configuration, start=task.start - timedelta(minutes=executions_index)
                )
                for osint_index, osint_fields in enumerate(
                    config.osint_fields if config.osint_fields is not None else [{}]
                ):
                    _osint_index = _executions_index + osint_index
                    osint = OSINT.objects.create(
                        **{
                            "data": f"admin{_osint_index}",
                            "data_type": OSINTDataType.USER,
                            "source": "Google",
                            **osint_fields,
                        }
                    )
                    osint.executions.add(execution)
                for host_index, host_fields in enumerate(
                    config.hosts_fields if config.hosts_fields is not None else [{}]
                ):
                    _host_index = _executions_index + host_index
                    host = Host.objects.create(
                        **{"ip": f"10.10.10.{_host_index}", "os_type": HostOS.LINUX, **host_fields}
                    )
                    host.executions.add(execution)
                    for port_fields in config.ports_fields if config.ports_fields is not None else [{}]:
                        port = Port.objects.create(
                            **{"port": 80, "service": "http", "protocol": Protocol.TCP, **port_fields, "host": host}
                        )
                        port.executions.add(execution)
                        for paths_index, path_fields in enumerate(
                            config.paths_fields if config.paths_fields is not None else [{}]
                        ):
                            path = Path.objects.create(
                                **{
                                    "status": 200,
                                    "type": PathType.ENDPOINT,
                                    "path": "/index.html",
                                    **path_fields,
                                    "port": port,
                                }
                            )
                            path.executions.add(execution)
                        for technologies_index, technology_fields in enumerate(
                            config.technologies_fields if config.technologies_fields is not None else [{}]
                        ):
                            _technologies_index = _host_index + technologies_index
                            technology = Technology.objects.create(
                                **{
                                    "version": f"1.0.{_technologies_index}",
                                    "name": "WordPress",
                                    "description": "Typical CMS",
                                    **technology_fields,
                                    "port": port,
                                }
                            )
                            technology.executions.add(execution)
                            for credential_index, credential_fields in enumerate(
                                config.credentials_fields if config.credentials_fields is not None else [{}]
                            ):
                                _credential_index = _technologies_index + credential_index
                                credential = Credential.objects.create(
                                    **{
                                        "context": "Default credentials",
                                        "email": f"admin{_credential_index}@rekono.com",
                                        "username": f"admin{_credential_index}",
                                        "secret": "admin",
                                        **credential_fields,
                                        "technology": technology,
                                    }
                                )
                                credential.executions.add(execution)
                            for vulnerability_index, vulnerability_fields in enumerate(
                                config.vulnerabilities_fields if config.vulnerabilities_fields is not None else [{}]
                            ):
                                _vulnerability_index = _technologies_index + vulnerability_index
                                vulnerability = Vulnerability.objects.create(
                                    **{
                                        "severity": Severity.MEDIUM,
                                        "name": f"Vulnerability {_vulnerability_index}",
                                        "description": f"Vulnerability {_vulnerability_index}",
                                        "cve": f"CVE-2025-{3000 + _vulnerability_index}",
                                        "cwe": "CWE-200",
                                        **vulnerability_fields,
                                        "technology": technology,
                                    }
                                )
                                vulnerability.executions.add(execution)
                                for exploit_index, exploit_fields in enumerate(
                                    config.exploits_fields if config.exploits_fields is not None else [{}]
                                ):
                                    _exploit_index = _vulnerability_index + exploit_index
                                    exploit = Exploit.objects.create(
                                        **{
                                            "title": f"ReverseShell {_exploit_index}",
                                            "edb_id": 1,
                                            "reference": "https://www.exploit-db.com/exploits/1",
                                            **exploit_fields,
                                            "vulnerability": vulnerability,
                                        }
                                    )
                                    exploit.executions.add(execution)
        self.findings = []
        for model in [
            Project,
            Target,
            TargetPort,
            Authentication,
            Task,
            Execution,
            OSINT,
            Host,
            Port,
            Path,
            Technology,
            Credential,
            Vulnerability,
            Exploit,
        ]:
            setattr(self, model.__name__.lower(), model.objects.first())
            if issubclass(model, Finding):
                self.findings.extend(model.objects.all())

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

    def setup_task_parameters(self) -> None:
        self.input_vulnerability = InputVulnerability.objects.create(cve="CVE-2023-2222")
        self.input_technology = InputTechnology.objects.create(name="Joomla", version="2.0.0")
        path = self.data_dir / "wordlists" / "endpoints_wordlist.txt"
        self.wordlist = Wordlist.objects.create(
            name="test", type=WordlistType.ENDPOINT, path=path, checksum=hashlib.sha512(path.read_bytes()).hexdigest()
        )
