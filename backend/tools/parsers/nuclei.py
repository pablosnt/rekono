"""Parser of the Nuclei vulnerability scanner."""

import json
import re
from typing import cast
from urllib.parse import urlparse

from findings.enums import PathType, Severity
from findings.models import Credential, Path, Port, Technology, Vulnerability
from tools.parsers.base import BaseParser


class Nuclei(BaseParser):
    """Findings discovered by Nuclei, read from its report.

    Nuclei writes one JSON object per line instead of one JSON document, and the
    kind of finding that each line reports is decided by the tags of the template
    that matched it.
    """

    def _parse(self) -> None:
        """Create the findings that the Nuclei templates report.

        The severity and the identifiers of a vulnerability come from the template
        that found it, so they are as complete as its author made them.
        """
        data = [json.loads(line) for line in self.load_report_by_lines()]
        paths = []
        ports: dict[int, Port | None] = {}
        for item in data:
            port = None
            _port_number = item.get("port")
            matched_at = item.get("matched-at")
            if matched_at:
                parse = urlparse(matched_at if "://" in matched_at else f"//{matched_at}")
                if parse.path and parse.path != "/" and parse.path not in paths:
                    paths.append(parse.path)
                # Only some templates report the port, so the rest take it from the URL that
                # they matched against
                if not _port_number:
                    _port_number = parse.port
            if _port_number:
                try:
                    port_number = int(_port_number)
                except (TypeError, ValueError):
                    port_number = None
                if port_number:
                    if port_number not in ports:
                        ports[port_number] = self.create_finding(Port, port=port_number)
                    port = ports[port_number]
            # The matcher says what the template found, like the version of a technology or the
            # name of the check that succeeded
            matcher = None
            if item.get("extracted-results", []):
                result = item.get("extracted-results", [])[0]
                if result not in ["security"]:
                    matcher = result
            elif item.get("matcher-name"):
                matcher = item.get("matcher-name")
            info = item.get("info", {})
            name = info.get("name")
            description = info.get("description")
            # A template can list several reference URLs; only the first one is kept
            reference = info.get("reference", [])
            tags = info.get("tags", []) or []
            if "tech" in tags:
                tech_name = matcher or name
                version = None
                if matcher and item.get("extractor-name") == "version":
                    # The "version" extractor yields the version string itself, so the technology
                    # name comes from the template instead of the extracted result
                    version = matcher
                    tech_name = name
                self.create_finding(
                    Technology,
                    **({"port": port, "linked_finding": True} if port else {}),
                    # Drop trailing detection descriptors so the technology name stays clean
                    name=re.split(r"\s+(?:End-of-Life|Detection|Detect|Version)\b", tech_name)[0].strip() or tech_name,
                    version=version,
                    # Reuse the template name as description only when the matcher already replaced it as the name
                    description=description.strip() if description else (name if matcher else None),
                    reference=reference[0] if reference else None,
                )
            elif "default-login" in tags and item.get("meta"):
                self.create_finding(
                    Credential,
                    username=item.get("meta", {}).get("username"),
                    secret=item.get("meta", {}).get("password"),
                    context=matcher or name,
                )
            else:
                severity = info.get("severity")
                classification = info.get("classification", {})
                # CVE and CWE identifiers are optional per template: the classification block
                # itself, or either key inside it, may be missing or null
                cve = classification.get("cve-id")
                cwe = classification.get("cwe-id", [])
                remediation = info.get("remediation")
                attributes = {
                    "name": (f"{name}: {matcher}" if matcher else name).strip(),
                    "description": description.strip() if description else None,
                    "severity": (cast(dict[str, str], Severity)[severity.upper()] if severity else Severity.INFO),
                    "cvss_vector": classification.get("cvss-metrics"),
                    "cwes": [c.upper() for c in cwe] if cwe else [],
                    "remediation": remediation.strip() if remediation else None,
                    "reference": reference[0] if reference else None,
                }
                if port:
                    attributes["port"] = port
                    attributes["linked_finding"] = True
                if cve and isinstance(cve, list):
                    # A template can reference more than one CVE, so a separate Vulnerability
                    # finding is created per CVE, all sharing the same other attributes
                    for cve_value in cve:
                        attributes["cve"] = cve_value.upper()
                        self.create_finding(Vulnerability, **attributes)
                else:
                    attributes["cve"] = cve.upper() if cve else None
                    self.create_finding(Vulnerability, **attributes)
        for path in paths:
            self.create_finding(Path, path=Path.clean_path(path), type=PathType.ENDPOINT)
