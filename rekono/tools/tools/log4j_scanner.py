import os
from typing import List

from findings.models import Finding, Vulnerability
from input_types.models import BaseInput
from tools.exceptions import ToolExecutionException
from tools.tools.base_tool import BaseTool

from rekono.settings import TOOLS


class Log4jscannerTool(BaseTool):
    '''Log4j Scanner tool class.'''

    run_directory = os.path.join(TOOLS['log4j-scanner']['directory'], 'log4-scanner')

    def check_installation(self) -> None:
        '''Check if tool is installed in the system.

        Raises:
            ToolExecutionException: Raised if tool isn't installed
        '''
        super().check_installation()
        if (
            not os.path.isdir(self.run_directory) or                            # Check log4j-scanner directory
            not os.path.isfile(os.path.join(self.run_directory, 'log4j-scan.py'))   # Check log4j-scanner script
        ):
            raise ToolExecutionException(f'Tool {self.tool.name} is not installed in the system')

    def tool_execution(self, arguments: List[str], targets: List[BaseInput], previous_findings: List[Finding]) -> str:
        '''Execute the tool.

        Args:
            arguments (List[str]): Arguments to include in the tool command
            targets (List[BaseInput]): List of targets and resources
            previous_findings (List[Finding]): List of previous findings

        Raises:
            ToolExecutionException: Raised if tool execution finishes with an exit code distinct than zero

        Returns:
            str: Plain output of the tool execution
        '''
        arguments.insert(0, os.path.join(self.run_directory, 'log4j-scan.py'))  # Add log4j-scanner script
        return super().tool_execution(arguments, targets, previous_findings)    # Execute script

    def parse_plain_output(self, output: str) -> None:
        '''Parse tool plain output to create finding entities. This should be implemented by child tool classes.

        Args:
            output (str): Plain tool output
        '''
        if '[!!!] Targets Affected' in output:
            cve = 'CVE-2021-45046' if 'CVE-2021-45046' in output else 'CVE-2021-44228'
            self.create_finding(Vulnerability, name='Log4Shell', cve=cve)
