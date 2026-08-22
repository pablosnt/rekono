"""Parser of the Nikto web scanner."""

from findings.enums import PathType, Severity
from findings.models import Path, Vulnerability
from tools.parsers.base import BaseParser


class Nikto(BaseParser):
    """Findings discovered by Nikto, read from its XML report."""

    def _parse(self) -> None:
        """Create the vulnerabilities and the paths that Nikto reports.

        Nikto doesn't rate what it finds, so every vulnerability gets the same
        severity.
        """
        # "/" is preseeded here so it never gets its own Path finding, even though most
        # items reference it, since it's already implicit for the scanned target
        endpoints = set(["/"])
        root = self.load_xml_report()
        if not root:
            return
        # Old reports wrap the scan in a bare <niktoscan> root, new reports use <niktoscans>;
        # either way the actual data is under the last matching "niktoscan" child
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
                        # Some descriptions already start with the endpoint, e.g.
                        # "/images/: Directory indexing found.", so it's only prefixed when missing
                        f"[{method} {endpoint}] {description}"
                        if endpoint and not description.startswith(endpoint)
                        else f"[{method}] {description}"
                    ),
                    severity=Severity.MEDIUM,
                    reference=references.split(",")[0] if references else None,  # Field doesn't exist on old reports
                )
            if endpoint and endpoint not in endpoints:
                endpoints.add(endpoint)
                self.create_finding(Path, path=Path.clean_path(endpoint), type=PathType.ENDPOINT)
