import os

from findings.models import Vulnerability
from rekono.settings import TOOLS

from tools.tools.base_tool import BaseTool


class Spring4shellscan(BaseTool):
    '''Spring4Shell Scan tool class.'''

    # Indicate the script path to execute
    script = os.path.join(TOOLS['spring4shell-scan']['directory'], 'spring4shell-scan.py')

    def parse_plain_output(self, output: str) -> None:
        '''Parse tool plain output to create finding entities. This should be implemented by child tool classes.

        Args:
            output (str): Plain tool output
        '''
        for search, name, cve in [
            ('[!!!] Target Affected (CVE-2022-22963)', 'Spring Cloud RCE', 'CVE-2022-22963'),
            ('[!!!] Target Affected (CVE-2022-22965)', 'Spring4Shell RCE', 'CVE-2022-22965'),
        ]:
            if search in output:
                self.create_finding(Vulnerability, name=name, cve=cve)
