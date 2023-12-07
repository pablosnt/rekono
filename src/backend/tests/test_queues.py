from executions.enums import Status
from executions.models import Execution
from processes.models import Process, Step
from tasks.models import Task
from tasks.queues import TasksQueue
from tests.framework import RekonoTest
from tools.enums import Intensity
from tools.models import Configuration

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
    (15, 2, 2),  # Dirsearch
    (36, 2, None),  # SMB Map
    (48, 2, 2),  # Gobuster
    (21, 2, None),  # Nikto
    (25, 2, None),  # ZAP
    (39, 2, None),  # Nuclei
    (32, 2, None),  # JoomScan
    (26, 3, 3),  # SearchSploit
    (27, 3, 3),  # Metasploit
]


class TasksQueueTest(RekonoTest):
    def setUp(self) -> None:
        super().setUp()
        self._setup_task_user_provided_entities()
        self.queue = TasksQueue()

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
        self.assertEqual(group, execution.group)
        self.assertEqual(status, execution.status)
        self.assertIsNone(execution.start)

    def test_tool_task(self) -> None:
        configuration = Configuration.objects.get(tool__id=1, default=True)
        task = Task.objects.create(
            target=self.target, configuration=configuration, intensity=Intensity.INSANE
        )
        task.wordlists.add(self.wordlist)
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
                for e in expected_executions
                if e[group_index] is None
            ] + [
                (e[0], e[group_index])
                for e in expected_executions
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

    def test_calculate_executions(self) -> None:
        pass
