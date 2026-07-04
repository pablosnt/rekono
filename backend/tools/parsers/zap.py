"""OWASP ZAP web application security scanner output parser.

Processes OWASP ZAP XML output to extract web application vulnerabilities
and discovered endpoints from security scans.
"""

from html import unescape
from urllib.parse import urlparse

from findings.enums import PathType, Severity
from findings.models import Path, Vulnerability
from tools.parsers.base import BaseParser


class Zap(BaseParser):
    """Parser for OWASP ZAP XML output files.

    Extracts web application vulnerability findings and discovered endpoints
    from OWASP ZAP security scans. Processes vulnerability alerts with severity
    mapping and endpoint discovery for comprehensive web security analysis.

    Attributes:
        severity_mapping (dict): Mapping between ZAP and Rekono severity levels
    """

    # Mapping between OWASP ZAP severity values and Rekono severity values
    severity_mapping = {
        0: Severity.INFO,
        1: Severity.LOW,
        2: Severity.MEDIUM,
        3: Severity.HIGH,
    }

    def _parse(self) -> None:
        """Parse OWASP ZAP XML output and extract web security findings.

        Processes XML scan results to create Vulnerability and Path findings
        from web application security tests.
        """
        endpoints = set(["/"])
        root = self.load_xml_report()
        if not root:
            return
        for site in root.findall("site"):
            for alert in site.findall("alerts/alertitem"):
                name = alert.findtext("alert")
                description = alert.findtext("desc") or ""
                severity = alert.findtext("riskcode")
                cwe = alert.findtext("cweid")
                remediation = alert.findtext("solution")
                reference = alert.findtext("reference")
                instances = alert.findall("instances/instance")
                if instances:
                    description += "\n\nLocation:\n"
                    for instance in instances:
                        url = instance.findtext("uri")
                        description += f"[{instance.findtext('method')}] {url}\n"
                        if url:
                            parsed = urlparse(url)
                            if parsed and parsed.path:
                                endpoint = Path.clean_path(parsed.path)
                                if endpoint not in endpoints:
                                    endpoints.add(endpoint)
                                    self.create_finding(Path, path=endpoint, type=PathType.ENDPOINT)
                if name:
                    name = self._clean(name)
                    self.create_finding(
                        Vulnerability,
                        name=name,
                        description=self._clean(description) if description else name,
                        severity=self.severity_mapping[int(severity)] if severity else Severity.MEDIUM,
                        cwes=[f"CWE-{cwe}"] if cwe else [],
                        remediation=self._clean(remediation) if remediation else None,
                        reference=self._clean(reference.split("</p><p>", 1)[0]) if reference else None,
                    )

    def _clean(self, value: str) -> str:
        """Clean HTML-encoded text from ZAP output.

        Args:
            value (str): HTML-encoded text to clean

        Returns:
            str: Cleaned text with HTML entities unescaped and tags removed
        """
        return unescape(value).replace("<p>", "").replace("</p>", "")
