import copy

from executions.enums import Status
from executions.models import Execution
from findings.enums import HostOS, PathType, PortStatus, Protocol
from findings.framework.models import Finding
from findings.models import Host, Path, Port
from parameters.models import InputTechnology, InputVulnerability
from processes.models import Process, Step
from target_ports.models import TargetPort
from tasks.models import Task
from tests.framework import QueueTest
from tools.enums import Intensity
from tools.models import Configuration


class BaseQueueTest(QueueTest):
    number_of_hosts = 10
    number_of_ports_per_host = 3
    number_of_paths_per_port = 2

    def setUp(self) -> None:
        super().setUp()
        self._setup_fake_tool()

    def _setup_multiple_findings(self, create_ports_and_paths: bool) -> list[Finding]:
        findings = []
        for host_index in range(1, self.number_of_hosts + 1):
            new_host = self._create_finding(
                Host,
                {"ip": f"10.10.10.{host_index}", "os_type": HostOS.LINUX},
                self.execution,
            )
            setattr(self, f"host{host_index}", new_host)
            findings.append(new_host)
            if create_ports_and_paths:
                for port_index in range(1, self.number_of_ports_per_host + 1):
                    new_port = self._create_finding(
                        Port,
                        {
                            "host": new_host,
                            "port": int(f"{host_index}{port_index}"),
                            "status": PortStatus.OPEN,
                            "protocol": Protocol.TCP,
                            "service": "http",
                        },
                        self.execution,
                    )
                    setattr(self, f"port{host_index}{port_index}", new_port)
                    findings.append(new_port)
                    for path_index in range(1, self.number_of_paths_per_port + 1):
                        new_path = self._create_finding(
                            Path,
                            {
                                "port": new_port,
                                "path": f"/{host_index}{port_index}{path_index}",
                                "status": 200,
                                "type": PathType.ENDPOINT,
                            },
                            self.execution,
                        )
                        setattr(
                            self, f"path{host_index}{port_index}{path_index}", new_path
                        )
                        findings.append(new_path)
        return findings

    def test_calculate_executions_from_findings(self) -> None:
        findings = self._setup_multiple_findings(True)
        executions = self.queue._calculate_executions(
            self.fake_tool, findings, [], [], [], []
        )
        expected = []
        last_expected = []
        for host_index in range(1, self.number_of_hosts + 1):
            item = {0: [getattr(self, f"host{host_index}")]}
            for port_index in range(1, self.number_of_ports_per_host + 1):
                item[0].append(getattr(self, f"port{host_index}{port_index}"))
            new_item = copy.deepcopy(item)
            new_item[0].append(getattr(self, f"path{host_index}11"))
            expected.append(new_item)
            for port_index in range(1, self.number_of_ports_per_host + 1):
                for path_index in range(1, self.number_of_paths_per_port + 1):
                    if port_index == 1 and path_index == 1:
                        continue
                    new_item = copy.deepcopy(item)
                    new_item[0].append(
                        getattr(self, f"path{host_index}{port_index}{path_index}")
                    )
                    last_expected.append(new_item)
        self.assertEqual(expected + last_expected, executions)

    def test_calculate_executions_from_only_hosts(self) -> None:
        findings = self._setup_multiple_findings(False)
        executions = self.queue._calculate_executions(
            self.fake_tool, findings, [], [], [], []
        )
        self.assertEqual(
            [
                {0: [getattr(self, f"host{h}")]}
                for h in range(1, self.number_of_hosts + 1)
            ],
            executions,
        )

    def test_calculate_executions_user_provided_entities(self) -> None:
        self._setup_task_user_provided_entities()
        number_of_entities = 5
        target_ports = [self.target_port]
        vulnerabilities = [self.input_vulnerability]
        technologies = [self.input_technology]
        for index in range(1, number_of_entities + 1):
            target_ports.append(
                TargetPort.objects.create(
                    target=self.target, port=self.target_port.port + index
                )
            )
            vulnerabilities.append(
                InputVulnerability.objects.create(
                    cve=self.input_vulnerability.cve + f"{index}"
                )
            )
            technologies.append(
                InputTechnology.objects.create(
                    name=self.input_technology.name + f"{index}",
                    version=self.input_technology.version,
                )
            )
        executions = self.queue._calculate_executions(
            self.fake_tool,
            [],
            target_ports,
            vulnerabilities,
            technologies,
            [self.wordlist],
        )
        expected = []
        last_exected = []
        base_item = {0: [], 1: target_ports, 4: [self.wordlist]}
        for vulnerability in vulnerabilities:
            item = copy.deepcopy(base_item)
            item[2] = [vulnerability]
            new_item = copy.deepcopy(item)
            new_item[3] = [technologies[0]]
            expected.append(dict(sorted(copy.deepcopy(new_item).items())))
            for technology in technologies[1:]:
                new_item = copy.deepcopy(item)
                new_item[3] = [technology]
                last_exected.append(dict(sorted(copy.deepcopy(new_item).items())))
        self.assertEqual(expected + last_exected, executions)


