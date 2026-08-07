"""Parser of the OWASP ZAP web scanner."""

from html import unescape
from urllib.parse import urlparse

from findings.enums import PathType, Severity
from findings.models import Path, Vulnerability
from tools.parsers.base import BaseParser


class Zap(BaseParser):
    """Findings discovered by ZAP, read from its XML report.

    Attributes:
        severity_mapping: Rekono severity that each ZAP risk code means.
    """

    severity_mapping = {
        0: Severity.INFO,
        1: Severity.LOW,
        2: Severity.MEDIUM,
        3: Severity.HIGH,
    }

    def _parse(self) -> None:
        """Create the vulnerabilities and the paths that ZAP reports.

        ZAP reports every place where it found a vulnerability, so those places are
        added to the description and become paths of their own.
        """
        # "/" is preseeded here so it never gets its own Path finding, since it's already
        # implicit for the scanned target
        endpoints = set(["/"])
        root = self.load_xml_report()
        if not root:
            return
        for site in root.findall("site"):
            for alert in site.findall("alerts/alertitem"):
                name = alert.findtext("alert")
                description = alert.findtext("desc") or ""
                # riskcode is a numeric string, not an int, so a literal "0" (Info) is still
                # truthy below and correctly mapped instead of falling back to MEDIUM
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
                        cwes=[f"CWE-{cwe}"] if cwe and cwe != "-1" else [],  # ZAP uses -1 for "no CWE mapping"
                        remediation=self._clean(remediation) if remediation else None,
                        # ZAP concatenates multiple references as consecutive <p> paragraphs,
                        # so only the first one is kept
                        reference=self._clean(reference.split("</p><p>", 1)[0]) if reference else None,
                    )

    def _clean(self, value: str) -> str:
        """Get a text without the HTML that ZAP writes its descriptions with.

        Args:
            value: Text taken from the ZAP report.

        Returns:
            The text with the HTML entities decoded and the paragraph tags removed.
        """
        return unescape(value).replace("<p>", "").replace("</p>", "")
