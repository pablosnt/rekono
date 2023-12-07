from executions.enums import Status
from executions.models import Execution
from processes.models import Process, Step
from tasks.models import Task
from tasks.queues import TasksQueue
from tests.framework import RekonoTest
from tools.enums import Intensity
from tools.models import Configuration


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
            Execution.objects.count(),
        )

    def test_process_task(self) -> None:
        self._test_process_task(Intensity.INSANE)
        execution_id = 1
        for configuration_id, group in [
            (19, 1),  # theHarvester
            (30, 1),  # EmailFinder
            (31, 1),  # EmailHarvester
            (46, 1),  # Gobuster
            (38, 1),  # Nmap
            (47, 2),  # Gobuster
            (22, 2),  # Sslscan
            (23, 2),  # SSLyze
            (28, 2),  # Log4Shell Scan
            (29, 2),  # Log4Shell Scan
            (34, 2),  # SSH Audit
            (24, 2),  # CMSeeK
            (33, 2),  # GitDumper & GitLeaks
            (15, 2),  # Dirsearch
            (36, 2),  # SMB Map
            (48, 2),  # Gobuster
            (21, 2),  # Nikto
            (25, 2),  # ZAP
            (39, 2),  # Nuclei
            (32, 2),  # JoomScan
            (26, 3),  # SearchSploit
            (27, 3),  # Metasploit
        ]:
            self._validate_execution(
                Execution.objects.get(configuration__id=configuration_id),
                self.task.id,
                execution_id,
                configuration_id,
                group,
            )
            execution_id += 1

    def test_process_task_sneaky_intensity(self) -> None:
        self._test_process_task(Intensity.SNEAKY)
        execution_id = 1
        for configuration_id, group in [
            (23, None),  # SSLyze
            (28, None),  # Log4Shell Scan
            (29, None),  # Log4Shell Scan
            (34, None),  # SSH Audit
            (24, None),  # CMSeeK
            (33, None),  # GitDumper & GitLeaks
            (36, None),  # SMB Map
            (21, None),  # Nikto
            (25, None),  # ZAP
            (39, None),  # Nuclei
            (32, None),  # JoomScan
            (19, 1),  # theHarvester
            (30, 1),  # EmailFinder
            (31, 1),  # EmailHarvester
            (46, 1),  # Gobuster
            (38, 1),  # Nmap
            (47, 2),  # Gobuster
            (22, 2),  # Sslscan
            (15, 2),  # Dirsearch
            (48, 2),  # Gobuster
            (26, 3),  # SearchSploit
            (27, 3),  # Metasploit
        ]:
            self._validate_execution(
                Execution.objects.get(configuration__id=configuration_id),
                self.task.id,
                execution_id,
                configuration_id,
                group or 1,
                Status.REQUESTED if group is not None else Status.SKIPPED,
            )
            execution_id += 1
