import os
import re

from findings.models import Enumeration, Host, Technology, Vulnerability
from libnmap.parser import NmapParser
from tools.arguments.constants import CVE_REGEX
from tools.tools.base_tool import BaseTool


class NmapTool(BaseTool):

    file_output_enabled = True

    def parse_vulners_nse(self, output: str, technology: Technology) -> list:
        cves = re.findall(CVE_REGEX, output)
        findings = []
        for cve in cves:
            vulnerability = Vulnerability.objects.create(
                technology=technology,
                name=cve,
                cve=cve
            )
            findings.append(vulnerability)
        return findings

    def parse_ftp_anon_nse(self, output: str, technology: Technology) -> list:
        vulnerability = Vulnerability.objects.create(
            technology=technology,
            name='FTP anonymous',
            description='FTP anonymous login is allowed',
            severity=Vulnerability.Severity.CRITICAL,
            reference='https://book.hacktricks.xyz/pentesting/pentesting-ftp#anonymous-login'
        )
        return [vulnerability]

    def parse_ftp_proftpd_bd_nse(self, output: str, technology: Technology) -> list:
        vulnerability = Vulnerability.objects.create(
            technology=technology,
            name='FTP Backdoor',
            description='FTP ProFTPD 1.3.3c Backdoor',
            severity=Vulnerability.Severity.CRITICAL
        )
        return [vulnerability]

    def parse_ftp_vsftpd_bd_nse(self, output: str, technology: Technology) -> list:
        vulnerability = Vulnerability.objects.create(
            technology=technology,
            name='CVE-2011-2523',
            cve='CVE-2011-2523'
        )
        return [vulnerability]

    def parse_ftp_libopie_nse(self, output: str, technology: Technology) -> list:
        vulnerability = Vulnerability.objects.create(
            technology=technology,
            name='CVE-2010-1938',
            cve='CVE-2010-1938'
        )
        return [vulnerability]

    def parse_ftp_cve_2010_4221(self, output: str, technology: Technology) -> list:
        vulnerability = Vulnerability.objects.create(
            technology=technology,
            name='CVE-2010-4221',
            cve='CVE-2010-4221'
        )
        return [vulnerability]

    def parse_output(self, output: str) -> list:
        findings = []
        if os.path.isfile(self.path_output):
            report = NmapParser.parse_fromfile(self.path_output)
            for h in report.hosts:
                if not h.is_up():
                    continue
                os_detections = h.os_match_probabilities()
                os_text = None
                os_type = None
                if os_detections:
                    selected_os = None
                    accuracy = 0
                    for o in os_detections:
                        if o.accuracy > accuracy:
                            selected_os = o
                            os_text = o.name
                    accuracy = 0
                    for c in selected_os.osclasses:
                        if c.accuracy > accuracy:
                            try:
                                os_type = Host.OSType[c.osfamily.upper()]
                            except KeyError:
                                os_type = Host.OSType.OTHER
                host = Host.objects.create(
                    address=h.address,
                    os=os_text,
                    os_type=os_type
                )
                findings.append(host)
                for s in h.services:
                    enumeration = Enumeration.objects.create(
                        host=host,
                        port=s.port,
                        port_status=Enumeration.PortStatus[s.state.upper()],
                        protocol=Enumeration.Protocol[s.protocol.upper()],
                        service=s.service
                    )
                    findings.append(enumeration)
                    if 'product' in s.service_dict and 'version' in s.service_dict:
                        technology = Technology.objects.create(
                            enumeration=enumeration,
                            name=s.service_dict.get('product'),
                            version=s.service_dict.get('version')
                        )
                        findings.append(technology)
                        if s.scripts_results:
                            parsers = {
                                'vulners': self.parse_vulners_nse,
                                'ftp-anon': self.parse_ftp_anon_nse,
                                'ftp-proftpd-backdoor': self.parse_ftp_proftpd_bd_nse,
                                'ftp-vsftpd-backdoor': self.parse_ftp_vsftpd_bd_nse,
                                'ftp-libopie': self.parse_ftp_libopie_nse,
                                'ftp-vuln-cve2010-4221': self.parse_ftp_cve_2010_4221,
                            }
                            for script in s.scripts_results:
                                if script.get('id', '') not in parsers:
                                    continue
                                new = parsers[script.get('id', '')](script.get('output', ''), technology)   # noqa: E501
                                findings.extend(new)
        return findings
