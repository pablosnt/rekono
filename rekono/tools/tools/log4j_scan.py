import os

from findings.models import Vulnerability
from rekono.settings import TOOLS

from tools.tools.base_tool import BaseTool


class Log4jscan(BaseTool):
    '''Log4j Scan tool class.'''

    run_directory = TOOLS['log4j-scan']['directory']
    # Indicate the script path to execute
    script = os.path.join(run_directory, 'log4j-scan.py')

    def parse_plain_output(self, output: str) -> None:
        '''Parse tool plain output to create finding entities. This should be implemented by child tool classes.

        Args:
            output (str): Plain tool output
        '''
        if '[!!!] Targets Affected' in output:
            self.create_finding(Vulnerability, name='Log4Shell', cve='CVE-2021-44228')
