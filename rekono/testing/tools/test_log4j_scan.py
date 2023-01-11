from findings.models import Vulnerability
from testing.tools.base import ToolParserTest


class Log4jScannerParserTest(ToolParserTest):
    '''Test cases for Log4j Scan parser.'''

    tool_name = 'Log4j Scan'

    def test_cve_2021_44228(self) -> None:
        '''Test to parse report with CVE-2021-44228 vulnerability.'''
        expected = [
            {'model': Vulnerability, 'name': 'Log4Shell', 'cve': 'CVE-2021-44228'}
        ]
        self.check_tool_output_parser('cve_2021_44228.txt', expected)

    def test_no_vulnerable(self) -> None:
        '''Test to parse report without vulnerability.'''
        self.check_tool_output_parser('not_vulnerable.txt', [])
