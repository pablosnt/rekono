import copy

from django.test import TestCase

from executions.enums import Status
from executions.models import Execution
from findings.models import Host
from framework.queues import ExecutionParametersToEnqueue
from parameters.models import InputTechnology, InputVulnerability
from processes.models import Process, Step
from target_ports.models import TargetPort
from tasks.models import Task
from tests.framework import QueueTest
from tests.framework.data import SetupProject
from tools.enums import Intensity as IntensityEnum
from tools.models import Configuration, Intensity

# pytype: disable=attribute-error


class GenericQueueTest(QueueTest, TestCase):
    data = [
        SetupProject(
            osint_fields=[],
            hosts_fields=[{}] * 10,
            ports_fields=[{"port": 80}, {"port": 81}, {"port": 82}],
            paths_fields=[{"path": "/index.html"}, {"path": "/login"}],
            technologies_fields=[],
            credentials_fields=[],
            vulnerabilities_fields=[],
            exploits_fields=[],
        )
    ]
    target_parameters_flag = True
    task_parameters_flag = True

    def test_calculate_executions_from_findings(self) -> None:
        # Expected:
        # host1, port11, port12, path111
        # host2, port21, port21, path211
        # host1, port11, port12, path121
        # host2, port21, port22, path221
        expected = []
        last_expected = []
        for host in Host.objects.all().order_by("id"):
            item = ExecutionParametersToEnqueue([host], [], [], [], [])
            for port in host.port.all():
                item.append("findings", port)
            new_item = copy.deepcopy(item)
            first_path = host.port.order_by("id").first().path.order_by("id").first()
            new_item.append("findings", first_path)
            expected.append(new_item)
            for port in host.port.all().order_by("id"):
                for path in port.path.all().exclude(pk=first_path.id).order_by("id"):
                    new_item = copy.deepcopy(item)
                    new_item.append("findings", path)
                    last_expected.append(new_item)
        self.assertEqual(
            expected + last_expected, self.queue.calculate_executions(self.fake_tool, self.findings, [], [], [], [])
        )

    def test_calculate_executions_from_only_hosts(self) -> None:
        # Expected:
        # host1
        # host2
        hosts = Host.objects.all()
        self.assertEqual(
            [ExecutionParametersToEnqueue([host], [], [], [], []) for host in hosts],
            self.queue.calculate_executions(self.fake_tool, hosts, [], [], [], []),
        )

    def test_calculate_executions_user_provided_entities(self) -> None:
        # Expected:
        # target, target_port1, target_port2, vulnerability1, technology1, wordlist
        # target, target_port1, target_port2, vulnerability2, technology1, wordlist
        # target, target_port1, target_port2, vulnerability1, technology2, wordlist
        # target, target_port1, target_port2, vulnerability2, technology2, wordlist
        number_of_entities = 5
        target_ports = [self.targetport]
        vulnerabilities = [self.input_vulnerability]
        technologies = [self.input_technology]
        for index in range(1, number_of_entities + 1):
            target_ports.append(TargetPort.objects.create(target=self.target, port=self.targetport.port + index))
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


class TasksQueueTest(QueueTest, TestCase):
    target_parameters_flag = True
    task_parameters_flag = True
    data = [SetupProject(executions_per_task=0)]

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
