from findings.enums import OSINTDataType, PathType
from findings.models import OSINT, Path
from tools.parsers.base import BaseParser


class Gobuster(BaseParser):
    def _parse(self) -> None:
        data = self.load_report_by_lines()
        for line in data:
            if " (Status: " in line and ") [Size: " in line:  # Endpoint format
                aux = line.split(" (Status: ")
                self.create_finding(
                    Path, path=aux[0].strip(), status=int(aux[1].split(")")[0].strip()), type=PathType.ENDPOINT
                )
            elif " Status: " in line and " [Size: " in line:  # VHOST format
                vhost, status = line.replace("Found: ", "").split(" Status: ")
                status = status.split(" [")[0].strip()
                if status.startswith("2") or status.startswith("3"):
                    if "://" in vhost:
                        vhost = vhost.split("://")[1]
                    self.create_finding(
                        OSINT, data=vhost.strip(), data_type=OSINTDataType.VHOST, source="VHOST enumeration"
                    )
            elif " [" in line and "]" in line:  # Subdomain format
                subdomain, addresses = line.replace("Found: ", "").split(" [")
                addresses = addresses.replace("]", "").split(",")
                self.create_finding(OSINT, data=subdomain.strip(), data_type=OSINTDataType.DOMAIN, source="DNS")
                for address in addresses:
                    self.create_finding(OSINT, data=address.strip(), data_type=OSINTDataType.IP, source="DNS")
