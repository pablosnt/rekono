from typing import Any

from django.db.models import Model
from django.test import TestCase
from django.utils import timezone
from findings.models import Host, Path, Port
from input_types.base import BaseInput
from input_types.models import InputType
from projects.models import Project
from resources.enums import WordlistType
from resources.models import Wordlist
from targets.enums import TargetType
from targets.models import Target, TargetPort
from tasks.enums import Status
from tasks.models import Task
from tools.enums import IntensityRank, Stage
from tools.models import Argument, Configuration, Input, Tool

from executions.models import Execution
from executions.utils import get_executions_from_findings


class ExecutionsFromFindingsTest(TestCase):
    '''Test cases for get_executions_from_findings CRITICAL feature.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        # Tool for testing
        self.tool = Tool.objects.create(name='Test', command='ls')
        configuration = Configuration.objects.create(
            name='Test',
            tool=self.tool,
            arguments='-la',
            stage=Stage.ENUMERATION
        )
        # Host argument
        test_host = Argument.objects.create(tool=self.tool, name='test_host', required=True)
        Input.objects.create(argument=test_host, type=InputType.objects.get(name='Host'))
        # Port argument
        test_enum = Argument.objects.create(tool=self.tool, name='test_enum', required=True, multiple=True)
        Input.objects.create(argument=test_enum, type=InputType.objects.get(name='Vulnerability'), order=1)
        Input.objects.create(argument=test_enum, type=InputType.objects.get(name='Technology'), order=2)
        Input.objects.create(argument=test_enum, type=InputType.objects.get(name='Port'), order=3)
        # Path argument
        test_path = Argument.objects.create(tool=self.tool, name='test_path', required=False)
        Input.objects.create(argument=test_path, type=InputType.objects.get(name='Path'))
        # Wordlist argument
        test_word = Argument.objects.create(tool=self.tool, name='test_word', required=False)
        Input.objects.create(argument=test_word, type=InputType.objects.get(name='Wordlist'))
        # Project > Target > Task > Execution to create findings for testing
        self.project = Project.objects.create(name='Test', description='Test', tags=['test'])
        self.target = Target.objects.create(project=self.project, target='scanme.nmap.org', type=TargetType.DOMAIN)
        task = Task.objects.create(
            target=self.target,
            tool=self.tool,
            configuration=configuration,
            intensity=IntensityRank.NORMAL,
            status=Status.COMPLETED,
            start=timezone.now(),
            end=timezone.now()
        )
        self.execution = Execution.objects.create(
            task=task,
            tool=task.tool,
            configuration=task.configuration,
            status=Status.COMPLETED,
            start=timezone.now(),
            end=timezone.now()
        )

    def create_finding(self, finding_type: Model, **fields: Any) -> BaseInput:
        '''Create finding and assign it to the testing execution.

        Args:
            finding_type (Model): Finding model

        Returns:
            Finding: Finding instance
        '''
        finding = finding_type.objects.create(**fields)
        finding.executions.add(self.execution)                                  # Add execution to the finding
        return finding

    def test_with_findings(self) -> None:
        '''Test get_executions_from_findings feature with findings.'''
        # Host 1 with some endpoints in some ports
        host_1 = self.create_finding(Host, address='10.10.10.1')
        port_1_1 = self.create_finding(Port, host=host_1, port=22)
        port_1_2 = self.create_finding(Port, host=host_1, port=80)
        path_1_2_1 = self.create_finding(Path, port=port_1_2, path='/endpoint1')
        path_1_2_2 = self.create_finding(Path, port=port_1_2, path='/endpoint2')
        path_1_2_3 = self.create_finding(Path, port=port_1_2, path='/endpoint3')
        port_1_3 = self.create_finding(Port, host=host_1, port=443)
        path_1_3_1 = self.create_finding(Path, port=port_1_3, path='/endpoint')
        port_1_4 = self.create_finding(Port, host=host_1, port=8080)
        path_1_4_1 = self.create_finding(Path, port=port_1_4, path='/endpoint')
        port_1_5 = self.create_finding(Port, host=host_1, port=8000)
        path_1_5_1 = self.create_finding(Path, port=port_1_5, path='/endpoint')
        # Host 2 with some endpoints in some ports
        host_2 = self.create_finding(Host, address='10.10.10.2')
        port_2_1 = self.create_finding(Port, host=host_2, port=22)
        port_2_2 = self.create_finding(Port, host=host_2, port=80)
        path_2_2_1 = self.create_finding(Path, port=port_2_2, path='/endpoint1')
        path_2_2_2 = self.create_finding(Path, port=port_2_2, path='/endpoint2')
        port_2_3 = self.create_finding(Port, host=host_2, port=443)
        port_2_4 = self.create_finding(Port, host=host_2, port=8080)
        path_2_4_1 = self.create_finding(Path, port=port_2_4, path='/endpoint1')
        path_2_4_2 = self.create_finding(Path, port=port_2_4, path='/endpoint2')
        port_2_5 = self.create_finding(Port, host=host_2, port=8000)
        # Host 3 with one endpoint for each port
        host_3 = self.create_finding(Host, address='10.10.10.3')
        port_3_1 = self.create_finding(Port, host=host_3, port=22)
        path_3_1_1 = self.create_finding(Path, port=port_3_1, path='/endpoint')
        port_3_2 = self.create_finding(Port, host=host_3, port=80)
        path_3_2_1 = self.create_finding(Path, port=port_3_2, path='/endpoint')
        port_3_3 = self.create_finding(Port, host=host_3, port=443)
        path_3_3_1 = self.create_finding(Path, port=port_3_3, path='/endpoint')
        port_3_4 = self.create_finding(Port, host=host_3, port=8080)
        path_3_4_1 = self.create_finding(Path, port=port_3_4, path='/endpoint')
        port_3_5 = self.create_finding(Port, host=host_3, port=8000)
        path_3_5_1 = self.create_finding(Path, port=port_3_5, path='/endpoint')
        # Host 4 without endpoints
        host_4 = self.create_finding(Host, address='10.10.10.4')
        port_4_1 = self.create_finding(Port, host=host_4, port=22)
        port_4_2 = self.create_finding(Port, host=host_4, port=80)
        port_4_3 = self.create_finding(Port, host=host_4, port=443)
        port_4_4 = self.create_finding(Port, host=host_4, port=8080)
        port_4_5 = self.create_finding(Port, host=host_4, port=8000)
        # Host 5 without ports
        host_5 = self.create_finding(Host, address='10.10.10.5')
        # Finding list to pass as argument
        findings = [
            host_1, host_2, host_3, host_4, host_5,
            port_1_1, port_1_2, port_1_3, port_1_4, port_1_5,
            port_2_1, port_2_2, port_2_3, port_2_4, port_2_5,
            port_3_1, port_3_2, port_3_3, port_3_4, port_3_5,
            port_4_1, port_4_2, port_4_3, port_4_4, port_4_5,
            path_1_2_1, path_1_2_2, path_1_2_3, path_1_3_1, path_1_4_1, path_1_5_1,
            path_2_2_1, path_2_2_2, path_2_4_1, path_2_4_2,
            path_3_1_1, path_3_2_1, path_3_3_1, path_3_4_1, path_3_5_1
        ]
        # Expected executions
        expected = [
            [host_1, port_1_1, port_1_2, port_1_3, port_1_4, port_1_5, path_1_2_1],
            [host_2, port_2_1, port_2_2, port_2_3, port_2_4, port_2_5, path_2_2_1],
            [host_3, port_3_1, port_3_2, port_3_3, port_3_4, port_3_5, path_3_1_1],
            [host_4, port_4_1, port_4_2, port_4_3, port_4_4, port_4_5],
            [host_5],
            [host_1, port_1_1, port_1_2, port_1_3, port_1_4, port_1_5, path_1_2_2],
            [host_1, port_1_1, port_1_2, port_1_3, port_1_4, port_1_5, path_1_2_3],
            [host_1, port_1_1, port_1_2, port_1_3, port_1_4, port_1_5, path_1_3_1],
            [host_1, port_1_1, port_1_2, port_1_3, port_1_4, port_1_5, path_1_4_1],
            [host_1, port_1_1, port_1_2, port_1_3, port_1_4, port_1_5, path_1_5_1],
            [host_2, port_2_1, port_2_2, port_2_3, port_2_4, port_2_5, path_2_2_2],
            [host_2, port_2_1, port_2_2, port_2_3, port_2_4, port_2_5, path_2_4_1],
            [host_2, port_2_1, port_2_2, port_2_3, port_2_4, port_2_5, path_2_4_2],
            [host_3, port_3_1, port_3_2, port_3_3, port_3_4, port_3_5, path_3_2_1],
            [host_3, port_3_1, port_3_2, port_3_3, port_3_4, port_3_5, path_3_3_1],
            [host_3, port_3_1, port_3_2, port_3_3, port_3_4, port_3_5, path_3_4_1],
            [host_3, port_3_1, port_3_2, port_3_3, port_3_4, port_3_5, path_3_5_1],
        ]
        executions = get_executions_from_findings(findings, self.tool)
        self.assertEqual(expected, executions)

    def test_with_only_one_finding_type(self) -> None:
        '''Test get_executions_from_findings feature with findings.'''
        host_1 = self.create_finding(Host, address='10.10.10.1')
        host_2 = self.create_finding(Host, address='10.10.10.2')
        host_3 = self.create_finding(Host, address='10.10.10.3')
        host_4 = self.create_finding(Host, address='10.10.10.4')
        findings = [host_1, host_2, host_3, host_4]                             # Finding list to pass as argument
        expected = [[host_1], [host_2], [host_3], [host_4]]                     # Expected executions
        executions = get_executions_from_findings(findings, self.tool)
        self.assertEqual(expected, executions)

    def test_with_targets(self) -> None:
        '''Test get_executions_from_findings feature with targets.'''
        # Target ports
        tp_1 = TargetPort.objects.create(target=self.target, port=22)
        tp_2 = TargetPort.objects.create(target=self.target, port=80)
        tp_3 = TargetPort.objects.create(target=self.target, port=443)
        tp_4 = TargetPort.objects.create(target=self.target, port=8080)
        tp_5 = TargetPort.objects.create(target=self.target, port=8000)
        # Wordlists
        wl_1 = Wordlist.objects.create(name='Wordlist 1', type=WordlistType.ENDPOINT, path='/some/path/1')
        wl_2 = Wordlist.objects.create(name='Wordlist 2', type=WordlistType.ENDPOINT, path='/some/path/2')
        wl_3 = Wordlist.objects.create(name='Wordlist 3', type=WordlistType.ENDPOINT, path='/some/path/3')
        # Target list to pass as argument
        targets = [
            wl_1, wl_2, wl_3,
            self.target,
            tp_1, tp_2, tp_3, tp_4, tp_5
        ]
        # Expected executions
        expected = [
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, wl_1],
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, wl_2],
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, wl_3],
        ]
        executions = get_executions_from_findings(targets, self.tool)
        self.assertEqual(expected, executions)
