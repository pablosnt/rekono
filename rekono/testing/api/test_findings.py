from unittest import mock

from findings.enums import DataType, Severity
from findings.models import (OSINT, Credential, Exploit, Technology,
                             Vulnerability)
from testing.api.base import RekonoTestCase
from testing.mocks.defectdojo import defect_dojo_success


class FindingsTest(RekonoTestCase):
    '''Test cases for Findings module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        super().initialize_environment()
        # Create findings entities
        self.domain_osint = OSINT.objects.create(
            execution=self.execution, data='scanme.nmap.org', data_type=DataType.DOMAIN, source='Google'
        )
        self.user_osint = OSINT.objects.create(
            execution=self.execution, data='Test', data_type=DataType.USER, source='DuckDuckGo'
        )
        self.technology = Technology.objects.create(
            execution=self.execution, enumeration=self.enumeration,
            name='Wordpress', version='1.0.0', description='Test'
        )
        self.credential_finding = Credential.objects.create(
            execution=self.execution, technology=self.technology,
            username='test', email='test@test.test', secret='test'
        )
        self.vulnerability = Vulnerability.objects.create(
            execution=self.execution, technology=self.technology,
            name='Log4Shell', description='Log4Shell', severity=Severity.CRITICAL,
            cve='CVE-2021-44228', cwe='CWE-20'
        )
        self.enum_vulnerability = Vulnerability.objects.create(
            execution=self.execution, enumeration=self.enumeration,
            name='Log4Shell', description='Log4Shell', severity=Severity.CRITICAL,
            cve='CVE-2021-44228', cwe='CWE-20'
        )
        self.exploit = Exploit.objects.create(
            execution=self.execution, vulnerability=self.vulnerability,
            name='Easy Exploit', description='RCE for script kiddies', checked=True
        )
        self.tech_exploit = Exploit.objects.create(
            execution=self.execution, technology=self.technology,
            name='Easy Exploit', description='RCE for script kiddies', checked=True
        )
        # Mapping between findings and endpoints
        self.data = [
            (self.domain_osint, 'osint'),
            (self.user_osint, 'osint'),
            (self.host, 'hosts'),
            (self.enumeration, 'enumerations'),
            (self.technology, 'technologies'),
            (self.http_endpoint, 'endpoints'),
            (self.credential_finding, 'credentials'),
            (self.vulnerability, 'vulnerabilities'),
            (self.enum_vulnerability, 'vulnerabilities'),
            (self.exploit, 'exploits'),
            (self.tech_exploit, 'exploits'),
        ]
        self.filter_endpoints = ['vulnerabilities', 'exploits']                 # Endpoints with filters to test
        self.models = {                                                         # Models to test __str__ method
            self.domain_osint: self.domain_osint.data,
            self.user_osint: self.user_osint.data,
            self.host: self.host.address,
            self.enumeration: f'{self.host.__str__()} - {self.enumeration.port}',
            self.technology: f'{self.enumeration.__str__()} - {self.technology.name}',
            self.http_endpoint: f'{self.enumeration.__str__()} - {self.http_endpoint.endpoint}',
            self.credential_finding: f'{self.technology.__str__()} - {self.credential_finding.email} - {self.credential_finding.username} - {self.credential_finding.secret}',      # noqa: E501
            self.vulnerability: f'{self.technology.__str__()} - {self.vulnerability.name} - {self.vulnerability.cve}',
            self.enum_vulnerability: f'{self.enumeration.__str__()} - {self.enum_vulnerability.name} - {self.enum_vulnerability.cve}',      # noqa: E501
            self.exploit: f'{self.vulnerability.__str__()} - {self.exploit.name}',
            self.tech_exploit: f'{self.technology.__str__()} - {self.tech_exploit.name}',
        }

    def test_disable_enable(self) -> None:
        '''Test disable and enable features.'''
        for finding, endpoint in self.data:
            self.api_test(self.client.get, f'/api/{endpoint}/{finding.id}/', expected={'is_active': True})
            self.api_test(self.client.delete, f'/api/{endpoint}/{finding.id}/', 204)                # Disable finding
            self.api_test(self.client.get, f'/api/{endpoint}/{finding.id}/', expected={'is_active': False})
            self.api_test(self.client.post, f'/api/{endpoint}/{finding.id}/enable/', 201)           # Enable finding
            self.api_test(self.client.get, f'/api/{endpoint}/{finding.id}/', expected={'is_active': True})

    def test_create_target_from_osint(self) -> None:
        '''Test target creation feature from OSINT.'''
        # Create target
        self.api_test(
            self.client.post, f'/api/osint/{self.domain_osint.id}/target/', 201,
            expected={'target': self.domain_osint.data, 'type': 'Domain'}
        )

    def test_create_target_from_invalid_osint(self) -> None:
        '''Test target creation feature from invalid OSINT data type.'''
        # OSINT data should be Domain or IP
        self.api_test(self.client.post, f'/api/osint/{self.user_osint.id}/target/', 400)

    def test_filters(self) -> None:
        '''Test filter feature for vulnerabilities and exploits.'''
        for filter, count in [
            (f'enumeration={self.enumeration.id}', 2),                          # Filter by enumeration
            ('enumeration=0', 0),
            (f'enumeration_port={self.enumeration.port}', 2),                   # Filter by enumeration port
            ('enumeration_port=0', 0),
            (f'host={self.host.id}', 2),                                        # Filter by host
            ('host=0', 0),
            (f'host_address={self.host.address}', 2),                           # Filter by host address
            ('host_address=0.0.0.0', 0),
            (f'host_os_type={self.host.os_type}', 2),                           # Filter by host OS type
            ('host_os_type=Windows', 0),
        ]:
            for endpoint in self.filter_endpoints:                              # For each filterable endpoint
                # Filter findings
                content = self.api_test(self.client.get, f'/api/{endpoint}/?{filter}', expected={'count': count})
                if count > 0:                                                   # Expected results
                    findings = [f for f, e in self.data if e == endpoint]       # Get expected findings
                    findings.reverse()                                          # Order findings by creation (so by Id)
                    for index, finding in enumerate(findings):
                        self.assertEqual(finding.id, content['results'][index]['id'])

    @mock.patch('defectdojo.api.DefectDojo.request', defect_dojo_success)       # Mocks Defect-Dojo response
    def test_import_defect_dojo(self) -> None:
        '''Test Defect-Dojo import feature.'''
        engagement_id = {'id': 1}
        new_engagement = {'name': 'Engagement', 'description': 'Engagement'}
        for finding, endpoint in self.data:
            # Import in existing engagement
            self.api_test(self.client.post, f'/api/{endpoint}/{finding.id}/defect-dojo/', 200, data=engagement_id)
            # Import in new engagement
            self.api_test(self.client.post, f'/api/{endpoint}/{finding.id}/defect-dojo/', 200, data=new_engagement)
