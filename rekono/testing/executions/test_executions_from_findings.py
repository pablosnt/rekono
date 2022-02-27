from django.test import TestCase
from django.utils import timezone
from executions.models import Execution
from executions.utils import get_executions_from_findings
from findings.models import Endpoint, Enumeration, Host
from input_types.models import InputType
from projects.models import Project
from resources.enums import WordlistType
from resources.models import Wordlist
from targets.enums import TargetType
from targets.models import Target, TargetEndpoint, TargetPort
from tasks.enums import Status
from tasks.models import Task
from tools.enums import IntensityRank, Stage
from tools.models import Argument, Configuration, Input, Tool


class ExecutionsFromFindingsTest(TestCase):
    '''Test cases for get_executions_from_findings CRITICAL feature.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        # Tool for testing
        self.tool = Tool.objects.create(name='Test', command='ls', stage=Stage.ENUMERATION)
        configuration = Configuration.objects.create(name='Test', tool=self.tool, arguments='-la')
        # Host argument
        test_host = Argument.objects.create(tool=self.tool, name='test_host', required=True)
        Input.objects.create(argument=test_host, type=InputType.objects.get(name='Host'))
        # Enumeration argument
        test_enum = Argument.objects.create(tool=self.tool, name='test_enum', required=True, multiple=True)
        Input.objects.create(argument=test_enum, type=InputType.objects.get(name='Vulnerability'), order=1)
        Input.objects.create(argument=test_enum, type=InputType.objects.get(name='Technology'), order=2)
        Input.objects.create(argument=test_enum, type=InputType.objects.get(name='Enumeration'), order=3)
        # Endpoint argument
        test_endp = Argument.objects.create(tool=self.tool, name='test_endp', required=True)
        Input.objects.create(argument=test_endp, type=InputType.objects.get(name='Endpoint'))
        # Wordlist argument
        test_word = Argument.objects.create(tool=self.tool, name='test_word', required=False)
        Input.objects.create(argument=test_word, type=InputType.objects.get(name='Wordlist'))
        # Project > Target > Task > Execution to create findings for testing
        self.project = Project.objects.create(name='Test', description='Test', tags=['test'])
        self.target = Target.objects.create(project=self.project, target='10.10.10.10', type=TargetType.PRIVATE_IP)
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
            status=Status.COMPLETED,
            start=timezone.now(),
            end=timezone.now()
        )

    def test_with_findings(self) -> None:
        '''Test get_executions_from_findings feature with findings. Simulates new executions from previous findings.'''
        # Host 1 with some endpoints in some enumerations
        host_1 = Host.objects.create(execution=self.execution, address='10.10.10.1')
        enum_1_1 = Enumeration.objects.create(execution=self.execution, host=host_1, port=22)
        enum_1_2 = Enumeration.objects.create(execution=self.execution, host=host_1, port=80)
        endp_1_2_1 = Endpoint.objects.create(execution=self.execution, enumeration=enum_1_2, endpoint='/endpoint1')
        endp_1_2_2 = Endpoint.objects.create(execution=self.execution, enumeration=enum_1_2, endpoint='/endpoint2')
        endp_1_2_3 = Endpoint.objects.create(execution=self.execution, enumeration=enum_1_2, endpoint='/endpoint3')
        enum_1_3 = Enumeration.objects.create(execution=self.execution, host=host_1, port=443)
        endp_1_3_1 = Endpoint.objects.create(execution=self.execution, enumeration=enum_1_3, endpoint='/endpoint')
        enum_1_4 = Enumeration.objects.create(execution=self.execution, host=host_1, port=8080)
        endp_1_4_1 = Endpoint.objects.create(execution=self.execution, enumeration=enum_1_4, endpoint='/endpoint')
        enum_1_5 = Enumeration.objects.create(execution=self.execution, host=host_1, port=8000)
        endp_1_5_1 = Endpoint.objects.create(execution=self.execution, enumeration=enum_1_5, endpoint='/endpoint')
        # Host 2 with some endpoints in some enumerations
        host_2 = Host.objects.create(execution=self.execution, address='10.10.10.2')
        enum_2_1 = Enumeration.objects.create(execution=self.execution, host=host_2, port=22)
        enum_2_2 = Enumeration.objects.create(execution=self.execution, host=host_2, port=80)
        endp_2_2_1 = Endpoint.objects.create(execution=self.execution, enumeration=enum_2_2, endpoint='/endpoint1')
        endp_2_2_2 = Endpoint.objects.create(execution=self.execution, enumeration=enum_2_2, endpoint='/endpoint2')
        enum_2_3 = Enumeration.objects.create(execution=self.execution, host=host_2, port=443)
        enum_2_4 = Enumeration.objects.create(execution=self.execution, host=host_2, port=8080)
        endp_2_4_1 = Endpoint.objects.create(execution=self.execution, enumeration=enum_2_4, endpoint='/endpoint1')
        endp_2_4_2 = Endpoint.objects.create(execution=self.execution, enumeration=enum_2_4, endpoint='/endpoint2')
        enum_2_5 = Enumeration.objects.create(execution=self.execution, host=host_2, port=8000)
        # Host 3 with one endpoint for each enumeration
        host_3 = Host.objects.create(execution=self.execution, address='10.10.10.3')
        enum_3_1 = Enumeration.objects.create(execution=self.execution, host=host_3, port=22)
        endp_3_1_1 = Endpoint.objects.create(execution=self.execution, enumeration=enum_3_1, endpoint='/endpoint')
        enum_3_2 = Enumeration.objects.create(execution=self.execution, host=host_3, port=80)
        endp_3_2_1 = Endpoint.objects.create(execution=self.execution, enumeration=enum_3_2, endpoint='/endpoint')
        enum_3_3 = Enumeration.objects.create(execution=self.execution, host=host_3, port=443)
        endp_3_3_1 = Endpoint.objects.create(execution=self.execution, enumeration=enum_3_3, endpoint='/endpoint')
        enum_3_4 = Enumeration.objects.create(execution=self.execution, host=host_3, port=8080)
        endp_3_4_1 = Endpoint.objects.create(execution=self.execution, enumeration=enum_3_4, endpoint='/endpoint')
        enum_3_5 = Enumeration.objects.create(execution=self.execution, host=host_3, port=8000)
        endp_3_5_1 = Endpoint.objects.create(execution=self.execution, enumeration=enum_3_5, endpoint='/endpoint')
        # Host 4 without endpoints
        host_4 = Host.objects.create(execution=self.execution, address='10.10.10.4')
        enum_4_1 = Enumeration.objects.create(execution=self.execution, host=host_4, port=22)
        enum_4_2 = Enumeration.objects.create(execution=self.execution, host=host_4, port=80)
        enum_4_3 = Enumeration.objects.create(execution=self.execution, host=host_4, port=443)
        enum_4_4 = Enumeration.objects.create(execution=self.execution, host=host_4, port=8080)
        enum_4_5 = Enumeration.objects.create(execution=self.execution, host=host_4, port=8000)
        # Host 5 without enumerations
        host_5 = Host.objects.create(execution=self.execution, address='10.10.10.5')
        # Finding list to pass as argument
        findings = [
            host_1, host_2, host_3, host_4, host_5,
            enum_1_1, enum_1_2, enum_1_3, enum_1_4, enum_1_5,
            enum_2_1, enum_2_2, enum_2_3, enum_2_4, enum_2_5,
            enum_3_1, enum_3_2, enum_3_3, enum_3_4, enum_3_5,
            enum_4_1, enum_4_2, enum_4_3, enum_4_4, enum_4_5,
            endp_1_2_1, endp_1_2_2, endp_1_2_3, endp_1_3_1, endp_1_4_1, endp_1_5_1,
            endp_2_2_1, endp_2_2_2, endp_2_4_1, endp_2_4_2,
            endp_3_1_1, endp_3_2_1, endp_3_3_1, endp_3_4_1, endp_3_5_1
        ]
        # Expected executions
        expected = [
            [host_1, enum_1_1, enum_1_2, enum_1_3, enum_1_4, enum_1_5, endp_1_2_1],
            [host_2, enum_2_1, enum_2_2, enum_2_3, enum_2_4, enum_2_5, endp_2_2_1],
            [host_3, enum_3_1, enum_3_2, enum_3_3, enum_3_4, enum_3_5, endp_3_1_1],
            [host_4, enum_4_1, enum_4_2, enum_4_3, enum_4_4, enum_4_5],
            [host_5],
            [host_1, enum_1_1, enum_1_2, enum_1_3, enum_1_4, enum_1_5, endp_1_2_2],
            [host_1, enum_1_1, enum_1_2, enum_1_3, enum_1_4, enum_1_5, endp_1_2_3],
            [host_1, enum_1_1, enum_1_2, enum_1_3, enum_1_4, enum_1_5, endp_1_3_1],
            [host_1, enum_1_1, enum_1_2, enum_1_3, enum_1_4, enum_1_5, endp_1_4_1],
            [host_1, enum_1_1, enum_1_2, enum_1_3, enum_1_4, enum_1_5, endp_1_5_1],
            [host_2, enum_2_1, enum_2_2, enum_2_3, enum_2_4, enum_2_5, endp_2_2_2],
            [host_2, enum_2_1, enum_2_2, enum_2_3, enum_2_4, enum_2_5, endp_2_4_1],
            [host_2, enum_2_1, enum_2_2, enum_2_3, enum_2_4, enum_2_5, endp_2_4_2],
            [host_3, enum_3_1, enum_3_2, enum_3_3, enum_3_4, enum_3_5, endp_3_2_1],
            [host_3, enum_3_1, enum_3_2, enum_3_3, enum_3_4, enum_3_5, endp_3_3_1],
            [host_3, enum_3_1, enum_3_2, enum_3_3, enum_3_4, enum_3_5, endp_3_4_1],
            [host_3, enum_3_1, enum_3_2, enum_3_3, enum_3_4, enum_3_5, endp_3_5_1],
        ]
        executions = get_executions_from_findings(findings, self.tool)
        self.assertEqual(expected, executions)

    def test_with_targets(self) -> None:
        '''Test get_executions_from_findings feature with targets. Simulates initial new executions.'''
        # Target ports with some target endpoints
        tp_1 = TargetPort.objects.create(target=self.target, port=22)
        tp_2 = TargetPort.objects.create(target=self.target, port=80)
        te_2_1 = TargetEndpoint.objects.create(target_port=tp_2, endpoint='/endpoint')
        tp_3 = TargetPort.objects.create(target=self.target, port=443)
        te_3_1 = TargetEndpoint.objects.create(target_port=tp_3, endpoint='/endpoint1')
        te_3_2 = TargetEndpoint.objects.create(target_port=tp_3, endpoint='/endpoint2')
        tp_4 = TargetPort.objects.create(target=self.target, port=8080)
        te_4_1 = TargetEndpoint.objects.create(target_port=tp_4, endpoint='/endpoint1')
        te_4_2 = TargetEndpoint.objects.create(target_port=tp_4, endpoint='/endpoint2')
        te_4_3 = TargetEndpoint.objects.create(target_port=tp_4, endpoint='/endpoint3')
        tp_5 = TargetPort.objects.create(target=self.target, port=8000)
        # Wordlists
        wl_1 = Wordlist.objects.create(name='Wordlist 1', type=WordlistType.PASSWORD, path='/some/path/1')
        wl_2 = Wordlist.objects.create(name='Wordlist 2', type=WordlistType.PASSWORD, path='/some/path/2')
        wl_3 = Wordlist.objects.create(name='Wordlist 3', type=WordlistType.ENDPOINT, path='/some/path/3')
        # Target list to pass as argument
        targets = [
            wl_1, wl_2, wl_3,
            self.target,
            tp_1, tp_2, tp_3, tp_4, tp_5,
            te_2_1, te_3_1, te_3_2, te_4_1, te_4_2, te_4_3
        ]
        # Expected executions
        expected = [
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, te_2_1, wl_1],
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, te_3_1, wl_1],
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, te_3_2, wl_1],
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, te_4_1, wl_1],
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, te_4_2, wl_1],
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, te_4_3, wl_1],
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, te_2_1, wl_2],
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, te_3_1, wl_2],
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, te_3_2, wl_2],
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, te_4_1, wl_2],
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, te_4_2, wl_2],
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, te_4_3, wl_2],
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, te_2_1, wl_3],
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, te_3_1, wl_3],
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, te_3_2, wl_3],
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, te_4_1, wl_3],
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, te_4_2, wl_3],
            [self.target, tp_1, tp_2, tp_3, tp_4, tp_5, te_4_3, wl_3],
        ]
        executions = get_executions_from_findings(targets, self.tool)
        self.assertEqual(expected, executions)
