from findings.enums import Severity
from findings.models import Credential, Technology, Vulnerability
from testing.tools.base import ToolParserTest


class NucleiParserTest(ToolParserTest):
    '''Test cases for Nuclei parser.'''

    tool_name = 'Nuclei'

    def test_tech_and_vulns(self) -> None:
        '''Test to parse report with technologies and vulnerabilities.'''
        expected = [
            {'model': Technology, 'name': 'PHP Detect', 'version': None, 'description': None, 'reference': None},
            {
                'model': Technology,
                'name': 'Apache Detection: Apache/2.4.25 (Debian)',
                'version': None,
                'description': 'Some Apache servers have the version on the response header. The OpenSSL version can be also obtained',     # noqa: E501
                'reference': None
            },
            {
                'model': Technology,
                'name': 'Wappalyzer Technology Detection: php',
                'version': None,
                'description': None,
                'reference': None
            },
            {
                'model': Vulnerability,
                'name': 'robots.txt endpoint prober',
                'description': None,
                'severity': Severity.INFO,
                'cve': None,
                'cwe': None,
                'reference': None
            },
            {
                'model': Vulnerability,
                'name': 'HTTP Missing Security Headers: access-control-allow-headers',
                'description': 'This template searches for missing HTTP security headers. The impact of these missing headers can vary.',     # noqa: E501
                'severity': Severity.INFO,
                'cve': None,
                'cwe': None,
                'reference': None
            },
            {
                'model': Vulnerability,
                'name': 'Redis Server - Unauthenticated Access',
                'description': 'Redis server without any required authentication was discovered.',
                'severity': Severity.HIGH,
                'cve': None,
                'cwe': None,
                'reference': 'https://redis.io/topics/security'
            },
            {
                'model': Vulnerability,
                'name': 'Exposed Gitignore',
                'description': None,
                'severity': Severity.INFO,
                'cve': None,
                'cwe': None,
                'reference': 'https://twitter.com/pratiky9967/status/1230001391701086208'
            },
            {
                'model': Technology,
                'name': 'WAF Detection: apachegeneric',
                'version': None,
                'description': 'A web application firewall was detected.',
                'reference': 'https://github.com/ekultek/whatwaf'
            },
            {
                'model': Vulnerability,
                'name': 'phpinfo Disclosure: 7.0.30',
                'description': 'A "PHP Info" page was found. The output of the phpinfo() command can reveal detailed PHP environment information.',       # noqa: E501
                'severity': Severity.LOW,
                'cve': None,
                'cwe': None,
                'reference': None
            },
            {
                'model': Vulnerability,
                'name': 'README.md file disclosure',
                'description': 'Internal documentation file often used in projects which can contain sensitive information.',       # noqa: E501
                'severity': Severity.INFO,
                'cve': None,
                'cwe': None,
                'reference': None
            },
            {
                'model': Credential,
                'username': 'admin',
                'secret': 'password',
                'context': 'DVWA Default Login'
            }
        ]
        super().check_tool_file_parser('tech_and_vulns.json', expected)
