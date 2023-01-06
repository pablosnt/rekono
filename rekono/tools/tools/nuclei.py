import json
from typing import Dict, cast

from findings.enums import Severity
from findings.models import Credential, Technology, Vulnerability

from tools.tools.base_tool import BaseTool


class Nuclei(BaseTool):
    '''Nuclei tool class.'''

    def parse_output_file(self) -> None:
        '''Parse tool output file to create finding entities.'''
        with open(self.path_output, 'r', encoding='utf-8') as output_file:
            report = [json.loads(line) for line in output_file if line]         # Read output file
        for item in report:
            name = item.get('info', {}).get('name')
            extracted_results = item.get('extracted-results', [])
            if extracted_results:
                name = f'{name}: {extracted_results[0]}'
            elif item.get('matcher-name'):
                name = f'{name}: {item.get("matcher-name")}'
            description = item.get('info', {}).get('description')
            reference = item.get('info', {}).get('reference', [])
            tags = item.get('info', {}).get('tags', []) or []
            if 'tech' in tags:                                                  # Finding is technology
                self.create_finding(
                    Technology,
                    name=name,
                    description=description.strip() if description else None,
                    reference=reference[0] if reference else None
                )
            elif 'default-login' in tags and item.get('meta'):                  # Finding is credential
                self.create_finding(
                    Credential,
                    username=item.get('meta', {}).get('username'),
                    secret=item.get('meta', {}).get('password'),
                    context=name
                )
            else:                                                               # Finding is vulnerability
                severity = item.get('info', {}).get('severity')
                cve = item.get('info', {}).get('classification', {}).get('cve-id')
                cwe = item.get('info', {}).get('classification', {}).get('cwe-id', [])
                self.create_finding(
                    Vulnerability,
                    name=name.strip(),
                    description=description.strip() if description else None,
                    severity=cast(Dict[str, str], Severity)[severity.upper()] if severity else Severity.INFO,
                    cve=cve.upper() if cve else None,
                    cwe=cwe[0].upper() if cwe else None,
                    reference=reference[0] if reference else None
                )
