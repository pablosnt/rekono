import os

from findings.models import Vulnerability
from rekono.settings import TOOLS

from tools.tools.base_tool import BaseTool


class Log4jscannerTool(BaseTool):
    '''Log4j Scanner tool class.'''

    script = os.path.join(TOOLS['log4j-scanner']['directory'], 'log4-scanner', 'log4j-scan.py')

    def parse_plain_output(self, output: str) -> None:
        '''Parse tool plain output to create finding entities. This should be implemented by child tool classes.

        Args:
            output (str): Plain tool output
        '''
        if '[!!!] Targets Affected' in output:
            cve = 'CVE-2021-45046' if 'CVE-2021-45046' in output else 'CVE-2021-44228'
            self.create_finding(Vulnerability, name='Log4Shell', cve=cve)
