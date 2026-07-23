"""Nmap output parser for network discovery and service detection findings.

Processes Nmap XML output to extract hosts, ports, services, technologies, and
vulnerabilities discovered during network scanning operations.
"""

import re
from typing import Any

from libnmap.parser import NmapParser

from findings.enums import HostOS, PathType, PortStatus, Severity, TransportProtocol
from findings.models import Credential, Host, Path, Port, Technology, Vulnerability
from security.validators.input_validator import Regex
from tools.parsers.base import BaseParser

# Nmap can report combined states such as "open|filtered" that can't be directly resolved to PortStatus values
PORT_STATUSES = {
    "open": PortStatus.OPEN,
    "closed": PortStatus.CLOSED,
    "filtered": PortStatus.FILTERED,
    "open|filtered": PortStatus.OPEN_FILTERED,
}


class Nmap(BaseParser):
    """Parser for Nmap XML output files.

    Extracts network discovery findings including hosts, open ports, running services,
    detected technologies, and security vulnerabilities from Nmap scan results.
    Supports NSE script output parsing for enhanced vulnerability detection.

    Attributes:
        Inherits all attributes from BaseParser
    """

    def _parse(self) -> None:
        """Parse Nmap XML output and extract security findings.

        Processes Nmap scan results to create Host, Port, Technology, and Vulnerability
        findings. Handles OS detection, service fingerprinting, and NSE script results.
        """
        report = NmapParser.parse_fromfile(self.report)
        for nmap_host in report.hosts:
            if not nmap_host.is_up():
                continue
            # Analyze OS detection results and select the most accurate match
            os_detection = nmap_host.os_match_probabilities()
            # Choose OS match with highest accuracy score
            selected_os = max(os_detection, key=lambda o: o.accuracy) if os_detection else None
            # Get the most accurate OS class from the selected OS match
            selected_class = max(selected_os.osclasses, key=lambda c: c.accuracy) if selected_os else None
            # Map Nmap OS family to our HostOS enum, defaulting to OTHER for unknown families
            os_type = HostOS.OTHER
            if selected_class:
                try:
                    os_type = HostOS[selected_class.osfamily.upper()]
                except KeyError:
                    # Keep default OTHER type if OS family not recognized
                    pass
            host = self.create_finding(
                Host, ip=nmap_host.address, os=selected_os.name if selected_os else None, os_type=os_type
            )
            for service in nmap_host.services:
                port = self.create_finding(
                    Port,
                    linked_finding=True,
                    host=host,
                    port=service.port,
                    status=PORT_STATUSES.get(service.state.lower(), PortStatus.OPEN_FILTERED),
                    protocol=TransportProtocol[service.protocol.upper()],
                    service=service.service,
                )
                technologies = []
                # Extract technology information from service fingerprinting results
                # Only create Technology finding if both product name and version are available
                if "product" in service.service_dict and "version" in service.service_dict:
                    technology = self.create_finding(
                        Technology,
                        linked_finding=True,
                        port=port,
                        name=service.service_dict["product"],
                        version=service.service_dict["version"],
                    )
                    technologies.append(technology)
                    # Process NSE scripts that provide additional vulnerability and service details
                    if service.scripts_results:
                        self._parse_nse_scripts(service.scripts_results, technology, port)
            if nmap_host.scripts_results:
                self._parse_nse_scripts(nmap_host.scripts_results, technologies)

    def _parse_nse_scripts(
        self, results: Any, technologies: list[Technology] | Technology, port: Port | None = None
    ) -> None:
        """Parse NSE script results and extract vulnerability findings.

        Args:
            results (Any): NSE script results from Nmap output
            technologies (list[Technology] | Technology): Associated technology findings
            port (Port | None): Port the scripts belong to, used as a fallback link when no
                technology was fingerprinted so findings keep traceability to the service
        """
        # Normalize technology input to handle both single Technology objects and lists
        technology = (
            technologies if isinstance(technologies, Technology) else (technologies[0] if technologies else None)
        )
        # Extract SMB-specific technologies for SMB-related vulnerabilities
        # SMB services use specific service names in Nmap output
        smb_technologies = (
            [technologies]
            if isinstance(technologies, Technology)
            else [t for t in technologies if t.port.service in ["microsoft-ds", "netbios-ssn"]]
        )
        smb_technology = smb_technologies[0] if smb_technologies else None
        # Prepare links for vulnerabilities
        technology_link = {"technology": technology} if technology else {"port": port}
        is_technology_link = technology is not None or port is not None
        smb_link = {"technology": smb_technology} if smb_technology else {"port": port}
        is_smb_link = smb_technology is not None or port is not None
        # Process each NSE script result based on its ID (script type)
        for script in results:
            match script.get("id"):
                case "vulners":
                    self._parse_nse_vulners(script, technology, port)
                case "ftp-anon":
                    self.create_finding(
                        Vulnerability,
                        linked_finding=is_technology_link,
                        **technology_link,
                        name="Anonymous FTP",
                        description="Anonymous login is allowed in FTP",
                        severity=Severity.CRITICAL,
                        # CWE-287: Improper Authentication
                        cwes=["CWE-287"],
                        reference="https://book.hacktricks.xyz/pentesting/pentesting-ftp#anonymous-login",
                    )
                case "ftp-proftpd-backdoor":
                    self.create_finding(
                        Vulnerability,
                        linked_finding=is_technology_link,
                        **technology_link,
                        name="FTP Backdoor",
                        description="FTP ProFTPD 1.3.3c Backdoor",
                        severity=Severity.CRITICAL,
                        # CWE-78: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')
                        cwes=["CWE-78"],
                    )
                case "ftp-vsftpd-backdoor":
                    self.create_finding(
                        Vulnerability,
                        linked_finding=is_technology_link,
                        **technology_link,
                        name="vsFTPd Backdoor",
                        cve="CVE-2011-2523",
                    )
                case "ftp-libopie":
                    self.create_finding(
                        Vulnerability,
                        linked_finding=is_technology_link,
                        **technology_link,
                        name="OPIE off-by-one stack overflow",
                        cve="CVE-2010-1938",
                    )
                case "ftp-vuln-cve2010-4221":
                    self.create_finding(
                        Vulnerability,
                        linked_finding=is_technology_link,
                        **technology_link,
                        name="ProFTPD server TELNET IAC stack overflow",
                        cve="CVE-2010-4221",
                    )
                case "smb-double-pulsar-backdoor":
                    self.create_finding(
                        Vulnerability,
                        linked_finding=is_smb_link,
                        **smb_link,
                        name="SMB Server DOUBLEPULSAR Backdoor",
                        description=(
                            "NNM detected the presence of DOUBLEPULSAR on the remote Windows host. DOUBLEPULSAR is one of "
                            "multiple Equation Group SMB implants and backdoors disclosed on 2017/04/14 by a group known as "
                            "the 'Shadow Brokers'. The implant allows an unauthenticated, remote attacker to use SMB as a "
                            "covert channel to exfiltrate data, launch remote commands, or execute arbitrary code."
                        ),
                        severity=Severity.CRITICAL,
                        # CWE-78: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')
                        cwes=["CWE-78"],
                        reference="https://www.tenable.com/plugins/nnm/700059",
                    )
                case "smb-vuln-webexec":
                    self.create_finding(
                        Vulnerability,
                        linked_finding=is_smb_link,
                        **smb_link,
                        name="Remote Code Execution vulnerability in WebExService",
                        cve="CVE-2018-15442",
                    )
                case "smb-vuln-cve-2017-7494":
                    self.create_finding(
                        Vulnerability,
                        linked_finding=is_smb_link,
                        **smb_link,
                        name="SAMBA Remote Code Execution from Writable Share",
                        cve="CVE-2017-7494",
                    )
                case (
                    "smb2-vuln-uptime"
                    | "smb-vuln-ms06-025"
                    | "smb-vuln-ms07-029"
                    | "smb-vuln-ms10-061"
                    | "smb-vuln-ms17-010"
                ):
                    self._parse_nse_vulners(script, smb_technology, port)
                case "smb-enum-users":
                    for line in script.get("output").split("\n"):
                        data = line.strip()
                        if data and " (RID:" in data:
                            self.create_finding(
                                Credential,
                                linked_finding=smb_technology is not None,
                                technology=smb_technology,
                                username=data.split(" (RID:", 1)[0],
                                context="SMB user",
                            )
                case "smb-enum-shares":
                    # Process SMB share enumeration results from Nmap's smb-enum-shares script
                    for share, fields in script.get("elements", {}).items():
                        # Skip shares that are metadata entries (contain account_used)
                        if "account_used" not in share:
                            # Extract clean share name from UNC path format (\\server\share -> share)
                            path = share.rsplit("\\", 1)[1] if "\\" in share else share
                            anonymous = fields.get("Anonymous access")
                            # Create a Path finding for each discovered SMB share
                            self.create_finding(
                                Path,
                                linked_finding=is_smb_link,
                                port=smb_technology.port if smb_technology else port,
                                path=path,
                                extra_info=(
                                    f"{fields.get('Comment') or ''} "
                                    f"Type: {fields.get('Type')} "
                                    f"Anonymous access: {anonymous} "
                                    f"Current access: {fields.get('Current user access')}"
                                ).strip(),
                                type=PathType.SHARE,
                            )
                            # Check for security issues with anonymous access to shares
                            # READ access is high severity, WRITE access is critical
                            if "READ" in anonymous or "WRITE" in anonymous:
                                self.create_finding(
                                    Vulnerability,
                                    linked_finding=is_smb_link,
                                    **smb_link,
                                    name="Anonymous SMB",
                                    description=f"Anonymous access is allowed to the SMB share {path}",
                                    severity=(Severity.CRITICAL if "WRITE" in anonymous else Severity.HIGH),
                                    # CWE-287: Improper Authentication
                                    cwes=["CWE-287"],
                                )
                case "smb-protocols":
                    if smb_technology:
                        smb_technology.description = f"Protocols: {', '.join([p.split('[dangerous', 1)[0].strip() for p in script.get('elements', {}).get('dialects', {}).get(None)])}"
                        smb_technology.save(update_fields=["description"])
                case _:
                    self._parse_nse_vulners(script, technology, port)

    def _parse_nse_vulners(self, script: Any, technology: Technology | None, port: Port | None = None) -> None:
        """Extract CVE references from NSE vulners script output.

        Args:
            script (Any): NSE script result containing vulnerability data
            technology (Technology | None): Technology finding to associate vulnerabilities with
            port (Port | None): Port used as a fallback link when no technology is available
        """
        cves = set()
        for cve in re.findall(Regex.CVE.value, script.get("output", "")):
            if cve not in cves:
                cves.add(cve)
                self.create_finding(
                    Vulnerability,
                    linked_finding=technology is not None or port is not None,
                    name=cve,
                    cve=cve,
                    technology=technology,
                    port=port if technology is None else None,
                )
