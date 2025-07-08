from executions.enums import Status
from executions.models import Execution
from targets.models import Target
from tasks.models import Task
from tests.framework import RekonoTest
from tools.models import Configuration
from wordlists.enums import WordlistType
from wordlists.models import Wordlist


class GobusterExecutorTest(RekonoTest):
    def setUp(self) -> None:
        super().setUp()
        self._setup_project()
        self.endpoints_wordlist = Wordlist.objects.create(
            name="endpoints",
            type=WordlistType.ENDPOINT,
            path=self.data_dir / "wordlists" / "endpoints_wordlist.txt",
        )
        self.subdomains_wordlist = Wordlist.objects.create(
            name="subdomains",
            type=WordlistType.SUBDOMAIN,
            path=self.data_dir / "wordlists" / "subdomains_wordlist.txt",
        )

    def _setup_executor(self, target: str) -> None:
        self.target = Target.objects.create(project=self.project, target=target, type=Target.get_type(target))
        self.configuration = Configuration.objects.get(tool__name="Gobuster", default=True)
        self.task = Task.objects.create(
            target=self.target,
            configuration=self.configuration,
            executor=self.auditor1,
        )
        self.execution = Execution.objects.create(
            task=self.task,
            configuration=self.configuration,
            status=Status.REQUESTED,
        )
        self.executor = self.configuration.tool.get_executor_class()(self.execution)

    def _test_check_arguments(self, target: str, wordlist: Wordlist, expected: bool) -> None:
        self._setup_executor(target)
        self.assertEqual(expected, self.executor.check_arguments([], [], [], [], [wordlist]))

    def test_check_arguments_no_domain_target(self) -> None:
        self._test_check_arguments("10.10.10.10", self.subdomains_wordlist, False)

    def test_check_arguments_no_wordlist(self) -> None:
        self._test_check_arguments("scanme.nmap.org", self.endpoints_wordlist, False)

    def test_check_arguments(self) -> None:
        self._test_check_arguments("scanme.nmap.org", self.subdomains_wordlist, True)
