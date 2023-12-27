from findings.enums import OSINTDataType, PathType
from findings.models import OSINT, Path
from tools.parsers.base import BaseParser


class Gobuster(BaseParser):
    def _parse_report(self) -> None:
        data = self._load_report_by_lines()
        for line in data:
            if " (Status: " in line and ") [Size: " in line:  # Endpoint format
                aux = line.split(" (Status: ")
                self.create_finding(
                    Path,
                    path=aux[0].strip(),
                    status=int(aux[1].split(")")[0].strip()),
                    type=PathType.ENDPOINT,
                )
            elif " Status: " in line and " [Size: " in line:  # VHOST format
                vhost, status = line.replace("Found: ", "").split(" Status: ")
                if status.split(" [")[0].strip().startswith("2"):
                    if "://" in vhost:
                        vhost = vhost.split("://")[1]
                    self.create_finding(
                        OSINT,
                        data=vhost.strip(),
                        data_type=OSINTDataType.VHOST,
                        source="Enumeration",
                    )
            elif " [" in line and "]" in line:  # Subdomain format
                subdomain, addresses = line.replace("Found: ", "").split(" [")
                addresses = addresses.replace("]", "").split(",")
                self.create_finding(
                    OSINT,
                    data=subdomain.strip(),
                    data_type=OSINTDataType.DOMAIN,
                    source="DNS",
                )
                for address in addresses:
                    self.create_finding(
                        OSINT,
                        data=address.strip(),
                        data_type=OSINTDataType.IP,
                        source="DNS",
                    )
