from findings.models import Vulnerability
from testing.tools.base import ToolParserTest
from tools.exceptions import ToolExecutionException


class Log4jScannerParserTest(ToolParserTest):
    '''Test cases for Log4j Scanner parser.'''

    tool_name = 'Log4j Scanner'

    def test_check_installation(self) -> None:
        '''Test check installatino feature for Log4j Scanner.'''
        installed = True
        try:
            self.tool.check_installation()
        except ToolExecutionException:
            installed = False
        self.assertFalse(installed)

    def test_cve_2021_44228(self) -> None:
        '''Test to parse report with CVE-2021-44228 vulnerability.'''
        expected = [
            {'model': Vulnerability, 'name': 'Log4Shell', 'cve': 'CVE-2021-44228'}
        ]
        self.check_tool_output_parser('cve_2021_44228.txt', expected)

    def test_cve_2021_45046(self) -> None:
        '''Test to parse report with CVE-2021-45046 vulnerability.'''
        expected = [
            {'model': Vulnerability, 'name': 'Log4Shell', 'cve': 'CVE-2021-45046'}
        ]
        self.check_tool_output_parser('cve_2021_45046.txt', expected)

    def test_no_vulnerable(self) -> None:
        '''Test to parse report without vulnerability.'''
        self.check_tool_output_parser('not_vulnerable.txt', [])
