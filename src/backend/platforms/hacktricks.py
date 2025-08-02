import defusedxml.ElementTree as parser

from executions.models import Execution
from findings.enums import HostOS
from findings.framework.models import Finding
from findings.models import Host, Port, Technology
from framework.platforms import BaseIntegration


class HackTricks(BaseIntegration):
    finding_types = [Host, Port, Technology]
    sitemap_url = "https://www.hacktricks.wiki/sitemap.xml"
    url = "https://book.hacktricks.wiki/en/"

    def __init__(self) -> None:
        super().__init__()
        # TODO: Unit test to ensure all these custom URLs are still alive
        self.services_base_url = f"{self.url}network-services-pentesting/"
        self.web_base_url = f"{self.url}pentesting-web/"
        self.host_type_mapping = {
            HostOS.LINUX: f"{self.url}linux-hardening/privilege-escalation/index.html",
            HostOS.MACOS: f"{self.url}macos-hardening/macos-security-and-privilege-escalation/index.html",
            HostOS.WINDOWS: f"{self.url}windows-hardening/windows-local-privilege-escalation/index.html",
            HostOS.ANDROID: f"{self.url}mobile-pentesting/android-app-pentesting/index.html",
            HostOS.IOS: f"{self.url}mobile-pentesting/ios-pentesting/index.html",
        }
        self.services_mapping = {
            f"{self.url}generic-methodologies-and-resources/pentesting-network/dhcpv6.html": [
                "dhcps",
                "dhcpc",
                "dhcpv6-server",
                "dhcpv6-client",
                "dhcp-failover",
                "dhcp-failover2",
            ],
            f"{self.url}pentesting-web/sql-injection/index.html": [
                "sqlserv",
                "sqlsrv",
                "msql",
            ],
            f"{self.url}pentesting-web/sql-injection/mysql-injection/index.html": ["mysql-cm-agent"],
            f"{self.url}pentesting-web/web-vulnerabilities-methodology.html": [
                "http",
                "https",
                "http-mgmt",
                "http-alt",
                "http-rpc-epmap",
                "httpx",
            ],
            f"{self.url}windows-hardening/active-directory-methodology/kerberoast.html": [
                "kerberos-adm",
                "kadmin",
                "krb_prop",
                "krbupdate",
                "kpasswd",
                "pkt-krb-ipsec",
            ],
            f"{self.url}generic-methodologies-and-resources/pentesting-network/network-protocols-explained-esp.html#radius": [
                "radius",
                "radacct",
            ],
            f"{self.url}pentesting-web/sql-injection/oracle-injection.html": ["sqlnet"],
            f"{self.services_base_url}ipsec-ike-vpn-pentesting.html": [
                "openvpn",
                "vpnz",
                "isakmp",
            ],
            f"{self.services_base_url}pentesting-mssql-microsoft-sql-server/index.html": ["rsqlserver"],
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

    # Separation in method needed for unit tests mocking
    def _get_all_hacktricks_links(self) -> list[str]:
        return [
            url[0].text for url in parser.fromstring(self._request(self.session.get, self.sitemap_url, json=False).text)
        ]

    def _get_mapped_value_for_service(self, service: str) -> tuple[str | None, str | None]:
        value = None
        for mapped_value, services in self.services_mapping.items():
            if service in services:
                value = mapped_value
                break
        if self.url in (value or ""):
            return value, None
        else:
            return None, value

    def _process_finding(self, execution: Execution, finding: Finding) -> None:
        hacktricks_link = None
        if isinstance(finding, Host) and finding.os_type in self.host_type_mapping:
            hacktricks_link = self.host_type_mapping[finding.os_type]
        elif isinstance(finding, Port) and finding.service:
            service_comparator = finding.service.lower().strip()
            hacktricks_link, service_comparator = self._get_mapped_value_for_service(service_comparator)
            if not hacktricks_link:
                for link in self.all_links:
                    if self.services_base_url not in link:
                        continue
                    url_service_path = link.replace(self.services_base_url, "").strip()
                    url_service_parts = url_service_path.split("-")
                    if "/" not in url_service_path and (
                        service_comparator in url_service_parts
                        or (
                            str(finding.port) in url_service_parts
                            and any(
                                [
                                    p
                                    for p in url_service_parts
                                    if p.lower().strip() in service_comparator
                                    or p.lower().strip() in service_comparator.replace("-", "")
                                    or service_comparator in p
                                ]
                            )
                        )
                    ):
                        hacktricks_link = link
                        break
        elif isinstance(finding, Technology):
            for base in [self.services_base_url, self.web_base_url]:
                for link in self.all_links:
                    if base in link and finding.name.lower() in link.lower():
                        hacktricks_link = link
                        break
                if hacktricks_link:
                    break
        if hacktricks_link:
            finding.hacktricks_link = hacktricks_link
            finding.save(update_fields=["hacktricks_link"])
