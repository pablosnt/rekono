from typing import List, Optional
from findings.enums import HostOS
from executions.models import Execution
from findings.framework.models import Finding
from findings.models import Host, Port, Technology
from framework.platforms import BaseIntegration
import defusedxml.ElementTree as parser


class HackTricks(BaseIntegration):
    def __init__(self) -> None:
        self.url = "https://book.hacktricks.xyz/"
        super().__init__()
        self.hacktricks_sitemap_url = f"{self.url}sitemap.xml"
        self.hacktricks_services_base_url = f"{self.url}network-services-pentesting/"
        self.hacktricks_pentesting_web_url = (
            f"{self.hacktricks_services_base_url}pentesting-web/"
        )
        self.host_type_mapping = {
            HostOS.LINUX: f"{self.url}linux-hardening/",
            HostOS.MACOS: f"{self.url}macos-hardening/",
            HostOS.WINDOWS: f"{self.url}windows-hardening/",
            HostOS.ANDROID: f"{self.url}mobile-pentesting/android-app-pentesting",
            HostOS.IOS: f"{self.url}mobile-pentesting/ios-pentesting",
        }
        self.services_mapping = {
            f"{self.url}generic-methodologies-and-resources/pentesting-network/dhcpv6": [
                "dhcps",
                "dhcpc",
                "dhcpv6-server",
                "dhcpv6-client",
                "dhcp-failover",
                "dhcp-failover2",
            ],
            f"{self.url}pentesting-web/sql-injection": ["sqlserv", "sqlsrv", "msql"],
            f"{self.url}pentesting-web/sql-injection/mysql-injection": [
                "mysql-cm-agent"
            ],
            f"{self.url}pentesting-web/web-vulnerabilities-methodology": [
                "http",
                "https",
                "http-mgmt",
                "http-alt",
                "http-rpc-epmap",
                "httpx",
            ],
            f"{self.url}windows-hardening/active-directory-methodology/kerberoast": [
                "kerberos-adm",
                "kadmin",
                "krb_prop",
                "krbupdate",
                "kpasswd",
                "pkt-krb-ipsec",
            ],
            f"{self.url}generic-methodologies-and-resources/pentesting-network/network-protocols-explained-esp#radius": [
                "radius",
                "radacct",
            ],
            f"{self.hacktricks_pentesting_web_url}sql-injection/oracle-injection": [
                "sqlnet"
            ],
            f"{self.hacktricks_services_base_url}ipsec-ike-vpn-pentesting": [
                "openvpn",
                "vpnz",
                "isakmp",
            ],
            f"{self.hacktricks_services_base_url}pentesting-mssql-microsoft-sql-server": [
                "rsqlserver"
            ],
            f"{self.hacktricks_services_base_url}/pentesting-printers/physical-damage#postscript": [
                "print-srv"
            ],
            "ftp": ["ftps", "ftp-data", "ftps-data", "via-ftp", "sftp", "ftp-agent"],
            "dns": ["domain"],
            "smb": ["microsoft-ds", "netbios-ssn"],
            "pop": ["pop2", "pop3", "pop3s"],
            "smtp": ["smtps"],
            "rlogin": ["login"],
            "imap": ["imap3", "imap4-ssl", "apple-imap-admin", "imaps"],
            "ldap": ["ldapssl", "ldaps"],
            "telnet": ["telnets"],
            "irc": ["ircs"],
        }
        self.all_links = self._get_all_hacktricks_links()

    def _get_all_hacktricks_links(self) -> List[str]:
        sitemap = self._request(self.hacktricks_sitemap_url, json=False)
        return [url[0].text for url in parser.fromstring(sitemap.text).getroot()]

    def _get_mapped_value_for_service(self, service: str) -> Optional[str]:
        for mapped_value, services in self.services_mapping.items():
            if service in services:
                return mapped_value
        return None  # TOTEST

    def process_findings(self, execution: Execution, findings: List[Finding]) -> None:
        super().process_findings(execution, findings)
        for finding in findings:
            hacktricks_link = None
            if isinstance(finding, Host) and finding.os_type in self.host_type_mapping:
                hacktricks_link = self.host_type_mapping[finding.os_type]
            elif isinstance(finding, Port) and finding.service:
                service_comparator = finding.service.lower().strip()
                mapped_value = self._get_mapped_value_for_service(service_comparator)
                if self.url in (mapped_value or ""):
                    hacktricks_link = mapped_value
                elif mapped_value:  # TOTEST
                    service_comparator = mapped_value
                if not hacktricks_link:
                    for link in self.all_links:
                        if self.hacktricks_services_base_url not in link:
                            continue
                        comparator = link.replace(
                            self.hacktricks_services_base_url, ""
                        ).strip()
                        link_parts = comparator.split("-")
                        if "/" not in comparator and (
                            service_comparator in link_parts
                            or (
                                str(finding.port) in link_parts
                                and (
                                    len(
                                        [
                                            p
                                            for p in link_parts
                                            if p.lower().strip() in service_comparator
                                            or p.lower().strip()
                                            in service_comparator.replace("-", "")
                                            or service_comparator in p
                                        ]
                                    )
                                    > 0
                                )
                            )
                        ):
                            hacktricks_link = link
                            break
            elif isinstance(finding, Technology):
                expected_url = (
                    f"{self.hacktricks_pentesting_web_url}{finding.name.lower()}"
                )
                if expected_url in self.all_links:
                    hacktricks_link = expected_url
            if hacktricks_link:
                finding.hacktricks_link = hacktricks_link
                finding.save(update_fields=["hacktricks_link"])
