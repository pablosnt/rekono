"""Integration with the HackTricks penetration testing wiki."""

import defusedxml.ElementTree as parser

from executions.models import Execution
from findings.enums import HostOS
from findings.framework.models import Finding
from findings.models import Host, Port, Technology
from framework.platforms import BaseIntegration


class HackTricks(BaseIntegration):
    """Integration that links the findings to the guides about how to attack them.

    Attributes:
        finding_types: Findings that HackTricks has guides about.
        url: Base URL of the wiki, in English.
        sitemap_url: Sitemap that lists every page of the wiki.
        services_base_url: Section of the wiki with the guides of the services.
        web_base_url: Section of the wiki with the guides of the web applications.
        host_type_mapping: Guide that each operating system is linked to.
        services_mapping: Guide, or name of another service, for the services whose
          page can't be found by their own name.
        all_links: Pages of the wiki, which the findings are matched against.
    """

    finding_types = [Host, Port, Technology]
    url = "https://hacktricks.wiki/en/"

    def __init__(self) -> None:
        """Prepare the integration, reading the pages that the wiki has."""
        super().__init__()
        self.sitemap_url = f"{self.url}sitemap.xml"
        self.services_base_url = f"{self.url}network-services-pentesting/"
        self.web_base_url = f"{self.url}pentesting-web/"
        self.host_type_mapping = {
            HostOS.LINUX: f"{self.url}linux-hardening/privilege-escalation/index.html",
            HostOS.MACOS: f"{self.url}macos-hardening/macos-security-and-privilege-escalation/index.html",
            HostOS.WINDOWS: f"{self.url}windows-hardening/windows-local-privilege-escalation/index.html",
            HostOS.ANDROID: f"{self.url}mobile-pentesting/android-app-pentesting/index.html",
            HostOS.IOS: f"{self.url}mobile-pentesting/ios-pentesting/index.html",
        }
        # The services whose page can't be found by their name, either because the page is
        # named after another service or because it isn't a service page at all
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

    def _get_all_hacktricks_links(self) -> list[str]:  # pragma: no cover
        """Get every page of the wiki, from its sitemap.

        Returns:
            The URL of every page, which is what the findings are matched against,
            since the wiki has no API to search in it.
        """
        return [
            url[0].text for url in parser.fromstring(self._request(self.session.get, self.sitemap_url, json=False).text)
        ]

    def _get_mapped_value_for_service(self, service: str) -> tuple[str | None, str | None]:
        """Get what the services mapping says about a service.

        Args:
            service: Name of the service, as the tools report it.

        Returns:
            The page of the service, if the mapping knows it, or the name of the
            service that its page is named after, so the caller can search for it.
        """
        for mapped_value, services in self.services_mapping.items():
            if service in services:
                # Some mapping values are already full HackTricks URLs and can be returned directly.
                # Others are just normalized service aliases (e.g. "ftp") that still need to be
                # matched against the sitemap links by the caller
                if self.url in (mapped_value or ""):
                    return mapped_value, None
                else:
                    return None, mapped_value
        return None, service

    def _process_finding(self, execution: Execution, finding: Finding) -> None:
        """Link a finding to the wiki page that explains how to attack it.

        A host is linked to the guide of its operating system, a port to the one
        of its service, and a technology to the one that talks about it.

        Args:
            execution: Execution that discovered the finding.
            finding: Finding to link to the wiki.
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
                    url_service_path = (
                        link.replace(self.services_base_url, "")
                        .replace("/index.html", "")
                        .replace("/index.html", "")
                        .replace(".html", "")
                        .replace(".htm", "")
                        .strip()
                    )
                    url_service_parts = url_service_path.split("-")
                    if "/" not in url_service_path and (
                        service_comparator in url_service_parts
                        # Falls back to the port number when the service name itself isn't part of
                        # the URL, since some HackTricks pages are named after the port instead
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
