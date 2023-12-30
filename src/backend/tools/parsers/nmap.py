import re
from typing import Any, List

from findings.enums import HostOS, PathType, PortStatus, Protocol, Severity
from findings.models import Credential, Host, Path, Port, Technology, Vulnerability
from libnmap.parser import NmapParser
from security.validators.input_validator import Regex
from tools.parsers.base import BaseParser


class Nmap(BaseParser):
    def _parse_report(self) -> None:
        report = NmapParser.parse_fromfile(self.report)
        for nmap_host in report.hosts:
            if not nmap_host.is_up():
                continue
            os_detection = nmap_host.os_match_probabilities()
            selected_os = (
                max(os_detection, key=lambda o: o.accuracy) if os_detection else None
            )
            selected_class = (
                max(selected_os.osclasses, key=lambda c: c.accuracy)
                if selected_os
                else None
            )
            os_type = HostOS.OTHER
            if selected_class:
                try:
                    os_type = HostOS[selected_class.osfamily.upper()]
                except KeyError:
                    pass
            host = self.create_finding(
                Host, address=nmap_host.address, os=selected_os.name, os_type=os_type
            )
            for service in nmap_host.services:
                port = self.create_finding(
                    Port,
                    host=host,
                    port=service.port,
                    status=PortStatus[service.state.upper()],
                    protocol=Protocol[service.protocol.upper()],
                    service=service.service,
                )
                technologies = []
                if (
                    "product" in service.service_dict
                    and "version" in service.service_dict
                ):
                    technology = self.create_finding(
                        Technology,
                        port=port,
                        name=service.service_dict["product"],
                        version=service.service_dict["version"],
                    )
                    technologies.append(technology)
                    if service.scripts_results:
                        self._parse_nse_scripts(service.scripts_results, technology)
            if nmap_host.scripts_results:
                self._parse_nse_scripts(nmap_host.scripts_results, technologies)

    def _parse_nse_scripts(
        self, results: Any, technologies: List[Technology] | Technology
    ) -> None:
        technology = (
            technologies if isinstance(technologies, Technology) else technologies[0]
        )
        smb_technologies = (
            [technologies]
            if isinstance(technologies, Technology)
            else [
                t
                for t in technologies
                if t.port.service in ["microsoft-ds", "netbios-ssn"]
            ]
        )
        smb_technology = smb_technologies[0] if smb_technologies else None
        for script in results:
            match script.get("id"):
                case "vulners":
                    self._parse_nse_vulners(script, technology)
                case "ftp-anon":
                    self.create_finding(
                        Vulnerability,
                        technology=technology,
                        name="Anonymous FTP",
                        description="Anonymous login is allowed in FTP",
                        severity=Severity.CRITICAL,
                        # CWE-287: Improper Authentication
                        cwe="CWE-287",
                        reference="https://book.hacktricks.xyz/pentesting/pentesting-ftp#anonymous-login",
                    )
                case "ftp-proftpd-backdoor":
                    self.create_finding(
                        Vulnerability,
                        technology=technology,
                        name="FTP Backdoor",
                        description="FTP ProFTPD 1.3.3c Backdoor",
                        severity=Severity.CRITICAL,
                        # CWE-78: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')
                        cwe="CWE-78",
                        osvdb="OSVDB-69562",
                    )
                case "ftp-vsftpd-backdoor":
                    self.create_finding(
                        Vulnerability,
                        technology=technology,
                        name="vsFTPd Backdoor",
                        cve="CVE-2011-2523",
                    )
                case "ftp-libopie":
                    self.create_finding(
                        Vulnerability,
                        technology=technology,
                        name="OPIE off-by-one stack overflow",
                        cve="CVE-2010-1938",
                    )
                case "ftp-vuln-cve2010-4221":
                    self.create_finding(
                        Vulnerability,
                        technology=technology,
                        name="ProFTPD server TELNET IAC stack overflow",
                        cve="CVE-2010-4221",
                    )
                case "smb-double-pulsar-backdoor":
                    self.create_finding(
                        Vulnerability,
                        technology=smb_technology,
                        name="SMB Server DOUBLEPULSAR Backdoor",
                        description=(
                            "NNM detected the presence of DOUBLEPULSAR on the remote Windows host. DOUBLEPULSAR is one of "
                            "multiple Equation Group SMB implants and backdoors disclosed on 2017/04/14 by a group known as "
                            "the 'Shadow Brokers'. The implant allows an unauthenticated, remote attacker to use SMB as a "
                            "covert channel to exfiltrate data, launch remote commands, or execute arbitrary code."
                        ),
                        severity=Severity.CRITICAL,
                        # CWE-78: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')
                        cwe="CWE-78",
                        reference="https://www.tenable.com/plugins/nnm/700059",
                    )
                case "smb-vuln-webexec":
                    self.create_finding(
                        Vulnerability,
                        technology=smb_technology,
                        name="Remote Code Execution vulnerability in WebExService",
                        cve="CVE-2018-15442",
                    )
                case "smb-vuln-cve-2017-7494":
                    self.create_finding(
                        Vulnerability,
                        technology=smb_technology,
                        name="SAMBA Remote Code Execution from Writable Share",
                        cve="CVE-2017-7494",
                    )
                case "smb2-vuln-uptime" | "smb-vuln-ms06-025" | "smb-vuln-ms07-029" | "smb-vuln-ms10-061" | "smb-vuln-ms17-010":
                    self._parse_nse_vulners(script, smb_technology)
                case "smb-enum-users":
                    for line in script.get("output").split("\n"):
                        data = line.strip()
                        if data and " (RID:" in data:
                            self.create_finding(
                                Credential,
                                technology=smb_technology,
                                username=data.split(" (RID:", 1)[0],
                                context="SMB user",
                            )
                case "smb-enum-shares":
                    for share, fields in script.get("elements", {}).items():
                        if "account_used" not in share:
                            path = share.rsplit("\\", 1)[1] if "\\" in share else share
                            anonymous = fields.get("Anonymous access")
                            self.create_finding(
                                Path,
                                port=smb_technology.port if smb_technology else None,
                                path=path,
                                extra_info=(
                                    f'{fields.get("Comment") or ""} '
                                    f'Type: {fields.get("Type")} '
                                    f"Anonymous access: {anonymous} "
                                    f'Current access: {fields.get("Current user access")}'
                                ).strip(),
                                type=PathType.SHARE,
                            )
                            if "READ" in anonymous or "WRITE" in anonymous:
                                self.create_finding(
                                    Vulnerability,
                                    technology=smb_technology,
                                    name="Anonymous SMB",
                                    description=f"Anonymous access is allowed to the SMB share {path}",
                                    severity=Severity.CRITICAL
                                    if "WRITE" in anonymous
                                    else Severity.HIGH,
                                    # CWE-287: Improper Authentication
                                    cwe="CWE-287",
                                )
                case "smb-protocols":
                    if smb_technology:
                        smb_technology.description = f'Protocols: {", ".join([p.split("[dangerous", 1)[0].strip() for p in script.get("elements", {}).get("dialects", {}).get(None)])}'
                        smb_technology.save(update_fields=["description"])
                case _:
                    self._parse_nse_vulners(script, technology)

    def _parse_nse_vulners(self, script: Any, technology: Technology) -> None:
        cves = set()
        for cve in re.findall(Regex.CVE.value, script.get("output", "")):
            if cve not in cves:
                cves.add(cve)
                self.create_finding(
                    Vulnerability, technology=technology, name=cve, cve=cve
                )
