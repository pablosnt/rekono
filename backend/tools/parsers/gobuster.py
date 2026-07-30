"""Gobuster directory and subdomain enumeration output parser.

Processes Gobuster's line-based plain text output to extract discovered paths,
subdomains, and virtual hosts from brute force enumeration scans.
"""

from findings.enums import OSINTDataType, PathType
from findings.models import OSINT, Path
from tools.parsers.base import BaseParser


class Gobuster(BaseParser):
    """Parser for Gobuster enumeration output files.

    Extracts discovered endpoints, subdomains, and virtual hosts from Gobuster's
    line-based plain text output. Supports multiple scan modes including directory,
    subdomain, and VHOST enumeration, telling them apart by matching each line
    against the literal format each mode is known to produce, since the report
    carries no explicit marker of which mode generated it.

    Attributes:
        Inherits all attributes from BaseParser
    """

    def _parse(self) -> None:
        """Parse Gobuster output and extract discovery findings.

        Processes line-based output to create Path and OSINT findings for
        discovered endpoints, subdomains, and virtual hosts.
        """
        data = self.load_report_by_lines()
        for line in data:
            if " (Status: " in line and ") [Size: " in line:  # Endpoint format
                aux = line.split(" (Status: ")
                # A redirect target gobuster appends in brackets for 3xx entries,
                # e.g. "[--> http://...]", is not captured, only the path and status are
                self.create_finding(
                    Path,
                    path=Path.clean_path(aux[0].strip()),
                    status=int(aux[1].split(")")[0].strip()),
                    type=PathType.ENDPOINT,
                )
            # VHOST format: same as the endpoint format above but without parentheses around the status
            elif " Status: " in line and " [Size: " in line:
                vhost, status = line.replace("Found: ", "").split(" Status: ")
                status = status.split(" [")[0].strip()
                # Wildcard DNS responses make gobuster report a "Found" line for almost every
                # attempted vhost, so only 2xx/3xx responses are kept as genuine hits
                if status.startswith("2") or status.startswith("3"):
                    # Not every entry has a full scheme prefix, e.g. some use a bare "dns:"
                    # with no slashes, so the prefix is only stripped when "://" is present
                    if "://" in vhost:
                        vhost = vhost.split("://")[1]
                    self.create_finding(
                        OSINT, data=vhost.strip(), data_type=OSINTDataType.VHOST, source="VHOST enumeration"
                    )
            elif len(line.split(" ", 1)) == 2:  # Subdomain format: "<subdomain> <ip1>,<ip2>..."
                subdomain, addresses = line.split(" ", 1)
                self.create_finding(OSINT, data=subdomain.strip(), data_type=OSINTDataType.DOMAIN, source="DNS")
                for address in addresses.strip().split(","):
                    self.create_finding(OSINT, data=address.strip(), data_type=OSINTDataType.IP, source="DNS")
