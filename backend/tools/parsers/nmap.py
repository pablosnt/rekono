"""Parser of the Nmap network scanner.

Besides the hosts, the ports, and the technologies that Nmap discovers itself, its
NSE scripts report vulnerabilities, credentials, and shared resources, so this
parser also knows what the scripts that Rekono runs write in their output.
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
    "unfiltered": PortStatus.OPEN,
    "closed": PortStatus.CLOSED,
    "filtered": PortStatus.FILTERED,
    "open|filtered": PortStatus.OPEN_FILTERED,
    "closed|filtered": PortStatus.CLOSED_FILTERED,
}


class Nmap(BaseParser):
    """Findings discovered by Nmap, read from its XML report."""

    def _parse(self) -> None:
        """Create the findings that Nmap and its NSE scripts report."""
        report = NmapParser.parse_fromfile(self.report)
        for nmap_host in report.hosts:
            if not nmap_host.is_up():
                continue
            # Nmap reports every operating system that the host could be running, with how
            # sure it is about each one, so the most accurate one is the one taken
            os_detection = nmap_host.os_match_probabilities()
            selected_os = max(os_detection, key=lambda o: o.accuracy) if os_detection else None
            selected_class = max(selected_os.osclasses, key=lambda c: c.accuracy) if selected_os else None
            os_type = HostOS.OTHER
            if selected_class:
                try:
                    os_type = HostOS[selected_class.osfamily.upper()]
                except KeyError:
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
                    # Any state string nmap reports that isn't covered by PORT_STATUSES falls back
                    # to OPEN_FILTERED instead of raising, so an unrecognized value doesn't abort
                    # parsing the rest of the hosts
                    status=PORT_STATUSES.get(service.state.lower(), PortStatus.OPEN_FILTERED),
                    protocol=TransportProtocol[service.protocol.upper()],
                    service=service.service,
                )
                technologies = []
                if "product" in service.service_dict and "version" in service.service_dict:
                    technology = self.create_finding(
                        Technology,
                        linked_finding=True,
                        port=port,
                        name=service.service_dict["product"],
                        version=service.service_dict["version"],
                    )
                    technologies.append(technology)
                    if service.scripts_results:
                        self._parse_nse_scripts(service.scripts_results, technology, port)
            if nmap_host.scripts_results:
                self._parse_nse_scripts(nmap_host.scripts_results, technologies)

    def _parse_nse_scripts(
        self, results: Any, technologies: list[Technology] | Technology, port: Port | None = None
    ) -> None:
        """Create the findings that the NSE scripts of Nmap report.

        Args:
            results: Output of the scripts that Nmap ran.
            technologies: Technologies found in the port, or the whole host if the
              scripts were run against the host instead of against one port.
            port: Port where the scripts were run, used to link the findings when
              no technology was identified in it.
        """
        technology = (
            technologies if isinstance(technologies, Technology) else (technologies[0] if technologies else None)
        )
        # The SMB findings are linked to the SMB technology, which is the only one that can be
        # identified among the technologies of a host
        smb_technologies = (
            [technologies]
            if isinstance(technologies, Technology)
            else [t for t in technologies if t.port.service in ["microsoft-ds", "netbios-ssn"]]
        )
        smb_technology = smb_technologies[0] if smb_technologies else None
        technology_link = {"technology": technology} if technology else {"port": port}
        is_technology_link = technology is not None or port is not None
        smb_link = {"technology": smb_technology} if smb_technology else {"port": port}
        is_smb_link = smb_technology is not None or port is not None
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
                        # CWE-78: Improper Neutralization of Special Elements used in an OS
                        # Command ('OS Command Injection')
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
                        # CWE-78: Improper Neutralization of Special Elements used in an OS
                        # Command ('OS Command Injection')
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
                    # Unlike smb-enum-shares, this script's output is plain text lines such as
                    # "username (RID: 500)" instead of a structured "elements" table
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
                    for share, fields in script.get("elements", {}).items():
                        # The script also reports which account it used to enumerate the shares,
                        # which isn't a share itself
                        if "account_used" not in share:
                            path = share.rsplit("\\", 1)[1] if "\\" in share else share
                            anonymous = fields.get("Anonymous access")
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
                        # Nmap's NSE table entries without a "key" attribute are parsed into a list
                        # stored under the key None, which is where the dialects list ends up here
                        smb_technology.description = f"Protocols: {', '.join([p.split('[dangerous', 1)[0].strip() for p in script.get('elements', {}).get('dialects', {}).get(None)])}"
                        smb_technology.save(update_fields=["description"])
                case "http-git":
                    if "Git repository found!" in script.get("output", ""):
                        self.create_finding(
                            Path,
                            linked_finding=is_technology_link,
                            port=technology.port if technology else port,
                            path=Path.clean_path("/.git"),
                            type=PathType.ENDPOINT,
                        )
                        self.create_finding(
                            Vulnerability,
                            linked_finding=is_technology_link,
                            **technology_link,
                            name="Exposed git repository",
                            description="Git repository is exposed in the endpoint /.git/ and it's possible to dump it and access the git history and source code",
                            severity=Severity.HIGH,
                            # CWE-527: Exposure of Version-Control Repository to an Unauthorized Control Sphere
                            cwes=["CWE-527"],
                            reference="https://iosentrix.com/blog/git-source-code-disclosure-vulnerability/",
                        )
                case _:
                    self._parse_nse_vulners(script, technology, port)

    def _parse_nse_vulners(self, script: Any, technology: Technology | None, port: Port | None = None) -> None:
        """Create one vulnerability per CVE found in the output of an NSE script.

        Args:
            script: Output of the script that reported the CVEs.
            technology: Technology that the vulnerabilities were found in.
            port: Port where the script was run, used to link the vulnerabilities
              when no technology was identified in it.
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
