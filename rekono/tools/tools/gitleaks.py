import json
import os
import subprocess
import uuid
from typing import List

from findings.enums import Severity
from findings.models import Credential, Port, Vulnerability
from input_types.enums import InputKeyword
from rekono.settings import REPORTS_DIR, TOOLS

from tools.exceptions import ToolExecutionException
from tools.tools.base_tool import BaseTool


class Gitleaks(BaseTool):
    '''GitLeaks tool class.'''

    # Exit code ignored because GitLeaks fails when find secrets
    ignore_exit_code = True
    gitdumper_directory = os.path.join(TOOLS['gittools']['directory'], 'Dumper')    # GitDumper directory
    script = os.path.join(gitdumper_directory, 'gitdumper.sh')                  # Indicate the script path to execute

    def parse_output_file(self) -> None:
        '''Parse tool output file to create finding entities. This should be implemented by child tool classes.'''
        with open(self.path_output, 'r', encoding='utf-8') as output_file:
            data = json.load(output_file)                                       # Read output file
        emails = []
        for finding in data:                                                    # For each finding
            self.create_finding(                                                # Save secret match
                Credential,
                secret=finding.get('Match'),
                context=f'/.git/ : {finding.get("File")} -> Line {finding.get("StartLine")}'
            )
            email = finding.get('Email')
            if email and email not in emails:                                   # New commit author email
                emails.append(email)
                self.create_finding(                                            # Save commit author email
                    Credential,
                    email=email,
                    context=f'/.git/ : Email of the commit author {finding.get("Author")}'
                )

    def tool_execution(self, arguments: List[str]) -> str:
        '''Execute the tool.

        Args:
            arguments (List[str]): Arguments to include in the tool command

        Raises:
            ToolExecutionException: Raised if tool execution finishes with an exit code distinct than zero

        Returns:
            str: Plain output of the tool execution
        '''
        _, service = list(self.findings_relations.items())[0]                   # Get http service to scan
        data = service.parse()
        if InputKeyword.URL.name.lower() in data and data[InputKeyword.URL.name.lower()]:
            if data[InputKeyword.URL.name.lower()][-1] != '/':
                data[InputKeyword.URL.name.lower()] += '/.git/'                 # Add .git path with last slash
            else:
                data[InputKeyword.URL.name.lower()] += '.git/'                  # Add .git path with last slash
            self.run_directory = os.path.join(REPORTS_DIR, str(uuid.uuid4()))   # Path where Git repo will be dumped
            process = subprocess.run(                                           # Dump Git repository
                ['bash', self.script, data[InputKeyword.URL.name.lower()], self.run_directory],
                capture_output=True,
                cwd=self.gitdumper_directory
            )
            # Checkout files
            subprocess.run(['git', 'checkout', '--', '.'], capture_output=True, cwd=self.run_directory)
            git_dumped = True
            for _, dirs, files in os.walk(self.run_directory):
                # Check if Git repository has been dumped or not
                git_dumped = len([d for d in dirs if d != '.git']) > 0 or len(files) > 0
                break
            if git_dumped:                                                      # Git repository has been dumped
                self.create_finding(                                            # Create related vulnerability
                    Vulnerability,
                    port=service if isinstance(service, Port) else None,
                    name='Git source code exposure',
                    description=(
                        'Source code is exposed in the endpoint /.git/ and '
                        "it's possible to dump it as a git repository"
                    ),
                    severity=Severity.HIGH,
                    # CWE-527: Exposure of Version-Control Repository to an Unauthorized Control Sphere
                    cwe='CWE-527',
                    reference='https://iosentrix.com/blog/git-source-code-disclosure-vulnerability/'
                )
                self.execution.extra_data_path = self.run_directory             # Save extra data related to GitLeaks
                self.execution.save(update_fields=['extra_data_path'])
                return super().tool_execution(arguments)                        # Run GitLeaks
            if process.returncode > 0:                                          # Error during gitdumper execution
                raise ToolExecutionException(process.stderr.decode('utf-8'))
            return process.stdout.decode('utf-8')                               # Git repository hasn't been dumped
        raise ToolExecutionException('Path argument is required')
