from findings.models import Vulnerability
from testing.tools.base import ToolParserTest

from tools.exceptions import ToolExecutionException


class Spring4ShellScanParserTest(ToolParserTest):
    '''Test cases for Spring4Shell Scan parser.'''

    tool_name = 'Spring4Shell Scan'

    def test_check_installation(self) -> None:
        '''Test check installation feature for Spring4Shell Scan.'''
        installed = True
        try:
            self.tool.check_installation()
        except ToolExecutionException:
            installed = False
        self.assertFalse(installed)

    def test_cve_2022_22963(self) -> None:
        '''Test to parse report with CVE-2022-22963 vulnerability.'''
        expected = [
            {'model': Vulnerability, 'name': 'Spring Cloud RCE', 'cve': 'CVE-2022-22963'}
        ]
        self.check_tool_output_parser('cve_2022_22963.txt', expected)

    def test_cve_2022_22965(self) -> None:
        '''Test to parse report with CVE-2022-22965 vulnerability.'''
        expected = [
            {'model': Vulnerability, 'name': 'Spring4Shell RCE', 'cve': 'CVE-2022-22965'}
        ]
        self.check_tool_output_parser('cve_2022_22965.txt', expected)

    def test_no_vulnerable(self) -> None:
        '''Test to parse report without vulnerability.'''
        self.check_tool_output_parser('not_vulnerable.txt', [])
