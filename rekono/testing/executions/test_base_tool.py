import os
from typing import List
from unittest import mock

import django_rq
from django.test import TestCase
from django.utils import timezone
from executions.models import Execution
from findings.enums import DataType, Protocol, Severity
from findings.models import (OSINT, Credential, Exploit, Finding, Host, Path,
                             Port, Technology, Vulnerability)
from input_types.base import BaseInput
from input_types.models import InputType
from projects.models import Project
from resources.enums import WordlistType
from resources.models import Wordlist
from rq import SimpleWorker
from targets.enums import TargetType
from targets.models import (Target, TargetEndpoint, TargetPort,
                            TargetTechnology, TargetVulnerability)
from tasks.enums import Status
from tasks.models import Task
from testing.mocks.defectdojo import (defect_dojo_error, defect_dojo_success,
                                      defect_dojo_success_multiple)
from tools.enums import IntensityRank, Stage
from tools.exceptions import ToolExecutionException
from tools.models import Argument, Configuration, Input, Intensity, Tool
from tools.tools.base_tool import BaseTool
from tools.utils import get_tool_class_by_name
from users.models import User


class BaseToolTest(TestCase):
    '''Test cases for Base Tool operations.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        self.data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data')    # Testing data path
        self.nikto_report = os.path.join(self.data_path, 'reports', 'nikto', 'default.xml')         # Nikto report
        # Tool and related objects
        self.nikto = Tool.objects.get(name='Nikto')
        self.intensity = Intensity.objects.get(tool=self.nikto, default=True)
        self.configuration = Configuration.objects.create(                      # Configuration with all argument types
            name='Test',
            tool=self.nikto,
            arguments=(
                '{intensity} {test_osint} {test_only_host} {test_host} {test_port} {test_path} '
                '{test_technology} {test_credential} {test_vulnerability} {test_exploit} {test_wordlist}'
            )
        )
        # Initialize auxiliary lists to help data usage
        self.arguments: List[Argument] = []
        self.targets: List[BaseInput] = []
        self.all_findings: List[Finding] = []
        self.required_findings: List[Finding] = []
        self.findings_to_use_targets: List[Finding] = []
        # Initialize environment for testing
        self.wordlist = self.create_wordlists()
        self.create_targets()
        self.create_osint()
        host = self.create_hosts()
        self.port = self.create_ports(host)
        self.create_paths(self.port)
        self.technology = self.create_technologies(self.port)
        self.create_credentials(self.technology)
        self.vulnerability = self.create_vulnerabilities(self.technology)
        self.exploit = self.create_exploits(self.vulnerability)
        # Expected arguments
        self.all_expected = ' '.join([
            '-T3', '--osint http://scanme.nmap.org/', '--only-host 10.10.10.10', '--host 10.10.10.10',
            '--port 443', '--port-commas 80,443', '--endpoint /robots.txt', '--tech Wordpress',
            '--version 1.0.0', '--email test@test.test', '--username test', '--secret test',
            '--vuln CVE-2021-44228', '--exploit Test', f'--wordlist {self.wordlist.path}'
        ]).split(' ')
        self.required_expected = ' '.join([
            '-T3', '--osint http://scanme.nmap.org/', '--only-host 10.10.10.10', '--host 10.10.10.10',
            '--port 443', '--port-commas 80,443', '--endpoint /robots.txt', '--tech Wordpress',
            '--version 1.0.0', '--vuln CVE-2021-44228', '--exploit Test', f'--wordlist {self.wordlist.path}'
        ]).split(' ')
        # Tool instance
        self.tool_class = get_tool_class_by_name(self.nikto.name)               # Related tool class
        self.tool_instance: BaseTool = self.tool_class(                         # Related tool object
            self.new_execution,
            self.nikto,
            self.configuration,
            self.intensity,
            self.arguments
        )

    def create_wordlists(self) -> Wordlist:
        '''Create wordlist data for testing.

        Returns:
            Wordlist: Valid wordlist instance
        '''
        passwords = os.path.join(self.data_path, 'resources', 'passwords_wordlist.txt')        # Password wordlist
        endpoints = os.path.join(self.data_path, 'resources', 'endpoints_wordlist.txt')        # Endpoint wordlist
        # Wordlist filtered due to invalid checksum
        filtered = Wordlist.objects.create(name='Other', type=WordlistType.PASSWORD, path=endpoints, checksum='invalid')
        wordlist = Wordlist.objects.create(name='Test', type=WordlistType.PASSWORD, path=passwords)
        argument = Argument.objects.create(
            tool=self.nikto,
            name='test_wordlist',
            argument='--wordlist {wordlist}',
            required=True
        )
        Input.objects.create(argument=argument, type=InputType.objects.get(name='Wordlist'))
        self.arguments.append(argument)
        self.targets.extend([filtered, wordlist])
        return wordlist

    def create_targets(self) -> None:
        '''Create target data for testing.'''
        self.project = Project.objects.create(
            name='Test', description='Test', tags=['test'],
            defectdojo_product_id=1,
            defectdojo_engagement_by_target=True,
            defectdojo_synchronization=True
        )
        # Target filtered due to target type. Private IP required
        target_filtered = Target.objects.create(project=self.project, target='scanme.nmap.org', type=TargetType.DOMAIN)
        target = Target.objects.create(project=self.project, target='10.10.10.10', type=TargetType.PRIVATE_IP)
        target_port_http = TargetPort.objects.create(target=target, port=80)
        target_port_https = TargetPort.objects.create(target=target, port=443)
        target_endpoint = TargetEndpoint.objects.create(target_port=target_port_http, endpoint='/robots.txt')
        target_technology = TargetTechnology.objects.create(
            target_port=target_port_http,
            name='Wordpress',
            version='1.0.0'
        )
        target_vulnerability = TargetVulnerability.objects.create(target_port=target_port_http, cve='CVE-2021-44228')
        user = User.objects.create_superuser('rekono', 'rekono@rekono.rekono', 'rekono')
        task = Task.objects.create(
            target=target,
            tool=self.nikto,
            configuration=self.configuration,
            intensity=IntensityRank.NORMAL,
            status=Status.COMPLETED,
            start=timezone.now(),
            end=timezone.now(),
            executor=user
        )
        self.first_execution = Execution.objects.create(                        # Execution related to testing findings
            task=task,
            status=Status.COMPLETED,
            start=timezone.now(),
            end=timezone.now()
        )
        self.new_execution = Execution.objects.create(task=task, status=Status.REQUESTED)   # New execution for testing
        self.targets.extend([
            target_filtered, target,
            target_port_http, target_port_https,
            target_endpoint,
            target_technology,
            target_vulnerability
        ])

    def create_osint(self) -> None:
        '''Create OSINT data for testing.'''
        # OSINT entity that can be used as argument. Only DOMAIN and IP are valid
        osint_user = OSINT.objects.create(data='test', data_type=DataType.USER, source='Google')
        osint_user.executions.add(self.first_execution)
        osint_domain = OSINT.objects.create(data='scanme.nmap.org', data_type=DataType.DOMAIN, source='Google')
        osint_domain.executions.add(self.first_execution)
        argument = Argument.objects.create(tool=self.nikto, name='test_osint', argument='--osint {url}', required=True)
        Input.objects.create(argument=argument, type=InputType.objects.get(name='OSINT'))
        self.arguments.append(argument)
        self.all_findings.extend([osint_user, osint_domain])
        self.required_findings.extend([osint_user, osint_domain])
        self.findings_to_use_targets.extend([osint_user, osint_domain])

    def create_hosts(self) -> Host:
        '''Create host data for testing.

        Returns:
            Host: Valid host instance
        '''
        # Host filtered due to address type. Private IP required
        filtered = Host.objects.create(address='scanme.nmap.org')
        filtered.executions.add(self.first_execution)
        host = Host.objects.create(address='10.10.10.10')
        host.executions.add(self.first_execution)
        # Argument with only one input
        argument_only_host = Argument.objects.create(
            tool=self.nikto,
            name='test_only_host',
            argument='--only-host {host}',
            required=True
        )
        # Input filtered by host type: Private IP required
        Input.objects.create(argument=argument_only_host, type=InputType.objects.get(name='Host'), filter='PRIVATE_IP')
        # Argument with multiple inputs
        argument = Argument.objects.create(tool=self.nikto, name='test_host', argument='--host {host}', required=True)
        Input.objects.create(argument=argument, type=InputType.objects.get(name='Path'), order=1)
        Input.objects.create(argument=argument, type=InputType.objects.get(name='Port'), order=2)
        Input.objects.create(argument=argument, type=InputType.objects.get(name='Host'), order=3)
        self.arguments.extend([argument_only_host, argument])
        self.all_findings.extend([filtered, host])
        self.required_findings.extend([filtered, host])
        return host

    def create_ports(self, host: Host) -> Port:
        '''Create port data for testing.

        Args:
            host (Host): Related host

        Returns:
            Port: Valid port instance
        '''
        # Port filtered due to service type. HTTP service required
        filtered = Port.objects.create(host=host, port=22, protocol=Protocol.TCP, service='ssh')
        filtered.executions.add(self.first_execution)
        http = Port.objects.create(host=host, port=80, protocol=Protocol.TCP, service='http')
        http.executions.add(self.first_execution)
        https = Port.objects.create(host=host, port=443, protocol=Protocol.TCP, service='https')
        https.executions.add(self.first_execution)
        argument = Argument.objects.create(
            tool=self.nikto,
            name='test_port',
            argument='--port {port} --port-commas {ports_commas}',
            required=True,
            multiple=True
        )
        # Input filtered by service type: HTTP service required
        Input.objects.create(argument=argument, type=InputType.objects.get(name='Port'), filter='http')
        self.arguments.append(argument)
        self.all_findings.extend([filtered, http, https])
        self.required_findings.extend([filtered, http, https])
        return http

    def create_paths(self, port: Port) -> None:
        '''Create path data for testing.

        Args:
            port (Port): Related port
        '''
        # Path filtered due to HTTP status code. 200 Ok required
        filtered = Path.objects.create(port=port, path='/admin', status=403)
        filtered.executions.add(self.first_execution)
        self.path = Path.objects.create(port=port, path='/robots.txt', status=200)
        self.path.executions.add(self.first_execution)
        argument = Argument.objects.create(
            tool=self.nikto,
            name='test_path',
            argument='--endpoint {endpoint}',
            required=True
        )
        # Input filtered by HTTP status code: HTTP Ok required
        Input.objects.create(argument=argument, type=InputType.objects.get(name='Path'), filter='200')
        self.arguments.append(argument)
        self.all_findings.extend([filtered, self.path])
        self.required_findings.extend([filtered, self.path])

    def create_technologies(self, port: Port) -> Technology:
        '''Create technology data for testing.

        Args:
            port (Port): Related port

        Returns:
            Technology: Valid technology instance
        '''
        # Technology filtered by name: Wordpress required
        filtered = Technology.objects.create(port=port, name='Joomla', version='1.0.0')
        filtered.executions.add(self.first_execution)
        technology = Technology.objects.create(port=port, name='Wordpress', version='1.0.0')
        technology.executions.add(self.first_execution)
        argument = Argument.objects.create(
            tool=self.nikto,
            name='test_technology',
            argument='--tech {technology} --version {version}',
            required=True
        )
        # Input filtered by technology name: Wordpress required
        Input.objects.create(argument=argument, type=InputType.objects.get(name='Technology'), filter='wordpress')
        self.arguments.append(argument)
        self.all_findings.extend([filtered, technology])
        self.required_findings.extend([filtered, technology])
        return technology

    def create_credentials(self, technology: Technology) -> None:
        '''Create credential data for testing.

        Args:
            technology (Technology): Related technology
        '''
        credential = Credential.objects.create(
            technology=technology,
            email='test@test.test',
            username='test',
            secret='test'
        )
        credential.executions.add(self.first_execution)
        argument = Argument.objects.create(
            tool=self.nikto,
            name='test_credential',
            argument='--email {email} --username {username} --secret {secret}',
            required=False
        )
        Input.objects.create(argument=argument, type=InputType.objects.get(name='Credential'))
        self.arguments.append(argument)
        self.all_findings.append(credential)
        self.findings_to_use_targets.append(credential)

    def create_vulnerabilities(self, technology: Technology) -> Vulnerability:
        '''Create vulnerability data for testing.

        Args:
            technology (Technology): Related technology

        Returns:
            Vulnerability: Valid vulnerability instance
        '''
        # Vulnerability filtered due to CVE is required
        filtered_1 = Vulnerability.objects.create(
            technology=technology,
            name='Predefined vulnerability',
            description='Predefined vulnerability',
            severity=Severity.HIGH,
            cwe='CWE-20'
        )
        filtered_1.executions.add(self.first_execution)
        # Vulnerability filtered due to CVE doesn't match the required one
        filtered_2 = Vulnerability.objects.create(
            technology=technology,
            name='CVE found',
            description='CVE found',
            severity=Severity.HIGH,
            cve='CVE-1111-1111',
            cwe='CWE-20'
        )
        filtered_2.executions.add(self.first_execution)
        vulnerability = Vulnerability.objects.create(
            technology=technology,
            name='Log4Shell',
            description='Log4Shell',
            severity=Severity.CRITICAL,
            cve='CVE-2021-44228',
            cwe='CWE-20'
        )
        vulnerability.executions.add(self.first_execution)
        argument = Argument.objects.create(
            tool=self.nikto,
            name='test_vulnerability',
            argument='--vuln {cve}',
            required=True
        )
        # Input filtered by specific CVE
        Input.objects.create(
            argument=argument,
            type=InputType.objects.get(name='Vulnerability'),
            filter='CVE-2021-44228'
        )
        self.arguments.append(argument)
        self.all_findings.extend([filtered_1, filtered_2, vulnerability])
        self.required_findings.extend([filtered_1, filtered_2, vulnerability])
        return vulnerability

    def create_exploits(self, vulnerability: Vulnerability) -> Exploit:
        '''Create exploit data for testing.

        Args:
            vulnerability (Vulnerability): Related vulnerability

        Returns:
            Vulnerability: Valid vulnerability instance
        '''
        exploit = Exploit.objects.create(vulnerability=vulnerability, title='Test')
        exploit.executions.add(self.first_execution)
        argument = Argument.objects.create(
            tool=self.nikto,
            name='test_exploit',
            argument='--exploit {exploit}',
            required=True
        )
        Input.objects.create(argument=argument, type=InputType.objects.get(name='Exploit'))
        self.arguments.append(argument)
        self.all_findings.append(exploit)
        self.required_findings.append(exploit)
        self.findings_to_use_targets.append(exploit)
        return exploit

    def change_input_filters(self) -> None:
        '''Change default input filters to test all filter types.'''
        i = Input.objects.get(
            argument__name='test_only_host',
            type=InputType.objects.get(name='Host')
        )
        i.filter = 'NOTFOUND'                                                   # By unknown address type. All included
        i.save(update_fields=['filter'])
        i = Input.objects.get(
            argument__name='test_port',
            type=InputType.objects.get(name='Port')
        )
        i.filter = '80'                                                         # By port number
        i.save(update_fields=['filter'])
        i = Input.objects.get(
            argument__name='test_path',
            type=InputType.objects.get(name='Path')
        )
        i.filter = '/robot'                                                     # By endpoint content
        i.save(update_fields=['filter'])
        i = Input.objects.get(
            argument__name='test_vulnerability',
            type=InputType.objects.get(name='Vulnerability')
        )
        i.filter = 'CRITICAL'                                                   # By vulnerability severity
        i.save(update_fields=['filter'])

    def test_default_tool_class(self) -> None:
        '''Test get tool class from invalid name.'''
        self.assertEqual(BaseTool, get_tool_class_by_name('NotFound'))

    def test_get_arguments_using_all_findings(self) -> None:
        '''Test get_arguments feature using all the available findings.'''
        arguments = self.tool_instance.get_arguments(self.targets, self.all_findings)
        self.assertEqual(self.all_expected, arguments)

    def test_get_arguments_using_all_findings_without_filters(self) -> None:
        '''Test get_arguments feature using all the available findings without input filters.'''
        Input.objects.all().update(filter=None)                                 # Remove all input filters
        arguments = self.tool_instance.get_arguments(self.targets, self.all_findings)
        expected = ' '.join([
            '-T3', '--osint http://scanme.nmap.org/', '--only-host scanme.nmap.org', '--host 10.10.10.10',
            '--port 443', '--port-commas 22,80,443', '--endpoint /admin', '--tech Joomla',
            '--version 1.0.0', '--email test@test.test', '--username test', '--secret test',
            '--vuln CVE-1111-1111', '--exploit Test', f'--wordlist {self.wordlist.path}'
        ]).split(' ')
        self.assertEqual(expected, arguments)

    def test_get_arguments_using_all_findings_and_alternative_filters(self) -> None:
        '''Test get_arguments feature using all the available findings and other filter types.'''
        self.change_input_filters()                                             # Change filter types
        arguments = self.tool_instance.get_arguments(self.targets, self.all_findings)
        expected = ' '.join([
            '-T3', '--osint http://scanme.nmap.org/', '--only-host scanme.nmap.org', '--host 10.10.10.10',
            '--port 80', '--port-commas 80', '--endpoint /robots.txt', '--tech Wordpress',
            '--version 1.0.0', '--email test@test.test', '--username test', '--secret test',
            '--vuln CVE-2021-44228', '--exploit Test', f'--wordlist {self.wordlist.path}'
        ]).split(' ')
        self.assertEqual(expected, arguments)

    def test_get_arguments_using_required_findings(self) -> None:
        '''Test get_arguments feature using only the required findings.'''
        # Change findings relations for more test situations
        self.vulnerability.technology = None
        self.vulnerability.port = self.port                                     # Change vulnerability relations
        self.vulnerability.save(update_fields=['technology', 'port'])
        self.exploit.vulnerability = None
        self.exploit.technology = self.technology                               # Change technology relations
        self.exploit.save(update_fields=['vulnerability', 'technology'])
        arguments = self.tool_instance.get_arguments(self.targets, self.required_findings)
        self.assertEqual(self.required_expected, arguments)

    def test_get_arguments_using_targets(self) -> None:
        '''Test get_arguments feature using targets.'''
        arguments = self.tool_instance.get_arguments(self.targets, self.findings_to_use_targets)
        self.assertEqual(self.all_expected, arguments)

    def test_get_arguments_using_targets_without_filters(self) -> None:
        '''Test get_arguments feature using targets without input filters.'''
        Input.objects.all().update(filter=None)                                 # Remove all input filters
        arguments = self.tool_instance.get_arguments(self.targets, self.findings_to_use_targets)
        expected = ' '.join([
            '-T3', '--osint http://scanme.nmap.org/', '--only-host scanme.nmap.org', '--host 10.10.10.10',
            '--port 443', '--port-commas 80,443', '--endpoint /robots.txt', '--tech Wordpress',
            '--version 1.0.0', '--email test@test.test', '--username test', '--secret test',
            '--vuln CVE-2021-44228', '--exploit Test', f'--wordlist {self.wordlist.path}'
        ]).split(' ')
        self.assertEqual(expected, arguments)

    def test_get_arguments_using_targets_and_alternative_filters(self) -> None:
        '''Test get_arguments feature using targets and other filter types.'''
        self.change_input_filters()
        arguments = self.tool_instance.get_arguments(self.targets, self.findings_to_use_targets)
        expected = ' '.join([
            '-T3', '--osint http://scanme.nmap.org/', '--only-host scanme.nmap.org', '--host 10.10.10.10',
            '--port 80', '--port-commas 80', '--endpoint /robots.txt', '--tech Wordpress',
            '--version 1.0.0', '--email test@test.test', '--username test', '--secret test',
            '--vuln CVE-2021-44228', '--exploit Test', f'--wordlist {self.wordlist.path}'
        ]).split(' ')
        self.assertEqual(expected, arguments)

    def test_check_arguments(self) -> None:
        '''Test check_arguments feature.'''
        self.assertTrue(self.tool_instance.check_arguments(self.targets, self.required_findings))
        self.assertFalse(self.tool_instance.check_arguments(self.targets, []))
        self.assertTrue(self.tool_instance.check_arguments(self.targets, self.findings_to_use_targets))
        self.assertFalse(self.tool_instance.check_arguments([], self.findings_to_use_targets))

    def test_tool_execution(self) -> None:
        '''Test tool_execution feature using ls command.'''
        # Testing tool with ls command
        tool = Tool.objects.create(name='Test', command='ls', stage=Stage.ENUMERATION)
        self.tool_class = get_tool_class_by_name(tool.name)                     # Related tool class
        self.tool_instance = self.tool_class(                                   # Related tool object
            self.new_execution,
            tool,
            self.configuration,
            self.intensity,
            self.arguments
        )
        errors_count = 0
        try:
            self.tool_instance.tool_execution(['/directory-not-found'], [], [])     # Directory not found
        except ToolExecutionException as ex:
            self.tool_instance.on_error(stderr=str(ex))                         # Test on_error feature
            execution = Execution.objects.get(pk=self.new_execution.id)         # Check execution data
            self.assertEqual(Status.ERROR, execution.status)
            self.assertEqual(str(ex).strip(), execution.output_error)
            errors_count += 1
        self.tool_instance.tool_execution(['/'], [], [])                        # Valid ls execution
        self.assertEqual(1, errors_count)

    def process_findings(self, imported_in_defectdojo: bool) -> None:
        '''Execute process_findings feature using nmap report.

        Args:
            imported_in_defectdojo (bool): Indicate if execution is expected to be imported in Defect-Dojo or not
        '''
        queue = django_rq.get_queue('findings-queue')
        queue.empty()                                                           # Clear findings queue
        self.tool_instance.path_output = self.nikto_report                      # Set nikto report
        self.tool_instance.run(self.targets, self.all_findings)                 # Run tool
        worker = SimpleWorker([queue], connection=queue.connection)             # Create RQ worker for findings queue
        worker.work(burst=True)                                                 # Launch RQ worker
        execution = Execution.objects.get(pk=self.new_execution.id)             # Check execution status
        self.assertEqual(Status.COMPLETED, execution.status)
        self.assertEqual(self.nikto_report, execution.output_file)
        self.assertEqual(imported_in_defectdojo, execution.imported_in_defectdojo)

    @mock.patch('defectdojo.api.DefectDojo.request', defect_dojo_success)       # Mocks Defect-Dojo response
    def test_process_findings_with_defectdojo_target_engagement(self) -> None:
        '''Test process_findings feature with import in Defect-Dojo using target engagement.'''
        self.process_findings(True)

    @mock.patch('defectdojo.api.DefectDojo.request', defect_dojo_success)       # Mocks Defect-Dojo response
    def test_process_findings_with_defectdojo_product_engagement(self) -> None:
        '''Test process_findings feature with import in Defect-Dojo using product engagement.'''
        self.project.defectdojo_engagement_id = 1                               # Product engagement Id
        self.project.defectdojo_engagement_by_target = False                    # Disable engagements by target
        self.project.save(update_fields=['defectdojo_engagement_id', 'defectdojo_engagement_by_target'])
        self.process_findings(True)

    @mock.patch('defectdojo.api.DefectDojo.request', defect_dojo_success)       # Mocks Defect-Dojo response
    @mock.patch('defectdojo.api.DefectDojo.get_product', defect_dojo_error)
    def test_process_findings_with_defectdojo_engagement_not_found(self) -> None:
        '''Test process_findings feature with import in Defect-Dojo using not found engagement.'''
        self.project.defectdojo_engagement_id = 1                               # Product engagement Id
        self.project.defectdojo_engagement_by_target = False                    # Disable engagements by target
        self.project.save(update_fields=['defectdojo_engagement_id', 'defectdojo_engagement_by_target'])
        self.process_findings(False)

    @mock.patch('defectdojo.api.DefectDojo.request', defect_dojo_success)       # Mocks Defect-Dojo response
    def test_process_findings_with_defectdojo_findings_import(self) -> None:
        '''Test process_findings feature with import in Defect-Dojo using the Rekono findings.'''
        self.nikto.defectdojo_scan_type = None                                   # Import findings instead executions
        self.nikto.save(update_fields=['defectdojo_scan_type'])
        self.process_findings(True)

    @mock.patch('defectdojo.api.DefectDojo.request', defect_dojo_success)       # Mocks Defect-Dojo response
    @mock.patch('defectdojo.api.DefectDojo.get_rekono_test_type', defect_dojo_success_multiple)
    def test_process_findings_with_existing_defectdojo_test_type(self) -> None:
        '''Test process_findings feature with import in Defect-Dojo using existing test type.'''
        self.nikto.defectdojo_scan_type = None                                   # Import findings instead executions
        self.nikto.save(update_fields=['defectdojo_scan_type'])
        self.process_findings(True)

    @mock.patch('defectdojo.api.DefectDojo.request', defect_dojo_success)       # Mocks Defect-Dojo response
    @mock.patch('defectdojo.api.DefectDojo.create_rekono_test_type', defect_dojo_error)
    def test_process_findings_with_errors_in_defectdojo_test_type_creation(self) -> None:
        '''Test process_findings feature with unexpected error during Defect-Dojo test type creation.'''
        self.nikto.defectdojo_scan_type = None                                   # Import findings instead executions
        self.nikto.save(update_fields=['defectdojo_scan_type'])
        self.process_findings(False)

    @mock.patch('defectdojo.api.DefectDojo.request', defect_dojo_error)         # Mocks Defect-Dojo response
    def test_process_findings_with_unvailable_defectdojo(self) -> None:
        '''Test process_findings feature with unavailable Defect-Dojo instance.'''
        self.process_findings(False)
