from findings.models import Vulnerability
from tools.tools.base_tool import BaseTool
from typing import List
from input_types.models import BaseInput
from findings.models import Finding
from rekono.settings import TOOLS
import os


class Log4jscannerTool(BaseTool):
    '''Log4j Scanner tool class.'''

    def tool_execution(self, arguments: List[str], targets: List[BaseInput], previous_findings: List[Finding], directory: str = None) -> str:
        arguments.insert(0, os.path.join(TOOLS['log4j-scanner']['directory'], 'log4j-scan.py'))
        return super().tool_execution(arguments, targets, previous_findings, TOOLS['log4j-scanner']['directory'])

    def parse_plain_output(self, output: str) -> None:
        if '[!!!] Targets Affected' in output:
            self.create_finding(Vulnerability, name='Log4Shell', cve=self.configuration.name)
