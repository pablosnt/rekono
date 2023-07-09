from typing import List, Union

import defusedxml.ElementTree as parser
from findings.enums import Severity
from findings.models import Technology, Vulnerability
from tools.tools.base_tool import BaseTool


class Sslscan(BaseTool):
    '''Sslscan tool class.'''

    def get_technology(self, technologies: List[Technology], sslversion: str) -> Union[Technology, None]:
        '''Select Technology from technology list based on protocol and version.

        Args:
            technologies (List[Technology]): Technology list
            sslversion (str): Protocol and version in format [protocol]v[version]

        Returns:
            Union[Technology, None]: Selected Technology from list
        '''
        select = [tech for tech in technologies if f'{tech.name}v{tech.version}' == sslversion]
        return select[0] if select else None

    def parse_output_file(self) -> None:
        '''Parse tool output file to create finding entities.'''
        technologies: List[Technology] = []
        try:
            root = parser.parse(self.path_output).getroot()                     # Report root
        except parser.ParseError:
            return
        tests = root.findall('ssltest')                                         # Get test
        for test in tests:                                                      # For each test
            for item in test:                                                   # For each item
                if item.tag == 'protocol' and item.attrib['enabled'] == '1':    # If item is an enabled protocol
                    technology = self.create_finding(                           # Create Technology
                        Technology,
                        name=item.attrib['type'].upper(),
                        version=item.attrib['version']
                    )
                    technologies.append(technology)                             # Save Technology in list
                    if (
                        # Insecure TLS version
                        (item.attrib['type'] == 'tls' and item.attrib['version'] not in ['1.2', '1.3']) or
                        item.attrib['type'] == 'ssl'                        # Insecure SSL protocol
                    ):
                        desc = '{protocol} {version} is supported'.format(      # Vulnerability description
                            protocol=item.attrib["type"].upper(),
                            version=item.attrib["version"]
                        )
                        self.create_finding(                                    # Create Vulnerability
                            Vulnerability,
                            technology=technology,                              # Related to current protocol Technology
                            name=f'Insecure {item.attrib["type"].upper()} version supported',
                            description=desc,
                            severity=Severity.MEDIUM if item.attrib['type'] == 'tls' else Severity.HIGH,
                            # CWE-326: Inadequate Encryption Strength
                            cwe='CWE-326'
                        )
                elif item.tag == 'renegotiation' and item.attrib['supported'] == '1' and item.attrib['secure'] != '1':
                    # If it is vulnerable to Insecure Renegotiation
                    self.create_finding(
                        Vulnerability,
                        name='Insecure TLS renegotiation supported',
                        description='Insecure TLS renegotiation supported',
                        severity=Severity.MEDIUM,
                        # CWE CATEGORY: Permissions, Privileges, and Access Controls
                        cwe='CWE-264'
                    )
                elif item.tag == 'heartbleed' and item.attrib['vulnerable'] == '1':
                    # If it is vulnerable to Heartbleed
                    # Create Vulnerability with CVE-2014-0160
                    self.create_finding(
                        Vulnerability,
                        # Get technology based on protocol and version (sslversion field)
                        technology=self.get_technology(technologies, item.attrib['sslversion']),
                        name=f'Heartbleed in {item.attrib["sslversion"]}',
                        cve='CVE-2014-0160',
                    )
                elif item.tag == 'cipher' and item.attrib['strength'] not in ['acceptable', 'strong']:
                    # Insecure cipher suite supported
                    # Vulnerability description
                    desc = '{version} {cipher} status={status} strength={strength}'.format(
                        version=item.attrib["sslversion"],
                        cipher=item.attrib["cipher"],
                        status=item.attrib["status"],
                        strength=item.attrib["strength"]
                    )
                    self.create_finding(                                        # Create Vulnerability
                        Vulnerability,
                        # Get technology based on protocol and version (sslversion field)
                        technology=self.get_technology(technologies, item.attrib['sslversion']),
                        name='Insecure cipher suite supported',
                        description=desc,
                        severity=Severity.LOW,
                        # CWE-326: Inadequate Encryption Strength
                        cwe='CWE-326'
                    )
