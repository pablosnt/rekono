from findings.enums import DataType, Severity
from findings.models import (OSINT, Credential, Exploit, Technology,
                             Vulnerability)
from testing.api.base import RekonoApiTestCase


class FindingsTest(RekonoApiTestCase):
    '''Test cases for Findings module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        super().initialize_environment()
        # Create findings entities
        self.domain_osint = OSINT.objects.create(data='nmap.org', data_type=DataType.DOMAIN, source='Google')
        self.domain_osint.executions.add(self.execution)
        self.user_osint = OSINT.objects.create(data='Test', data_type=DataType.USER, source='DuckDuckGo')
        self.user_osint.executions.add(self.execution)
        self.technology = Technology.objects.create(
            port=self.port,
            name='Wordpress', version='1.0.0',
            description='Test'
        )
        self.technology.executions.add(self.execution)
        self.credential_finding = Credential.objects.create(
            technology=self.technology,
            username='test',
            email='test@test.test',
            secret='test'
        )
        self.credential_finding.executions.add(self.execution)
        self.vulnerability = Vulnerability.objects.create(
            technology=self.technology,
            name='Log4Shell', description='Log4Shell',
            severity=Severity.CRITICAL,
            cve='CVE-2021-44228', cwe='CWE-20'
        )
        self.vulnerability.executions.add(self.execution)
        self.port_vulnerability = Vulnerability.objects.create(
            port=self.port,
            name='Log4Shell', description='Log4Shell',
            severity=Severity.CRITICAL,
            cve='CVE-2021-44228', cwe='CWE-20'
        )
        self.port_vulnerability.executions.add(self.execution)
        self.exploit = Exploit.objects.create(
            vulnerability=self.vulnerability,
            title='Easy Exploit'
        )
        self.exploit.executions.add(self.execution)
        self.tech_exploit = Exploit.objects.create(
            technology=self.technology,
            title='Easy Exploit'
        )
        self.tech_exploit.executions.add(self.execution)
        # Mapping between findings and endpoints
        self.data = [
            (self.domain_osint, 'osint'),
            (self.user_osint, 'osint'),
            (self.host, 'hosts'),
            (self.port, 'ports'),
            (self.technology, 'technologies'),
            (self.http_path, 'paths'),
            (self.credential_finding, 'credentials'),
            (self.vulnerability, 'vulnerabilities'),
            (self.port_vulnerability, 'vulnerabilities'),
            (self.exploit, 'exploits'),
            (self.tech_exploit, 'exploits'),
        ]
        self.filter_paths = ['vulnerabilities', 'exploits']                     # Paths with filters to test
        self.models = {                                                         # Models to test __str__ method
            self.domain_osint: self.domain_osint.data,
            self.user_osint: self.user_osint.data,
            self.host: self.host.address,
            self.port: f'{self.host.__str__()} - {self.port.port}',
            self.technology: f'{self.port.__str__()} - {self.technology.name}',
            self.http_path: f'{self.port.__str__()} - {self.http_path.path}',
            self.credential_finding: (
                f'{self.technology.__str__()} - {self.credential_finding.email} - '
                f'{self.credential_finding.username} - {self.credential_finding.secret}'
            ),
            self.vulnerability: f'{self.technology.__str__()} - {self.vulnerability.name} - {self.vulnerability.cve}',
            self.port_vulnerability: (
                f'{self.port.__str__()} - {self.port_vulnerability.name} - {self.port_vulnerability.cve}'
            ),
            self.exploit: f'{self.vulnerability.__str__()} - {self.exploit.title}',
            self.tech_exploit: f'{self.technology.__str__()} - {self.tech_exploit.title}',
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
            (f'port={self.port.id}', 2),                                        # Filter by port
            ('port=0', 0),
            (f'port_number={self.port.port}', 2),                               # Filter by port number
            ('port_number=0', 0),
            (f'host={self.host.id}', 2),                                        # Filter by host
            ('host=0', 0),
            (f'host_address={self.host.address}', 2),                           # Filter by host address
            ('host_address=0.0.0.0', 0),
            (f'host_os_type={self.host.os_type}', 2),                           # Filter by host OS type
            ('host_os_type=Windows', 0),
        ]:
            for endpoint in self.filter_paths:                                  # For each filterable endpoint
                # Filter findings
                content = self.api_test(self.client.get, f'/api/{endpoint}/?{filter}', expected={'count': count})
                if count > 0:                                                   # Expected results
                    findings = [f for f, e in self.data if e == endpoint]       # Get expected findings
                    findings.reverse()                                          # Order findings by creation (so by Id)
                    for index, finding in enumerate(findings):
                        self.assertEqual(finding.id, content['results'][index]['id'])