class TasksQueueTest(QueueTest):
    expected_executions = [
        (19, 1, 1),  # theHarvester
        (30, 1, 1),  # EmailFinder
        (31, 1, 1),  # EmailHarvester
        (46, 1, 1),  # Gobuster
        (38, 1, 1),  # Nmap
        (47, 2, 2),  # Gobuster
        (22, 2, 2),  # Sslscan
        (23, 2, None),  # SSLyze
        (28, 2, None),  # Log4Shell Scan
        (29, 2, None),  # Log4Shell Scan
        (34, 2, None),  # SSH Audit
        (24, 2, None),  # CMSeeK
        (33, 2, None),  # GitDumper & GitLeaks
        (36, 2, None),  # SMB Map
        (25, 2, None),  # ZAP
        (15, 2, 2),  # Dirsearch
        (48, 2, 2),  # Gobuster
        (21, 2, None),  # Nikto
        (39, 2, None),  # Nuclei
        (32, 2, None),  # JoomScan
        (26, 3, 3),  # SearchSploit
        (27, 3, 3),  # Metasploit
    ]

    def setUp(self) -> None:
        super().setUp()
        self._setup_task_user_provided_entities()

    def _validate_execution(
        self,
        execution: Execution,
        task_id: int,
        execution_id: int,
        configuration_id: int,
        group: int,
        status: Status = Status.REQUESTED,
    ) -> None:
        self.assertEqual(task_id, execution.task.id)
        self.assertEqual(execution_id, execution.id)
        self.assertEqual(configuration_id, execution.configuration.id)
        self.assertEqual(status, execution.status)
        self.assertIsNone(execution.start)

    def test_tool_task(self) -> None:
        configuration = Configuration.objects.get(tool__id=1, default=True)
        task = Task.objects.create(
            target=self.target, configuration=configuration, intensity=Intensity.INSANE
        )
        task.wordlists.add(self.wordlist)
        task.input_technologies.add(self.input_technology)
        task.input_vulnerabilities.add(self.input_vulnerability)
        self.queue._consume_tool_task(task)
        self.assertEqual(1, Execution.objects.count())
        self._validate_execution(
            Execution.objects.get(pk=1), task.id, 1, configuration.id, 1
        )

    def _test_process_task(self, intensity: Intensity) -> None:
        process = Process.objects.get(pk=1)
        self.task = Task.objects.create(
            target=self.target, process=process, intensity=intensity
        )
        self.task.wordlists.add(self.wordlist)
        self.queue._consume_process_task(self.task)
        self.assertEqual(
            Step.objects.filter(process=process).count(),
            Execution.objects.filter(task=self.task).count(),
        )

    def test_process_task(self) -> None:
        execution_id = 1
        for intensity, group_index in [(Intensity.INSANE, 1), (Intensity.SNEAKY, 2)]:
            self._test_process_task(intensity)
            for configuration_id, group in [
                (e[0], e[group_index])
                for e in self.expected_executions
                if e[group_index] is None
            ] + [
                (e[0], e[group_index])
                for e in self.expected_executions
                if e[group_index] is not None
            ]:
                self._validate_execution(
                    Execution.objects.get(
                        task=self.task, configuration__id=configuration_id
                    ),
                    self.task.id,
                    execution_id,
                    configuration_id,
                    group or 1,
                    Status.REQUESTED if group is not None else Status.SKIPPED,
                )
                execution_id += 1
