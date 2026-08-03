import base64
import os
import sys
from pathlib import Path
from typing import Any
from unittest import mock
from urllib.parse import urlparse

from django.test import TestCase

from authentications.enums import AuthenticationType
from findings.enums import OSINTDataType, TransportProtocol
from findings.models import Port
from framework.models import BaseInput
from settings.models import Settings
from target_ports.models import TargetPort
from tests.framework import BaseTest
from tests.framework.data import SetupProject
from tools.executors.zap import Zap
from tools.models import Argument

# pytype: disable=attribute-error


def get_url(self, host: str, port: int | None = None, endpoint: str | None = None, *args: Any, **kwargs: Any) -> str:
    return f"http://{host}" + (f":{port}" if port else "") + (endpoint or "/")


class ToolExecutorTest(BaseTest, TestCase):
    data = [SetupProject(osint_fields=[{"data": "10.10.10.11", "data_type": OSINTDataType.IP}])]
    fake_tool_flag = True
    target_parameters_flag = True
    task_parameters_flag = True

    def setUp(self) -> None:
        super().setUp()
        self.execution.configuration = self.fake_configuration
        self.execution.save(update_fields=["configuration"])
        self.executor = self.fake_tool.executor_class(self.execution)

    def _test_environment(self, expected: dict[str, Any]) -> None:
        environment = self.executor.get_environment()
        for key, value in expected.items():
            self.assertIsNotNone(environment.get(key))
            self.assertEqual(value, environment.get(key))

    def test_get_environment(self) -> None:
        expected_env = {"KEY1": "value1", "KEY2": "value2"}
        self.executor.arguments = [f"{k}={v}" for k, v in expected_env.items()] + [self.fake_tool.command, "--foo=bar"]
        self._test_environment(expected_env)

    def test_get_environment_skips_sensitive_variables(self) -> None:
        self.executor.arguments = [
            "SAFE=ok",
            "LD_PRELOAD=/tmp/evil.so",
            "PATH=/tmp/attacker",
            self.fake_tool.command,
            "--foo=bar",
        ]
        environment = self.executor.get_environment()
        self.assertEqual("ok", environment.get("SAFE"))
        self.assertIsNone(environment.get("LD_PRELOAD"))
        self.assertNotEqual("/tmp/attacker", environment.get("PATH"))

    def test_get_environment_with_proxies(self) -> None:
        proxy = "10.10.10.10:80"
        expected_env = {f"{key.upper()}_PROXY": proxy for key in ["all", "http", "https", "ftp", "no"]}
        settings = Settings.objects.first()
        for field, value in expected_env.items():
            setattr(settings, field.lower(), value)
        settings.save(update_fields=[f.lower() for f in expected_env.keys()])
        self.executor.arguments = [self.fake_tool.command, "--foo=bar"]
        self._test_environment(expected_env)

    def test_get_environment_excludes_own_venv_from_path(self) -> None:
        self.executor.arguments = [self.fake_tool.command, "--foo=bar"]
        self.assertNotIn(str(Path(sys.executable).parent), self.executor.get_environment()["PATH"].split(os.pathsep))

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_get_arguments_only_findings(self) -> None:
        expected = "-p 10.10.10.11 -p http://10.10.10.10:80/index.html -p 80 -p /index.html -p WordPress -p admin -p CVE-2025-3010 -p ReverseShell 10 -p root"
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
            "-p 10.10.10.10 -p http://10.10.10.10:80/ -p 80 -p WordPress -p CVE-2025-3010 -p root",
            " ".join(
                self.executor.get_arguments([self.host, self.port, self.technology, self.vulnerability], [], [], [], [])
            ),
        )

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_get_arguments_multiple_ports(self) -> None:
        new_port = Port.objects.create(host=self.host, port=443, service="http", protocol=TransportProtocol.TCP)
        new_port.executions.add(self.execution)
        self.assertEqual(
            "-p 10.10.10.10 -p http://10.10.10.10:80/ -p 80,443 -p WordPress -p CVE-2025-3010 -p root",
            " ".join(
                self.executor.get_arguments(
                    [self.host, self.port, new_port, self.technology, self.vulnerability], [], [], [], []
                )
            ),
        )

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_get_arguments_multiple_target_ports(self) -> None:
        second_target_port = TargetPort.objects.create(target=self.target, port=22, path=None)
        self.assertEqual(
            "-p 10.10.10.10 -p http://10.10.10.10:80/ -p 80,22 -p WordPress -p CVE-2025-3010 -p root",
            " ".join(
                self.executor.get_arguments(
                    [self.host, self.technology, self.vulnerability], [self.targetport, second_target_port], [], [], []
                )
            ),
        )

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_get_arguments_with_path_filter(self) -> None:
        self.assertEqual(
            "-p 10.10.10.10 -p http://10.10.10.10:80/index.html -p 80 -p /index.html -p WordPress -p CVE-2025-3010 -p root",
            " ".join(
                self.executor.get_arguments([self.port, self.path, self.technology, self.vulnerability], [], [], [], [])
            ),
        )
        self.path.path = "rootpath/test"
        self.path.save(update_fields=["path"])
        self.targetport.path = "rootpath"
        self.targetport.save(update_fields=["path"])
        self.assertEqual(
            "-p 10.10.10.10 -p http://10.10.10.10:80/rootpath/test -p 80 -p /rootpath/test -p WordPress -p CVE-2025-3010 -p root",
            " ".join(
                self.executor.get_arguments([self.port, self.path, self.technology, self.vulnerability], [], [], [], [])
            ),
        )

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def _test_get_arguments_no_findings(self) -> None:
        self.target.target = "10.10.10.12"
        self.target.save(update_fields=["target"])
        self.assertEqual(
            f"-p 10.10.10.10 -p http://10.10.10.12:80/ -p 80 -p Joomla -p CVE-2023-2222 -p root -p {self.wordlist.path}",
            " ".join(
                self.executor.get_arguments(
                    [], [self.targetport], [self.input_vulnerability], [self.input_technology], [self.wordlist]
                )
            ),
        )

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_get_arguments_no_findings(self) -> None:
        self.target.target = "10.10.10.12"
        self.target.save(update_fields=["target"])
        expected = f"-p 10.10.10.12 -p http://10.10.10.12:80/ -p 80 -p Joomla -p CVE-2023-2222 -p {{secret}} -p {self.wordlist.path}"
        self.assertEqual(
            expected.format(secret="root"),
            " ".join(
                self.executor.get_arguments(
                    [], [self.targetport], [self.input_vulnerability], [self.input_technology], [self.wordlist]
                )
            ),
        )
        self.authentication.type = AuthenticationType.BASIC
        self.authentication.save(update_fields=["type"])
        self.assertEqual(
            expected.format(secret=base64.b64encode("root10:root".encode()).decode()),
            " ".join(
                self.executor.get_arguments(
                    [],
                    [TargetPort.objects.get(pk=self.targetport.id)],
                    [self.input_vulnerability],
                    [self.input_technology],
                    [self.wordlist],
                )
            ),
        )

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_get_arguments_keeps_secret_with_whitespace_in_one_argument(self) -> None:
        secret = "root --output /home/rekono/.rekono/owned.txt"
        self.authentication.secret = secret
        self.authentication.save(update_fields=["_secret"])
        arguments = self.executor.get_arguments(
            [self.host, self.port, self.technology, self.vulnerability], [], [], [], []
        )
        self.assertIn(secret, arguments)
        self.assertNotIn("--output", arguments)

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_get_arguments_keeps_double_quotes_in_one_argument(self) -> None:
        argument = Argument.objects.get(configuration=self.fake_configuration, name="token")
        argument.argument = '-p "{secret}"'
        argument.save(update_fields=["argument"])
        self.authentication.secret = "root secret"
        self.authentication.save(update_fields=["_secret"])
        arguments = self.executor.get_arguments(
            [self.host, self.port, self.technology, self.vulnerability], [], [], [], []
        )
        self.assertIn('"root secret"', arguments)
        self.assertNotIn("root secret", arguments)

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_get_arguments_keeps_empty_value_from_splitting_the_next_one(self) -> None:
        argument = Argument.objects.get(configuration=self.fake_configuration, name="token")
        argument.argument = "-u '{username}' -p '{secret}'"
        argument.save(update_fields=["argument"])
        secret = "root --output /home/rekono/.rekono/owned.txt"
        self.authentication.type = AuthenticationType.BASIC
        self.authentication.name = ""
        self.authentication.secret = secret
        self.authentication.save(update_fields=["type", "name", "_secret"])
        arguments = self.executor.get_arguments(
            [self.host, self.port, self.technology, self.vulnerability], [], [], [], []
        )
        self.assertIn("", arguments)
        self.assertIn(secret, arguments)
        self.assertNotIn("--output", arguments)

    @mock.patch("framework.models.BaseInput.get_url", return_value=None)
    def test_get_arguments_skips_when_required_url_not_reachable(self, get_url_mock: mock.MagicMock) -> None:
        with self.assertRaises(RuntimeError):
            self.executor.get_arguments([self.host, self.port, self.technology, self.vulnerability], [], [], [], [])

    def test_check_arguments_no_base_inputs(self) -> None:
        self.assertFalse(self.executor.check_arguments([], [], [], [], []))

    @mock.patch("framework.models.BaseInput.get_url", get_url)
    def test_check_arguments_missing_one_required_finding(self) -> None:
        self.assertFalse(
            self.executor.check_arguments([self.osint, self.host, self.port, self.technology], [], [], [], [])
        )

    @mock.patch.object(BaseInput._url_cache, "get", return_value=None)
    @mock.patch("framework.models.requests.get", side_effect=Exception("unreachable"))
    def test_get_url_probes_only_task_scoped_port(self, requests_get: mock.MagicMock, *args, **kwargs) -> None:
        task = self.execution.task
        task.target_port = self.targetport
        task.save(update_fields=["target_port"])
        TargetPort.objects.create(target=self.target, port=8080, path=None)
        self.assertIsNone(self.target.get_url(self.target.target, task=task))
        self.assertEqual(
            set([self.targetport.port]), set([urlparse(call.args[0]).port for call in requests_get.call_args_list])
        )

    @mock.patch.object(BaseInput._url_cache, "get", return_value=None)
    @mock.patch("framework.models.requests.get", side_effect=Exception("unreachable"))
    def test_get_url_falls_back_to_all_task_scoped_ports(self, requests_get: mock.MagicMock, *args, **kwargs) -> None:
        task = self.execution.task
        task.target_port = None
        task.save(update_fields=["target_port"])
        tp = TargetPort.objects.create(target=self.target, port=8080, path=None)
        self.assertIsNone(self.target.get_url(self.target.target, task=task))
        self.assertEqual(
            set([self.targetport.port, tp.port]),
            set([urlparse(call.args[0]).port for call in requests_get.call_args_list]),
        )

    @mock.patch.object(BaseInput._url_cache, "get", return_value=None)
    @mock.patch("framework.models.requests.get", side_effect=Exception("unreachable"))
    def test_get_url_falls_back_to_default_ports_without_task(
        self, requests_get: mock.MagicMock, *args, **kwargs
    ) -> None:
        TargetPort.objects.create(target=self.target, port=8080, path=None)
        self.assertIsNone(self.target.get_url(self.target.target))
        self.assertEqual(set([80, 443]), set([urlparse(call.args[0]).port for call in requests_get.call_args_list]))


class ZapExecutorTest(BaseTest, TestCase):
    data = [SetupProject()]
    fake_tool_flag = True
    target_parameters_flag = True
    task_parameters_flag = True

    def setUp(self) -> None:
        super().setUp()
        self.execution.configuration = self.fake_configuration
        self.execution.save(update_fields=["configuration"])
        self.executor = Zap(self.execution)

    def test_before_running_isolates_home_and_proxy_port(self) -> None:
        self.executor.arguments = [self.fake_tool.command, "-cmd"]
        self.executor.before_running()
        arguments = " ".join(self.executor.arguments)
        self.assertIn(f"-dir {self.executor.zap_home}", arguments)
        self.assertIn("-config network.localServers.mainProxy.port=", arguments)
