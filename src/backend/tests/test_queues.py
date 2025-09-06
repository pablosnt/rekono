import copy

from executions.enums import Status
from executions.models import Execution
from findings.enums import HostOS, PathType, PortStatus, Protocol
from findings.models import Host, Path, Port
from framework.queues import ExecutionParametersToEnqueue
from parameters.models import InputTechnology, InputVulnerability
from processes.models import Process, Step
from target_ports.models import TargetPort
from tasks.models import Task
from tests.framework import QueueTest
from tools.enums import Intensity as IntensityEnum
from tools.models import Configuration, Intensity


class BaseQueueTest(QueueTest):
    number_of_hosts = 10
    number_of_ports_per_host = 3
    number_of_paths_per_port = 2
    setup_entities = ["executions", "fake_tool", "target_and_task_parameters"]

    def setUp(self):
        super().setUp()
        self.findings = []
        self.hosts = []
        for host_index in range(1, self.number_of_hosts + 1):
            new_host = Host.objects.create(ip=f"10.10.10.{host_index}", os_type=HostOS.LINUX)
            new_host.executions.add(self.selected_execution)
            setattr(self, f"host{host_index}", new_host)
            self.findings.append(new_host)
            self.hosts.append(new_host)
            for port_index in range(1, self.number_of_ports_per_host + 1):
                new_port = Port.objects.create(
                    host=new_host,
                    port=int(f"{host_index}{port_index}"),
                    status=PortStatus.OPEN,
                    protocol=Protocol.TCP,
                    service="http",
                )
                new_port.executions.add(self.selected_execution)
                setattr(self, f"port{host_index}{port_index}", new_port)
                self.findings.append(new_port)
                for path_index in range(1, self.number_of_paths_per_port + 1):
                    new_path = Path.objects.create(
                        port=new_port, path=f"/{host_index}{port_index}{path_index}", status=200, type=PathType.ENDPOINT
                    )
                    new_path.executions.add(self.selected_execution)
                    setattr(self, f"path{host_index}{port_index}{path_index}", new_path)
                    self.findings.append(new_path)

    def test_calculate_executions_from_findings(self) -> None:
        # Expected:
        # host1, port11, port12, path111
        # host2, port21, port21, path211
        # host1, port11, port12, path121
        # host2, port21, port22, path221
        expected = []
        last_expected = []
        for host_index in range(1, self.number_of_hosts + 1):
            item = ExecutionParametersToEnqueue([getattr(self, f"host{host_index}")], [], [], [], [])
            for port_index in range(1, self.number_of_ports_per_host + 1):
                item.append("findings", getattr(self, f"port{host_index}{port_index}"))
            new_item = copy.deepcopy(item)
            new_item.append("findings", getattr(self, f"path{host_index}11"))
            expected.append(new_item)
            for port_index in range(1, self.number_of_ports_per_host + 1):
                for path_index in range(1, self.number_of_paths_per_port + 1):
                    if port_index == 1 and path_index == 1:
                        continue
                    new_item = copy.deepcopy(item)
                    new_item.append("findings", getattr(self, f"path{host_index}{port_index}{path_index}"))
                    last_expected.append(new_item)
        self.assertEqual(
            expected + last_expected, self.queue.calculate_executions(self.fake_tool, self.findings, [], [], [], [])
        )

    def test_calculate_executions_from_only_hosts(self) -> None:
        # Expected:
        # host1
        # host2
        self.assertEqual(
            [ExecutionParametersToEnqueue([host], [], [], [], []) for host in self.hosts],
            self.queue.calculate_executions(self.fake_tool, self.hosts, [], [], [], []),
        )

    def test_calculate_executions_user_provided_entities(self) -> None:
        # Expected:
        # target, target_port1, target_port2, vulnerability1, technology1, wordlist
        # target, target_port1, target_port2, vulnerability2, technology1, wordlist
        # target, target_port1, target_port2, vulnerability1, technology2, wordlist
        # target, target_port1, target_port2, vulnerability2, technology2, wordlist
        number_of_entities = 5
        target_ports = [self.target_port]
        vulnerabilities = [self.input_vulnerability]
        technologies = [self.input_technology]
        for index in range(1, number_of_entities + 1):
            target_ports.append(TargetPort.objects.create(target=self.target, port=self.target_port.port + index))
            vulnerabilities.append(InputVulnerability.objects.create(cve=self.input_vulnerability.cve + f"{index}"))
            technologies.append(
                InputTechnology.objects.create(
                    name=self.input_technology.name + f"{index}", version=self.input_technology.version
                )
            )
        executions = self.queue.calculate_executions(
            self.fake_tool, [], target_ports, vulnerabilities, technologies, [self.wordlist]
        )
        expected = []
        last_expected = []
        base_item = ExecutionParametersToEnqueue([], target_ports, [], [], [self.wordlist])
        for vulnerability in vulnerabilities:
            item = copy.deepcopy(base_item)
            item.append("input_vulnerabilities", vulnerability)
            new_item = copy.deepcopy(item)
            new_item.append("input_technologies", technologies[0])
            expected.append(new_item)
            for technology in technologies[1:]:
                new_item = copy.deepcopy(item)
                new_item.append("input_technologies", technology)
                last_expected.append(new_item)
        self.assertEqual(expected + last_expected, executions)


class TasksQueueTest(QueueTest):
    setup_entities = ["target_and_task_parameters"]

    def test_tool_task(self) -> None:
        configuration = Configuration.objects.get(tool__id=1, default=True)
        task = Task.objects.create(target=self.target, configuration=configuration, intensity=IntensityEnum.INSANE)
        task.wordlists.add(self.wordlist)
        task.input_technologies.add(self.input_technology)
        task.input_vulnerabilities.add(self.input_vulnerability)
        self.queue._consume_tool_task(task)
        self.assertEqual(1, Execution.objects.filter(task=task).count())
        execution = Execution.objects.get(pk=1)
        self.assertEqual(task.id, execution.task.id)
        self.assertEqual(1, execution.id)
        self.assertEqual(configuration.id, execution.configuration.id)
        self.assertEqual(Status.REQUESTED, execution.status)
        self.assertIsNone(execution.start)

    def test_process_task(self) -> None:
        process = Process.objects.get(pk=1)
        for intensity in [IntensityEnum.INSANE, IntensityEnum.SNEAKY]:
            task = Task.objects.create(target=self.target, process=process, intensity=intensity)
            task.wordlists.add(self.wordlist)
            self.queue._consume_process_task(task)
            self.assertEqual(Step.objects.filter(process=process).count(), Execution.objects.filter(task=task).count())
            for execution in Execution.objects.filter(task=task).all():
                self.assertTrue(Step.objects.filter(configuration=execution.configuration, process=process))
                self.assertEqual(
                    Status.REQUESTED
                    if Intensity.objects.filter(tool=execution.configuration.tool, value__lte=intensity).exists()
                    else Status.SKIPPED,
                    execution.status,
                )
                self.assertIsNone(execution.start)
