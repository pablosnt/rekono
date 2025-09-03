"""HackTricks penetration testing knowledge base integration.

Provides integration with HackTricks.wiki to automatically enrich security
findings with relevant penetration testing methodologies, exploitation
techniques, and security guidance documentation.
"""

import defusedxml.ElementTree as parser

from executions.models import Execution
from findings.enums import HostOS
from findings.framework.models import Finding
from findings.models import Host, Port, Technology
from framework.platforms import BaseIntegration


class HackTricks(BaseIntegration):
    """Integration class for HackTricks penetration testing knowledge base.

    Automatically enriches security findings with links to relevant HackTricks
    documentation including penetration testing methodologies, privilege escalation
    techniques, and service-specific exploitation guides.

    Processing Features:
        - Host-based methodology linking for privilege escalation techniques
        - Service-specific penetration testing guide mapping
        - Technology-specific exploitation methodology references
        - Dynamic sitemap parsing for up-to-date documentation links
        - Intelligent service name matching and URL construction

    Attributes:
        finding_types (list): List of finding types processed by this integration
        sitemap_url (str): HackTricks sitemap URL for dynamic link discovery
        url (str): Base HackTricks documentation URL
        services_base_url (str): Base URL for network service pentesting guides
        web_base_url (str): Base URL for web application pentesting guides
        host_type_mapping (dict): OS-specific privilege escalation guide URLs
        services_mapping (dict): Service name to documentation URL mappings
        all_links (list): Cached list of all available HackTricks documentation links
    """

    finding_types = [Host, Port, Technology]
    sitemap_url = "https://www.hacktricks.wiki/sitemap.xml"
    url = "https://book.hacktricks.wiki/en/"

    def __init__(self) -> None:
        """Initialize HackTricks integration with URL mappings and link discovery.

        Sets up service mappings, host type mappings, and retrieves all available
        documentation links from the HackTricks sitemap for dynamic matching.
        """
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

    def _get_all_hacktricks_links(self) -> list[str]:
        """Retrieve all available HackTricks documentation links from sitemap.

        Parses the HackTricks XML sitemap to extract all available documentation
        URLs for dynamic matching against discovered findings.

        Returns:
            list[str]: List of all HackTricks documentation URLs

        Note:
            Method separation enables unit testing with mocked network requests.
        """
        return [
            url[0].text for url in parser.fromstring(self._request(self.session.get, self.sitemap_url, json=False).text)
        ]

    def _get_mapped_value_for_service(self, service: str) -> tuple[str | None, str | None]:
        """Get mapped HackTricks URL for a specific service name.

        Searches the services mapping to find the appropriate HackTricks
        documentation URL for the given service name.

        Args:
            service (str): Service name to find documentation for

        Returns:
            tuple[str | None, str | None]: Tuple containing (hacktricks_url, service_name)
                                          where hacktricks_url is the mapped URL or None,
                                          and service_name is the processed service name
        """
        for mapped_value, services in self.services_mapping.items():
            if service in services:
                if self.url in (mapped_value or ""):
                    return mapped_value, None
                else:
                    return None, mapped_value
        return None, service

    def _process_finding(self, execution: Execution, finding: Finding) -> None:
        """Process and enrich finding with relevant HackTricks documentation link.

        Analyzes the finding type and characteristics to determine the most
        appropriate HackTricks methodology or guide, then updates the finding
        with the documentation link.

        Processing Logic:
            - Host findings: Match OS type to privilege escalation guides
            - Port findings: Match service names to penetration testing methodologies
            - Technology findings: Search for technology-specific exploitation guides

        Args:
            execution (Execution): The execution context for this processing
            finding (Finding): The finding to enrich with HackTricks documentation
        """
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
