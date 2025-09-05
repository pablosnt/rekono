import base64
from typing import Any
from unittest import mock

from authentications.enums import AuthenticationType
from executions.enums import Status
from executions.models import Execution
from findings.enums import OSINTDataType
from findings.models import Port
from settings.models import Settings
from targets.models import Target
from tasks.models import Task
from tests.framework import BaseTest
from tools.executors.base import BaseExecutor
from tools.models import Configuration
from wordlists.enums import WordlistType
from wordlists.models import Wordlist


def get_url(self, host: str, port: int | None = None, endpoint: str | None = None, *args: Any) -> str:
    return f"http://{host}" + (f":{port}" if port else "") + (endpoint or "/")


class ToolExecutorTest(BaseTest):
    setup_entities = ["fake_execution", "findings"]

    def setUp(self) -> None:
        super().setUp()
        self.osint.data = "10.10.10.11"
        self.osint.data_type = OSINTDataType.IP
        self.osint.save(update_fields=["data", "data_type"])
        self.executor = self.fake_tool.executor_class(self.selected_execution)

    def _test_environment(self, expected: dict[str, Any]) -> None:
        environment = self.executor.get_environment()
        for key, value in expected.items():
            self.assertIsNotNone(environment.get(key))
            self.assertEqual(value, environment.get(key))

    def test_get_environment(self) -> None:
        expected_env = {"KEY1": "value1", "KEY2": "value2"}
        self.executor.arguments = [f"{k}={v}" for k, v in expected_env.items()] + [self.fake_tool.command, "--foo=bar"]
        self._test_environment(expected_env)

    def test_get_environment_with_proxies(self) -> None:
        proxy = "10.10.10.10:80"
        expected_env = {f"{key.upper()}_PROXY": proxy for key in ["all", "http", "https", "ftp", "no"]}
        settings = Settings.objects.first()
        for field, value in expected_env.items():
            setattr(settings, field.lower(), value)
        settings.save(update_fields=[f.lower() for f in expected_env.keys()])
        self.executor.arguments = [self.fake_tool.command, "--foo=bar"]
        self._test_environment(expected_env)

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_get_arguments_only_findings(self) -> None:
        expected = "-p 10.10.10.11 -p http://10.10.10.10:80/index.php -p 80 -p /index.php -p WordPress -p admin -p CVE-2023-1111 -p ReverseShell"
        self.assertEqual(expected, " ".join(self.executor.get_arguments(self.findings, [], [], [], [])))
        self.vulnerability.technology = None
        self.vulnerability.port = self.port
        self.vulnerability.save(update_fields=["port", "technology"])
        self.exploit.vulnerability = None
        self.exploit.technology = self.technology
        self.exploit.save(update_fields=["vulnerability", "technology"])
        self.assertEqual(expected, " ".join(self.executor.get_arguments(self.findings, [], [], [], [])))

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_get_arguments_only_required_findings(self) -> None:
        self.assertEqual(
            "-p 10.10.10.10 -p http://10.10.10.10:80/ -p 80 -p WordPress -p CVE-2023-1111",
            " ".join(
                self.executor.get_arguments([self.host, self.port, self.technology, self.vulnerability], [], [], [], [])
            ),
        )

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_get_arguments_multiple_ports(self) -> None:
        new_port = Port.objects.create(**{**self.raw_findings[Port], "host": self.host, "port": 443})
        new_port.executions.add(self.selected_execution)
        self.assertEqual(
            "-p 10.10.10.10 -p http://10.10.10.10:80/ -p 80,443 -p WordPress -p CVE-2023-1111",
            " ".join(
                self.executor.get_arguments(
                    [self.host, self.port, new_port, self.technology, self.vulnerability], [], [], [], []
                )
            ),
        )

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_get_arguments_with_path_filter(self) -> None:
        self.setup_target_and_task_parameters()
        self.assertEqual(
            "-p 10.10.10.10 -p http://10.10.10.10:80/ -p 80 -p WordPress -p CVE-2023-1111 -p root",
            " ".join(
                self.executor.get_arguments([self.port, self.path, self.technology, self.vulnerability], [], [], [], [])
            ),
        )
        self.path.path = "rootpath/test"
        self.path.save(update_fields=["path"])
        self.target_port.path = "rootpath"
        self.target_port.save(update_fields=["path"])
        self.assertEqual(
            "-p 10.10.10.10 -p http://10.10.10.10:80/rootpath/test -p 80 -p /rootpath/test -p WordPress -p CVE-2023-1111 -p root",
            " ".join(
                self.executor.get_arguments([self.port, self.path, self.technology, self.vulnerability], [], [], [], [])
            ),
        )

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def _test_get_arguments_no_findings(self) -> None:
        self.target.target = "10.10.10.12"
        self.target.save(update_fields=["target"])
        self.assertEqual(
            f"-p 10.10.10.10 -p http://10.10.10.12:80/login.php -p 80 -p /login.php -p Joomla -p CVE-2023-2222 -p {base64.b64encode('root:root'.encode()).decode() if self.authentication.type == AuthenticationType.BASIC else 'root'} -p {self.wordlist.path}",
            " ".join(
                self.executor.get_arguments(
                    [], [self.target_port], [self.input_vulnerability], [self.input_technology], [self.wordlist]
                )
            ),
        )

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_get_arguments_no_findings(self) -> None:
        self.setup_target_and_task_parameters()
        self.target.target = "10.10.10.12"
        self.target.save(update_fields=["target"])
        expected = f"-p 10.10.10.12 -p http://10.10.10.12:80/login.php -p 80 -p /login.php -p Joomla -p CVE-2023-2222 -p {{secret}} -p {self.wordlist.path}"
        self.assertEqual(
            expected.format(secret="root"),
            " ".join(
                self.executor.get_arguments(
                    [], [self.target_port], [self.input_vulnerability], [self.input_technology], [self.wordlist]
                )
            ),
        )
        self.authentication.type = AuthenticationType.BASIC
        self.authentication.save(update_fields=["type"])
        self.assertEqual(
            expected.format(secret=base64.b64encode("root:root".encode()).decode()),
            " ".join(
                self.executor.get_arguments(
                    [], [self.target_port], [self.input_vulnerability], [self.input_technology], [self.wordlist]
                )
            ),
        )

    def test_check_arguments_no_base_inputs(self) -> None:
        self.assertFalse(self.executor.check_arguments([], [], [], [], []))

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_check_arguments_missing_one_required_finding(self) -> None:
        self.assertFalse(
            self.executor.check_arguments([self.osint, self.host, self.port, self.technology], [], [], [], [])
        )


