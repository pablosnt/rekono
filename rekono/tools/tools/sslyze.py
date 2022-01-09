import json

from findings.enums import Severity
from findings.models import Technology, Vulnerability
from tools.tools.base_tool import BaseTool


class SslyzeTool(BaseTool):

    tls_versions = {
        'ssl': ['2.0', '3.0'],
        'tls': ['1.0', '1.1', '1.2', '1.3'],
    }

    def checker(self, item: dict, parent: str, child: str, expected: list) -> bool:
        return (
            parent in item
            and child in item[parent]
            and item[parent][child] in expected
        )

    def check_true(self, item: dict, parent: str, child: str) -> bool:
        return (
            parent in item
            and child in item[parent]
            and item[parent][child]
        )

    def get_rc4s(self, item: dict, field: str) -> list:
        rc4s = []
        if field in item and 'accepted_cipher_suites' in item[field]:
            for cs in item[field]['accepted_cipher_suites']:
                if (
                    'cipher_suite' in cs
                    and 'name' in cs['cipher_suite']
                    and '_RC4_' in cs['cipher_suite']['name']
                ):
                    rc4s.append(cs['cipher_suite']['name'])
        return rc4s

    def analyze_protocol(
        self,
        data: dict,
        protocol: str,
        version: str,
        generic_tech: Technology
    ) -> None:
        technology = self.create_finding(
            Technology,
            name=protocol.upper(),
            version=version,
            related_to=generic_tech
        )
        if protocol.lower() == 'tls' and version in ['1.2', '1.3']:
            rc4s = self.get_rc4s(data, 'tls_1_2_cipher_suites')
            for rc4 in rc4s:
                self.create_finding(
                    Vulnerability,
                    technology=technology,
                    name='Insecure cipher suite supported',
                    description=f'TLS {version} {rc4}',
                    severity=Severity.LOW,
                    cwe='CWE-326'
                )
        else:
            self.create_finding(
                Vulnerability,
                technology=technology,
                name=f'Insecure {protocol.upper()} version supported',
                description=f'{protocol.upper()} {version} is supported',
                severity=Severity.MEDIUM,
                cwe='CWE-326'
            )

    def parse_output(self, output: str) -> None:
        with open(self.path_output, 'r') as output_file:
            report = json.load(output_file)
        if 'server_scan_results' not in report:
            return []
        report = report['server_scan_results']
        generic_tech = self.create_finding(Technology, name='Generic TLS')
        for item in report:
            r = item['scan_commands_results']
            if self.check_true(r, 'heartbleed', 'is_vulnerable_to_heartbleed'):
                self.create_finding(
                    Vulnerability,
                    technology=generic_tech,
                    name='Heartbleed',
                    cve='CVE-2014-0160'
                )
            if self.check_true(r, 'openssl_css_injection', 'is_vulnerable_to_ccs_injection'):
                self.create_finding(
                    Vulnerability,
                    technology=generic_tech,
                    name='OpenSSL CSS Injection',
                    cve='CVE-2014-0224'
                )
            if self.checker(
                r,
                'robot',
                'robot_result',
                ['VULNERABLE_STRONG_ORACLE', 'VULNERABLE_WEAK_ORACLE']
            ):
                self.create_finding(
                    Vulnerability,
                    technology=generic_tech,
                    name='ROBOT',
                    description='Return Of the Bleichenbacher Oracle Threat',
                    severity=Severity.MEDIUM,
                    cwe='CWE-203',
                    reference='https://www.robotattack.org/'
                )
            if (
                self.checker(r, 'session_renegotiation', 'supports_secure_renegotiation', [False])
                or self.check_true(
                    r,
                    'session_renegotiation',
                    'is_vulnerable_to_client_renegotiation_dos'
                )
                or self.check_true(r, 'session_renegotiation', 'accepts_client_renegotiation')
            ):
                self.create_finding(
                    Vulnerability,
                    technology=generic_tech,
                    name='Insecure TLS renegotiation supported',
                    description='Insecure TLS renegotiation supported',
                    severity=Severity.HIGH,
                    cwe='CWE-264'
                )
            if self.check_true(r, 'tls_compression', 'supports_compression'):
                self.create_finding(
                    Vulnerability,
                    technology=generic_tech,
                    name='CRIME',
                    cve='CVE-2012-4929'
                )
            for protocol, versions in self.tls_versions.items():
                for version in versions:
                    if self.check_true(
                        r,
                        f'{protocol.lower()}_{version.replace(".", "_")}_cipher_suites',
                        'accepted_cipher_suites'
                    ):
                        self.analyze_protocol(r, protocol, version, generic_tech)
            if self.check_true(r, 'certificate_info', 'certificate_deployments'):
                for deploy in r['certificate_info']['certificate_deployments']:
                    if (
                        'leaf_certificate_subject_matches_hostname' in deploy
                        and not deploy['leaf_certificate_subject_matches_hostname']
                    ):
                        self.create_finding(
                            Vulnerability,
                            technology=generic_tech,
                            name='Certificate subject error',
                            description="Certificate subject doesn't match hostname",
                            severity=Severity.LOW,
                            cwe='CWE-295'
                        )
