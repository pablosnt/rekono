from findings.enums import PathType, Severity
from findings.models import Path, Vulnerability
from testing.tools.base import ToolParserTest


class NiktoParserTest(ToolParserTest):
    '''Test cases for Nikto parser.'''

    tool_name = 'Nikto'

    def test_default(self) -> None:
        '''Test to parse report with some vulnerabilities and endpoints.'''
        expected = [
            {
                'model': Vulnerability,
                'name': 'The anti-clickjacking X-Frame-Options header is not present.',
                'description': '[GET /] The anti-clickjacking X-Frame-Options header is not present.',
                'severity': Severity.MEDIUM,
                'osvdb': 'OSVDB-0'
            },
            {
                'model': Vulnerability,
                'name': (
                    'The X-XSS-Protection header is not defined. This header can hint to the user agent '
                    'to protect against some forms of XSS'
                ),
                'description': (
                    '[GET /] The X-XSS-Protection header is not defined. This header can hint to the user '
                    'agent to protect against some forms of XSS'
                ),
                'severity': Severity.MEDIUM,
                'osvdb': 'OSVDB-0'
            },
            {
                'model': Vulnerability,
                'name': (
                    'The X-Content-Type-Options header is not set. This could allow the user agent to '
                    'render the content of the site in a different fashion to the MIME type'
                ),
                'description': (
                    '[GET /] The X-Content-Type-Options header is not set. This could allow the user '
                    'agent to render the content of the site in a different fashion to the MIME type'
                ),
                'severity': Severity.MEDIUM,
                'osvdb': 'OSVDB-0'
            },
            {
                'model': Vulnerability,
                'name': "Uncommon header 'tcn' found, with contents: list",
                'description': "[GET /index] Uncommon header 'tcn' found, with contents: list",
                'severity': Severity.MEDIUM,
                'osvdb': 'OSVDB-0'
            },
            {'model': Path, 'path': '/index', 'type': PathType.ENDPOINT},
            {
                'model': Vulnerability,
                'name': (
                    'Apache mod_negotiation is enabled with MultiViews, which allows attackers to easily '
                    'brute force file names. See http://www.wisec.it/sectou.php?id=4698ebdc59d15. The following '
                    "alternatives for 'index' were found: index.html"
                ),
                'description': (
                    '[GET /index] Apache mod_negotiation is enabled with MultiViews, which allows attackers '
                    'to easily brute force file names. See http://www.wisec.it/sectou.php?id=4698ebdc59d15. '
                    "The following alternatives for 'index' were found: index.html"
                ),
                'severity': Severity.MEDIUM,
                'osvdb': 'OSVDB-0'
            },
            {
                'model': Vulnerability,
                'name': (
                    'Apache/2.4.7 appears to be outdated (current is at least Apache/2.4.37). '
                    'Apache 2.2.34 is the EOL for the 2.x branch.'
                ),
                'description': (
                    '[HEAD /] Apache/2.4.7 appears to be outdated (current is at least Apache/2.4.37). '
                    'Apache 2.2.34 is the EOL for the 2.x branch.'
                ),
                'severity': Severity.MEDIUM,
                'osvdb': 'OSVDB-0'
            },
            {
                'model': Vulnerability,
                'name': 'Allowed HTTP Methods: GET, HEAD, POST, OPTIONS ',
                'description': '[OPTIONS /] Allowed HTTP Methods: GET, HEAD, POST, OPTIONS ',
                'severity': Severity.MEDIUM,
                'osvdb': 'OSVDB-0'
            },
            {
                'model': Vulnerability,
                'name': '/images/: Directory indexing found.',
                'description': '[GET /images/] /images/: Directory indexing found.',
                'severity': Severity.MEDIUM,
                'osvdb': 'OSVDB-3268'
            },
            {'model': Path, 'path': '/images/', 'type': PathType.ENDPOINT},
            {
                'model': Vulnerability,
                'name': '/icons/README: Apache default file found.',
                'description': '[GET /icons/README] /icons/README: Apache default file found.',
                'severity': Severity.MEDIUM,
                'osvdb': 'OSVDB-3233'
            },
            {'model': Path, 'path': '/icons/README', 'type': PathType.ENDPOINT}
        ]
        super().check_tool_file_parser('default.xml', expected)