class GobusterExecutorTest(BaseTest):
    setup_entities = ["project"]

    def setUp(self):
        super().setUp()
        self.endpoints_wordlist = Wordlist.objects.create(
            name="endpoints", type=WordlistType.ENDPOINT, path=self.data_dir / "wordlists" / "endpoints_wordlist.txt"
        )
        self.subdomains_wordlist = Wordlist.objects.create(
            name="subdomains", type=WordlistType.SUBDOMAIN, path=self.data_dir / "wordlists" / "subdomains_wordlist.txt"
        )

    def _get_executor(self, target: str) -> BaseExecutor:
        configuration = Configuration.objects.get(tool__name="Gobuster", default=True)
        return configuration.tool.executor_class(
            Execution.objects.create(
                task=Task.objects.create(
                    target=Target.objects.create(project=self.project, target=target, type=Target.get_type(target)),
                    configuration=configuration,
                    executor=self.auditor1,
                ),
                configuration=configuration,
                status=Status.REQUESTED,
            )
        )

    def test_check_arguments_no_domain_target(self) -> None:
        self.assertFalse(self._get_executor("10.10.10.10").check_arguments([], [], [], [], [self.subdomains_wordlist]))

    def test_check_arguments_no_wordlist(self) -> None:
        self.assertFalse(
            self._get_executor("scanme.nmap.org").check_arguments([], [], [], [], [self.endpoints_wordlist])
        )

    def test_check_arguments(self) -> None:
        self.assertTrue(
            self._get_executor("scanme.nmap.org").check_arguments([], [], [], [], [self.subdomains_wordlist])
        )
