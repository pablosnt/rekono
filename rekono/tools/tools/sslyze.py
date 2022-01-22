import json
from typing import List, cast

from findings.enums import Severity
from findings.models import Technology, Vulnerability
from tools.tools.base_tool import BaseTool


class SslyzeTool(BaseTool):
    '''SSLyze tool class.'''

    tls_versions = {
        'ssl': ['2.0', '3.0'],                                                  # SSL versions
        'tls': ['1.0', '1.1', '1.2', '1.3'],                                    # TLS versions
    }

    def checker(self, item: dict, parent: str, child: str, expected: list) -> bool:
        '''Check if item contains a key that contains a subkey whose value is in an expected values list.

        Args:
            item (dict): Item data
            parent (str): Parent key
            child (str): Child key
            expected (list): Expected values list

        Returns:
            bool: Indicate if child key exists in parent key from item, and if whose value matches some expected value
        '''
        return parent in item and child in item[parent] and item[parent][child] in expected

    def check_true(self, item: dict, parent: str, child: str) -> bool:
        '''Check if item contains a key that contains a subkey.

        Args:
            item (dict): Item data
            parent (str): Parent key
            child (str): Child key

        Returns:
            bool: Indicate if child key exists in parent key from item
        '''
        return parent in item and child in item[parent] and item[parent][child]

    def get_rc4s(self, data: dict, field: str) -> List[str]:
        '''Get supported RC4 cipher suites.

        Args:
            data (dict): Original SSLyze data
            field (str): Field where the cipher suite data is

        Returns:
            List[str]: List of supported RC4 cipher suites
        '''
        rc4s = []
        if field in data and 'accepted_cipher_suites' in data[field]:           # If supported cipher suites found
            for cs in data[field]['accepted_cipher_suites']:                    # For each cipher suite
                if 'cipher_suite' in cs and 'name' in cs['cipher_suite'] and '_RC4_' in cs['cipher_suite']['name']:
                    # RC4 cipher suite found
                    rc4s.append(cs['cipher_suite']['name'])                     # Save cipher suite name
        return rc4s

    def analyze_protocols(self, data: dict, generic_tech: Technology) -> None:
        '''Analyze protocol based on his version and supported cipher suites.

        Args:
            data (dict): Original SSLyze data
            generic_tech (Technology): Related generic TLS Technology
        '''
        for protocol, versions in self.tls_versions.items():                    # For each supported protocol
            for version in versions:                                            # For each supported version
                if self.check_true(
                    data,
                    f'{protocol.lower()}_{version.replace(".", "_")}_cipher_suites',
                    'accepted_cipher_suites'
                ):
                    # Create Technology associated to the protocol and related to generic TLS Technology
                    technology = self.create_finding(
                        Technology,
                        name=protocol.upper(),
                        version=version,
                        related_to=generic_tech
                    )
                    if protocol.lower() == 'tls' and version in ['1.2', '1.3']:                     # Secure TLS version
                        # Search supported RC4 cipher suites
                        rc4s = self.get_rc4s(data, f'tls_{version.replace(".", "_")}_cipher_suites')
                        for rc4 in rc4s:                                        # For each RC4 cipher suite
                            self.create_finding(                                # Create Vulnerability
                                Vulnerability,
                                technology=technology,                          # Related to protocol Technology
                                name='Insecure cipher suite supported',
                                description=f'TLS {version} {rc4}',
                                severity=Severity.LOW,
                                # CWE-326: Inadequate Encryption Strength
                                cwe='CWE-326'
                            )
                    else:                                                       # SSL protocol or insecure TLS version
                        self.create_finding(                                    # Create Vulnerability
                            Vulnerability,
                            technology=technology,                              # Related to protocol Technology
                            name=f'Insecure {protocol.upper()} version supported',
                            description=f'{protocol.upper()} {version} is supported',
                            severity=Severity.HIGH,
                            # CWE-326: Inadequate Encryption Strength
                            cwe='CWE-326'
                        )

    def parse_output_file(self) -> None:
        '''Parse tool output file to create finding entities.'''
        with open(self.path_output, 'r') as output_file:
            report = json.load(output_file)                                     # Read output file
        report = report.get('server_scan_results', [])                          # Get scan results
        # Create generic TLS Technology if scan results found
        generic_tech = self.create_finding(Technology, name='Generic TLS') if report else None
        for item in report or []:                                               # For item in report
            r = item['scan_commands_results']
            if self.check_true(r, 'heartbleed', 'is_vulnerable_to_heartbleed'):
                # If it is vulnerable to Heartbleed
                # Create Vulnerability with CVE-2014-0160
                self.create_finding(Vulnerability, technology=generic_tech, name='Heartbleed', cve='CVE-2014-0160')
            if self.check_true(r, 'openssl_css_injection', 'is_vulnerable_to_ccs_injection'):
                # If it is vulnerable to CSS injection
                # Create Vulnerability with CVE-2014-0224
                self.create_finding(Vulnerability, technology=generic_tech, name='OpenSSL CSS Injection', cve='CVE-2014-0224')      # noqa: E501
            if self.checker(r, 'robot', 'robot_result', ['VULNERABLE_STRONG_ORACLE', 'VULNERABLE_WEAK_ORACLE']):
                # If it is vulnerable to ROBOT
                self.create_finding(                                            # Create Vulnerability
                    Vulnerability,
                    technology=generic_tech,                                    # Related to generic TLS Technology
                    name='ROBOT',
                    description='Return Of the Bleichenbacher Oracle Threat',
                    severity=Severity.MEDIUM,
                    cwe='CWE-203',                                              # CWE-203: Observable Discrepancy
                    reference='https://www.robotattack.org/'
                )
            if (
                self.checker(r, 'session_renegotiation', 'supports_secure_renegotiation', [False]) or
                self.check_true(r, 'session_renegotiation', 'is_vulnerable_to_client_renegotiation_dos') or
                self.check_true(r, 'session_renegotiation', 'accepts_client_renegotiation')
            ):
                # If it is vulnerable to Insecure Renegotiation
                self.create_finding(                                            # Create Vulnerability
                    Vulnerability,
                    technology=generic_tech,                                    # Related to generic TLS Technology
                    name='Insecure TLS renegotiation supported',
                    description='Insecure TLS renegotiation supported',
                    severity=Severity.HIGH,
                    # CWE CATEGORY: Permissions, Privileges, and Access Controls
                    cwe='CWE-264'
                )
            if self.check_true(r, 'tls_compression', 'supports_compression'):   # If it is vulnerable to CRIME
                # Create Vulnerability with CVE-2012-4929
                self.create_finding(Vulnerability, technology=generic_tech, name='CRIME', cve='CVE-2012-4929')
            self.analyze_protocols(r, cast(Technology, generic_tech))           # Analyze protocol and version
            if self.check_true(r, 'certificate_info', 'certificate_deployments'):
                for deploy in r['certificate_info']['certificate_deployments']:     # For each certificate information
                    if (
                        'leaf_certificate_subject_matches_hostname' in deploy and
                        not deploy['leaf_certificate_subject_matches_hostname']
                    ):
                        # If certificate subject doesn't match hostname
                        self.create_finding(                                    # Create vulnerability
                            Vulnerability,
                            technology=generic_tech,                            # Related to generic TLS Technology
                            name='Certificate subject error',
                            description="Certificate subject doesn't match hostname",
                            severity=Severity.LOW,
                            # CWE-295: Improper Certificate Validation
                            cwe='CWE-295'
                        )
