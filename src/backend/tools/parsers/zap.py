from html import unescape

from findings.enums import PathType, Severity
from findings.models import Path, Vulnerability
from tools.parsers.base import BaseParser


class Zap(BaseParser):
    # Mapping between OWASP ZAP severity values and Rekono severity values
    severity_mapping = {
        0: Severity.INFO,
        1: Severity.LOW,
        2: Severity.MEDIUM,
        3: Severity.HIGH,
    }

    def _parse_report(self) -> None:
        endpoints = set(["/"])
        root = self._load_report_as_xml()
        for site in root:
            url_base = site.attrib["name"]
            for alert in site.findall("alerts/alertitem"):
                description = alert.findtext("desc") or ""
                severity = alert.findtext("riskcode")
                cwe = alert.findtext("cweid")
                reference = alert.findtext("reference")
                instances = alert.findall("instances/instance")
                if instances:
                    description += "\n\nLocation:\n"
                for instance in instances or []:
                    url = instance.findtext("uri")
                    name = alert.findtext("alert")
                    description += f'[{instance.findtext("method")}] {url}\n'
                    if url:
                        endpoint = url.replace(url_base, "")
                        if endpoint and endpoint not in endpoints:
                            endpoints.add(endpoint)
                            self.create_finding(
                                Path, path=endpoint, type=PathType.ENDPOINT
                            )
                    if name:
                        self.create_finding(
                            Vulnerability,
                            name=self._clean(name),
                            description=self._clean(description)
                            if description
                            else self._clean(name),
                            severity=self.severity_mapping[int(severity)]
                            if severity
                            else Severity.MEDIUM,
                            cwe=f"CWE-{cwe}" if cwe else None,
                            reference=self._clean(reference) if reference else None,
                        )

    def _clean(self, value: str) -> str:
        return (
            unescape(value)
            .split("</p><p>", 1)[0]
            .replace("<p>", "")
            .replace("</p>", "")
        )
