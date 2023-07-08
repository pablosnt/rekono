import json
from typing import Any, Dict, List, Union

from django.db.models import Model
from findings.enums import Severity
from findings.models import Finding, Technology, Vulnerability
from tools.tools.base_tool import BaseTool


class Sslyze(BaseTool):
    '''SSLyze tool class.'''

    # Exit code ignored because SSLyze can "fail" when find vulnerabilities
    ignore_exit_code = True
    tls_versions = [                                                            # SSL and TLS versions
        ('ssl', '2.0'), ('ssl', '3.0'), ('tls', '1.0'), ('tls', '1.1'), ('tls', '1.2'), ('tls', '1.3')
    ]
    generic_tech: Union[Technology, None] = None

    def create_finding(self, finding_type: Model, **fields: Any) -> Finding:
        '''Create finding from fields.

        Args:
            finding_type (Model): Finding model

        Returns:
            Finding: Created finding entity
        '''
        if 'technology' in fields and not fields.get('technology'):
            # Create generic TLS Technology if needed
            self.generic_tech = super().create_finding(Technology, name='Generic TLS')
            fields['technology'] = self.generic_tech
        return super().create_finding(finding_type, **fields)

    def analyze_cipher_suites(self, cipher_suites: List[Dict[str, Any]], technology: Technology) -> None:
        '''Get supported RC4 cipher suites.

        Args:
            cipher_suites (List[Dict[str, Any]]): Accepted cipher suites
            technology (Technology): Technology related to the protocol
        '''
        for cs in cipher_suites:
            if '_RC4_' in cs['cipher_suite']['name']:
                self.create_finding(                                        # Create Vulnerability
                    Vulnerability,
                    technology=technology,                                  # Related to protocol Technology
                    name='Insecure cipher suite supported',
                    description=f'TLS {technology.version} {cs["cipher_suite"]["name"]}',
                    severity=Severity.LOW,
                    # CWE-326: Inadequate Encryption Strength
                    cwe='CWE-326'
                )

    def analyze_protocols(self, data: dict) -> None:
        '''Analyze protocol based on his version and supported cipher suites.

        Args:
            data (dict): Original SSLyze data
        '''
        for protocol, version in self.tls_versions:                             # For each protocol and version
            cipher_suites = data[f'{protocol.lower()}_{version.replace(".", "_")}_cipher_suites']['result']['accepted_cipher_suites']   # noqa: E501
            if cipher_suites:
                # Create Technology associated to the protocol and related to generic TLS Technology
                technology = self.create_finding(
                    Technology,
                    name=protocol.upper(),
                    version=version,
                    related_to=self.generic_tech
                )
                if protocol.lower() != 'tls' or version not in ['1.2', '1.3']:  # SSL protocol or insecure TLS version
                    self.create_finding(                                        # Create Vulnerability
                        Vulnerability,
                        technology=technology,                                  # Related to protocol Technology
                        name=f'Insecure {protocol.upper()} version supported',
                        description=f'{protocol.upper()} {version} is supported',
                        severity=Severity.MEDIUM if protocol.upper() == 'TLS' else Severity.HIGH,
                        # CWE-326: Inadequate Encryption Strength
                        cwe='CWE-326'
                    )
                if protocol.lower() == 'tls':
                    self.analyze_cipher_suites(cipher_suites, technology)       # Search supported weak cipher suites

    def parse_output_file(self) -> None:
        '''Parse tool output file to create finding entities.'''
        with open(self.path_output, 'r', encoding='utf-8') as output_file:
            report = json.load(output_file)                                     # Read output file
        report = report.get('server_scan_results', [])                          # Get scan results
        for item in report or []:                                               # For item in report
            r = item['scan_commands_results'] if 'scan_commands_results' in item else item['scan_result']
            if not r:
                continue
            if r['heartbleed']['result']['is_vulnerable_to_heartbleed']:        # If it is vulnerable to Heartbleed
                # Create Vulnerability with CVE-2014-0160
                self.create_finding(Vulnerability, technology=self.generic_tech, name='Heartbleed', cve='CVE-2014-0160')
            if r['openssl_ccs_injection']['result']['is_vulnerable_to_ccs_injection']:
                # If it is vulnerable to CCS injection
                # Create Vulnerability with CVE-2014-0224
                self.create_finding(
                    Vulnerability,
                    technology=self.generic_tech,
                    name='OpenSSL CSS Injection',
                    cve='CVE-2014-0224'
                )
            if r['robot']['result']['robot_result'] in ['VULNERABLE_STRONG_ORACLE', 'VULNERABLE_WEAK_ORACLE']:
                # If it is vulnerable to ROBOT
                self.create_finding(                                            # Create Vulnerability
                    Vulnerability,
                    technology=self.generic_tech,                               # Related to generic TLS Technology
                    name='ROBOT',
                    description='Return Of the Bleichenbacher Oracle Threat',
                    severity=Severity.MEDIUM,
                    cwe='CWE-203',                                              # CWE-203: Observable Discrepancy
                    reference='https://www.robotattack.org/'
                )
            if (
                not r['session_renegotiation']['result']['supports_secure_renegotiation'] or
                r['session_renegotiation']['result']['is_vulnerable_to_client_renegotiation_dos']
            ):
                # If it is vulnerable to Insecure Renegotiation
                self.create_finding(                                            # Create Vulnerability
                    Vulnerability,
                    technology=self.generic_tech,                               # Related to generic TLS Technology
                    name='Insecure TLS renegotiation supported',
                    description='Insecure TLS renegotiation supported',
                    severity=Severity.MEDIUM,
                    # CWE CATEGORY: Permissions, Privileges, and Access Controls
                    cwe='CWE-264'
                )
            if r['tls_compression']['result']['supports_compression']:          # If it is vulnerable to CRIME
                # Create Vulnerability with CVE-2012-4929
                self.create_finding(Vulnerability, technology=self.generic_tech, name='CRIME', cve='CVE-2012-4929')
            self.analyze_protocols(r)                                           # Analyze protocol and version
            # For each certificate information
            for deploy in r['certificate_info']['result']['certificate_deployments'] or []:
                if not deploy['leaf_certificate_subject_matches_hostname']:
                    # If certificate subject doesn't match hostname
                    self.create_finding(                                        # Create vulnerability
                        Vulnerability,
                        technology=self.generic_tech,                           # Related to generic TLS Technology
                        name='Certificate subject error',
                        description="Certificate subject doesn't match hostname",
                        severity=Severity.INFO,
                        # CWE-295: Improper Certificate Validation
                        cwe='CWE-295'
                    )
