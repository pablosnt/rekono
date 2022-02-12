from django.utils import timezone
from executions.models import Execution
from findings.enums import DataType, OSType, PortStatus, Protocol, Severity
from findings.models import (OSINT, Credential, Endpoint, Enumeration, Exploit,
                             Host, Technology, Vulnerability)
from findings.nvd_nist import NvdNist
from projects.models import Project
from targets.models import Target
from tasks.enums import Status
from tasks.models import Task
from testing.api.base import RekonoTestCase
from tools.enums import IntensityRank
from tools.models import Configuration, Tool


class FindingsTest(RekonoTestCase):
    '''Test cases for Findings module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        # Create environment for testing
        self.project = Project.objects.create(
            name='Project Test', description='Project Test', tags=['test'], owner=self.admin
        )
        self.project.members.add(self.admin)
        self.target = Target.objects.create(project=self.project, target='10.10.10.10')
        self.tool = Tool.objects.get(name='Nmap')
        self.configuration = Configuration.objects.get(tool=self.tool, default=True)
        self.task = Task.objects.create(
            target=self.target,
            tool=self.tool,
            configuration=self.configuration,
            intensity=IntensityRank.NORMAL,
            status=Status.COMPLETED,
            start=timezone.now(),
            end=timezone.now()
        )
        self.execution = Execution.objects.create(
            task=self.task,
            status=Status.COMPLETED,
            start=timezone.now(),
            end=timezone.now()
        )
        # Create findings objects
        self.osint = OSINT.objects.create(
            execution=self.execution, data='scanme.nmap.org', data_type=DataType.DOMAIN, source='Google'
        )
        self.osint_alt = OSINT.objects.create(
            execution=self.execution, data='Test', data_type=DataType.USER, source='DuckDuckGo'
        )
        self.host = Host.objects.create(
            execution=self.execution, address='10.10.10.10', os='Ubuntu', os_type=OSType.LINUX
        )
        self.enumeration = Enumeration.objects.create(
            execution=self.execution, host=self.host, port=80,
            port_status=PortStatus.OPEN, protocol=Protocol.TCP, service='http'
        )
        self.technology = Technology.objects.create(
            execution=self.execution, enumeration=self.enumeration,
            name='Wordpress', version='1.0.0', description='Test'
        )
        self.endpoint = Endpoint.objects.create(
            execution=self.execution, enumeration=self.enumeration, endpoint='/robots.txt', status=200
        )
        self.credential = Credential.objects.create(
            execution=self.execution, technology=self.technology,
            username='test', email='test@test.test', secret='test'
        )
        self.vulnerability = Vulnerability.objects.create(
            execution=self.execution, technology=self.technology,
            name='Log4Shell', description='Log4Shell', severity=Severity.CRITICAL,
            cve='CVE-2021-44228', cwe='CWE-20'
        )
        self.exploit = Exploit.objects.create(
            execution=self.execution, vulnerability=self.vulnerability,
            name='Easy Exploit', description='RCE for script kiddies', checked=True
        )
        # Mapping between findings and endpoints
        self.data = [
            (self.osint, 'osint'),
            (self.host, 'hosts'),
            (self.enumeration, 'enumerations'),
            (self.technology, 'technologies'),
            (self.endpoint, 'endpoints'),
            (self.credential, 'credentials'),
            (self.vulnerability, 'vulnerabilities'),
            (self.exploit, 'exploits')
        ]
        self.filter_endpoints = ['vulnerabilities', 'exploits']

    def test_disable_enable(self) -> None:
        '''Test disable and enable features.'''
        for finding, endpoint in self.data:
            self.api_test(self.rekono.get, f'/api/{endpoint}/{finding.id}/', 200, {}, {'is_active': True})
            self.api_test(self.rekono.delete, f'/api/{endpoint}/{finding.id}/', 204)                # Disable finding
            self.api_test(self.rekono.get, f'/api/{endpoint}/{finding.id}/', 200, {}, {'is_active': False})
            self.api_test(self.rekono.post, f'/api/{endpoint}/{finding.id}/enable/', 201)           # Enable finding
            self.api_test(self.rekono.get, f'/api/{endpoint}/{finding.id}/', 200, {}, {'is_active': True})

    def test_create_target_from_osint(self) -> None:
        '''Test target creation feature from OSINT.'''
        expected = {'target': self.osint.data, 'type': 'Domain'}
        # Create target
        content = self.api_test(self.rekono.post, f'/api/osint/{self.osint.id}/target/', 201, {}, expected)
        self.api_test(self.rekono.get, f'/api/targets/{content["id"]}/', 200, {}, expected)

    def test_create_target_from_invalid_osint(self) -> None:
        '''Test target creation feature from invalid OSINT data type.'''
        # OSINT data should be Domain or IP
        self.api_test(self.rekono.post, f'/api/osint/{self.osint_alt.id}/target/', 400)

    def test_filter_by_enumeration(self) -> None:
        '''Test filter vulnerabilities and exploits feature by enumeration.'''
        for finding, endpoint in [(f, e) for f, e in self.data if e in self.filter_endpoints]:
            content = self.api_test(
                self.rekono.get, f'/api/{endpoint}/?enumeration={self.enumeration.id}', 200, {}, {'count': 1}
            )
            self.assertEqual(finding.id, content['results'][0]['id'])

    def test_filter_by_enumeration_not_found(self) -> None:
        '''Test filter vulnerabilities and exploits feature by not found enumeration.'''
        for endpoint in self.filter_endpoints:
            self.api_test(self.rekono.get, f'/api/{endpoint}/?enumeration=0', 200, {}, {'count': 0})

    def test_filter_by_port(self) -> None:
        '''Test filter vulnerabilities and exploits feature by port.'''
        for finding, endpoint in [(f, e) for f, e in self.data if e in self.filter_endpoints]:
            content = self.api_test(
                self.rekono.get, f'/api/{endpoint}/?enumeration_port={self.enumeration.port}', 200, {}, {'count': 1}
            )
            self.assertEqual(finding.id, content['results'][0]['id'])

    def test_filter_by_port_not_found(self) -> None:
        '''Test filter vulnerabilities and exploits feature by not found port.'''
        for endpoint in self.filter_endpoints:
            self.api_test(self.rekono.get, f'/api/{endpoint}/?enumeration_port=0', 200, {}, {'count': 0})

    def test_filter_by_host(self) -> None:
        '''Test filter vulnerabilities and exploits feature by host.'''
        for finding, endpoint in [(f, e) for f, e in self.data if e in self.filter_endpoints]:
            content = self.api_test(self.rekono.get, f'/api/{endpoint}/?host={self.host.id}', 200, {}, {'count': 1})
            self.assertEqual(finding.id, content['results'][0]['id'])

    def test_filter_by_host_not_found(self) -> None:
        '''Test filter vulnerabilities and exploits feature by not found host.'''
        for endpoint in self.filter_endpoints:
            self.api_test(self.rekono.get, f'/api/{endpoint}/?host=0', 200, {}, {'count': 0})

    def test_filter_by_address(self) -> None:
        '''Test filter vulnerabilities and exploits feature by address.'''
        for finding, endpoint in [(f, e) for f, e in self.data if e in self.filter_endpoints]:
            content = self.api_test(
                self.rekono.get, f'/api/{endpoint}/?host_address={self.host.address}', 200, {}, {'count': 1}
            )
            self.assertEqual(finding.id, content['results'][0]['id'])

    def test_filter_by_address_not_found(self) -> None:
        '''Test filter vulnerabilities and exploits feature by not found address.'''
        for endpoint in self.filter_endpoints:
            self.api_test(self.rekono.get, f'/api/{endpoint}/?host_address=0.0.0.0', 200, {}, {'count': 0})

    def test_filter_by_os_type(self) -> None:
        '''Test filter vulnerabilities and exploits feature by OS type.'''
        for finding, endpoint in [(f, e) for f, e in self.data if e in self.filter_endpoints]:
            content = self.api_test(
                self.rekono.get, f'/api/{endpoint}/?host_os_type={self.host.os_type}', 200, {}, {'count': 1}
            )
            self.assertEqual(finding.id, content['results'][0]['id'])

    def test_filter_by_os_type_not_found(self) -> None:
        '''Test filter vulnerabilities and exploits feature by not found OS type.'''
        for endpoint in self.filter_endpoints:
            self.api_test(self.rekono.get, f'/api/{endpoint}/?host_os_type=Windows', 200, {}, {'count': 0})


class NvdNistTest(RekonoTestCase):
    '''Test cases for NVD NIST API.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        self.cve = 'CVE-2021-44228'                                             # Log4shell CVE
        self.old_cve = 'CVE-2010-4422'                                          # CVE with only CVSS version 2
        self.not_found_cve = 'CVE-0000-0000'                                    # Not found CVE

    def get_cve_data(self, cve: str, severity: str) -> None:
        '''Get CVE data from NVD NIST and check response.

        Args:
            cve (str): CVE code
            severity (str): Expected severity
        '''
        nvd_nist = NvdNist(cve)
        self.assertEqual(cve, nvd_nist.cve)
        self.assertEqual(nvd_nist.cve_reference_pattern.format(cve=cve), nvd_nist.reference)
        self.assertEqual(severity, nvd_nist.severity)

    def test_get_cve_data(self) -> None:
        '''Test get CVE data from NVD NIST feature.'''
        self.get_cve_data(self.cve, Severity.CRITICAL)

    def test_cve_data_not_found(self) -> None:
        '''Test get not found CVE data from NVD NIST feature.'''
        self.get_cve_data(self.not_found_cve, Severity.MEDIUM)

    def test_get_old_cve_data(self) -> None:
        '''Test get old CVE data from NVD NIST feature.'''
        self.get_cve_data(self.old_cve, Severity.HIGH)
