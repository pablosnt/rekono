from typing import Any, Dict

from findings.enums import Severity
from findings.models import Technology, Vulnerability
from tools.tools.base_tool import BaseTool


class Sshaudit(BaseTool):
    '''SSH Audit tool class.'''

    # Exit code ignored because SSH Audit fails when find vulnerabilities
    ignore_exit_code = True

    def parse_plain_output(self, output: str) -> None:
        '''Parse tool plain output to create finding entities. This should be implemented by child tool classes.

        Args:
            output (str): Plain tool output
        '''
        algorithms_mapping: Dict[str, Any] = {
            'kex': {'name': 'key exchange', 'algorithms': []},
            'key': {'name': 'host key', 'algorithms': []},
            'enc': {'name': 'encryption', 'algorithms': []},
            'mac': {'name': 'MAC', 'algorithms': []}
        }
        technology = None
        for line in output.split('\n'):                                         # Get output by lines
            data = line.strip()
            if '(gen) software: ' in data:                                      # SSH version
                aux = data.split('(gen) software: ', 1)[1].split(' ', 1)
                technology = self.create_finding(Technology, name=aux[0], version=aux[1].split(' [', 1)[0])
            elif '(cve) ' in data:                                              # CVE found
                aux = data.split('(cve) ', 1)[1].split(' ', 1)
                self.create_finding(
                    Vulnerability,
                    name=aux[1].split(') ', 1)[1].split(' [', 1)[0].capitalize(),
                    cve=aux[0]
                )
            else:
                for topic in algorithms_mapping.keys():                         # For each algorithm type
                    if f'({topic}) ' in data and '[fail]' in data:              # Insecure algorithm found
                        algorithm = data.split(f'({topic}) ', 1)[1].split(' ', 1)[0]
                        if algorithm not in algorithms_mapping[topic]['algorithms']:
                            algorithms_mapping[topic]['algorithms'].append(algorithm)
                        break
        for details in algorithms_mapping.values():                             # For each algorithm type
            if len(details['algorithms']) > 0:                                  # With insecure algorithms
                self.create_finding(
                    Vulnerability,
                    technology=technology,                                      # Related to SSH technology
                    name=f'Insecure {details["name"]} algorithms',
                    description=', '.join(details['algorithms']),
                    severity=Severity.LOW,
                    # CWE-326: Inadequate Encryption Strength
                    cwe='CWE-326'
                )
