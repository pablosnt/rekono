"""Parser of the Gobuster enumeration tool."""

from findings.enums import OSINTDataType, PathType
from findings.models import OSINT, Path
from tools.parsers.base import BaseParser


class Gobuster(BaseParser):
    """Findings discovered by Gobuster, read from its report."""

    def _parse(self) -> None:
        """Create the paths, the subdomains, and the vhosts that Gobuster reports.

        Gobuster enumerates all of them with the same command and its report says
        nothing about what it enumerated, so each line is recognized by the format
        that the mode which wrote it produces.
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
