from findings.enums import PathType, Severity
from findings.models import Path, Vulnerability
from tools.parsers.base import BaseParser


class Nikto(BaseParser):
    def _parse_report(self) -> None:
        endpoints = set(["/"])
        root = self._load_report_as_xml()
        for item in root.findall("niktoscan")[-1].findall("scandetails")[0].findall("item"):
            endpoint = item.findtext("uri")
            description = item.findtext("description")
            if description:
                description = description.strip()
                method = item.attrib["method"]
                references = item.findtext("references")
                self.create_finding(
                    Vulnerability,
                    name=description,
                    description=(
                        f"[{method} {endpoint}] {description}"
                        if endpoint and not description.startswith(endpoint)
                        else f"[{method}] {description}"
                    ),
                    severity=Severity.MEDIUM,
                    reference=references.split(",")[0] if references else None,  # Field doesn't exist on old reports
                )
            if endpoint and endpoint not in endpoints:
                endpoints.add(endpoint)
                self.create_finding(Path, path=endpoint, type=PathType.ENDPOINT)
