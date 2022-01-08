import re
from typing import Any

from findings.enums import OSType, PortStatus, Protocol, Severity
from findings.models import Enumeration, Host, Technology, Vulnerability
from libnmap.parser import NmapParser
from tools.tools.base_tool import BaseTool

CVE_REGEX = 'CVE-[0-9]{4}-[0-9]{1,7}'


class NmapTool(BaseTool):

    def parse_vulners_nse(self, output: str, technology: Technology) -> None:
        cves = re.findall(CVE_REGEX, output)
        for cve in cves:
            self.create_finding(
                Vulnerability,
                technology=technology,
                name=cve,
                cve=cve
            )

    def parse_ftp_anon_nse(self, output: str, technology: Technology) -> None:
        self.create_finding(
            Vulnerability,
            technology=technology,
            name='FTP anonymous',
            description='FTP anonymous login is allowed',
            severity=Severity.CRITICAL,
            cwe='CWE-287',
            reference='https://book.hacktricks.xyz/pentesting/pentesting-ftp#anonymous-login'
        )

    def parse_ftp_proftpd_bd_nse(self, output: str, technology: Technology) -> None:
        self.create_finding(
            Vulnerability,
            technology=technology,
            name='FTP Backdoor',
            description='FTP ProFTPD 1.3.3c Backdoor',
            severity=Severity.CRITICAL,
            cwe='CWE-78',
            osvdb='OSVDB-69562'
        )

    def parse_ftp_vsftpd_bd_nse(self, output: str, technology: Technology) -> None:
        self.create_finding(
            Vulnerability,
            technology=technology,
            name='CVE-2011-2523',
            cve='CVE-2011-2523'
        )

    def parse_ftp_libopie_nse(self, output: str, technology: Technology) -> None:
        self.create_finding(
            Vulnerability,
            technology=technology,
            name='CVE-2010-1938',
            cve='CVE-2010-1938'
        )

    def parse_ftp_cve_2010_4221(self, output: str, technology: Technology) -> None:
        vulnerability = self.create_finding(
            Vulnerability,
            technology=technology,
            name='CVE-2010-4221',
            cve='CVE-2010-4221'
        )
        return [vulnerability]

    def parse_nse_scripts(self, scripts_results: Any, technology: Technology) -> None:
        parsers = {
            'vulners': self.parse_vulners_nse,
            'ftp-anon': self.parse_ftp_anon_nse,
            'ftp-proftpd-backdoor': self.parse_ftp_proftpd_bd_nse,
            'ftp-vsftpd-backdoor': self.parse_ftp_vsftpd_bd_nse,
            'ftp-libopie': self.parse_ftp_libopie_nse,
            'ftp-vuln-cve2010-4221': self.parse_ftp_cve_2010_4221,
        }
        for script in scripts_results:
            if script.get('id') not in parsers:
                continue
            parsers[script.get('id')](script.get('output'), technology)

    def select_os_detection(self, os_detection: Any) -> None:
        os_text = None
        os_type = OSType.OTHER
        if os_detection:
            selected_os = None
            accuracy = 0
            for o in os_detection:
                if o.accuracy > accuracy:
                    selected_os = o
                    os_text = o.name
            accuracy = 0
            for c in selected_os.osclasses:
                if c.accuracy > accuracy:
                    try:
                        os_type = OSType[c.osfamily.upper()]
                    except KeyError:
                        os_type = OSType.OTHER
        return os_text, os_type

    def parse_output(self, output: str) -> list:
        report = NmapParser.parse_fromfile(self.path_output)
        for h in report.hosts:
            if not h.is_up():
                continue
            os_text, os_type = self.select_os_detection(h.os_match_probabilities())
            host = self.create_finding(
                Host,
                address=h.address,
                os=os_text,
                os_type=os_type
            )
            for s in h.services:
                enumeration = self.create_finding(
                    Enumeration,
                    host=host,
                    port=s.port,
                    port_status=PortStatus[s.state.upper()],
                    protocol=Protocol[s.protocol.upper()],
                    service=s.service
                )
                if 'product' in s.service_dict and 'version' in s.service_dict:
                    technology = self.create_finding(
                        Technology,
                        enumeration=enumeration,
                        name=s.service_dict.get('product'),
                        version=s.service_dict.get('version')
                    )
                    if s.scripts_results:
                        self.parse_nse_scripts(s.scripts_results, technology)
