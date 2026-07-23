"""Nuclei vulnerability scanner output parser.

Processes Nuclei JSON output to extract vulnerabilities, technology fingerprints,
credential findings, exposed ports, and discovered paths from web application
security scans. Findings are linked to the port they were detected on whenever
Nuclei reports one.
"""

import json
import re
from typing import cast
from urllib.parse import urlparse

from findings.enums import PathType, Severity
from findings.models import Credential, Path, Port, Technology, Vulnerability
from tools.parsers.base import BaseParser


class Nuclei(BaseParser):
    """Parser for Nuclei JSON output files.

    Extracts vulnerability findings, technology detections, exposed credentials,
    ports, and paths from Nuclei template-based security scans. Handles multiple
    finding types based on template tags and metadata, associating findings with
    the port they were detected on when available.

    Attributes:
        Inherits all attributes from BaseParser
    """

    def _parse(self) -> None:
        """Parse Nuclei JSON output and extract security findings.

        Processes line-delimited JSON output to create Vulnerability, Technology,
        Credential, Port, and Path findings based on template tags and extracted
        results. Technology and Vulnerability findings are linked to the Port they
        were detected on when Nuclei reports a port for the matched target.
        """
        # Parse each line of the JSON output as a separate finding
        data = [json.loads(line) for line in self.load_report_by_lines()]
        paths = []
        # Cache ports by number so the same port is reported only once
        ports: dict[int, Port | None] = {}
        for item in data:
            port = None
            # Nuclei reports the port explicitly for some templates
            _port_number = item.get("port")
            # Save the path where the Nuclei alert was triggered
            matched_at = item.get("matched-at")
            if matched_at:
                parse = urlparse(matched_at if "://" in matched_at else f"//{matched_at}")
                if parse.path and parse.path != "/" and parse.path not in paths:
                    paths.append(parse.path)
                # Fall back to the port embedded in the matched URL
                if not _port_number:
                    _port_number = parse.port
            if _port_number:
                # Guard against malformed port values so a bad entry doesn't abort the scan
                try:
                    port_number = int(_port_number)
                except (TypeError, ValueError):
                    port_number = None
                if port_number:
                    # Reuse the Port finding already created for this number in this scan
                    if port_number not in ports:
                        ports[port_number] = self.create_finding(Port, port=port_number)
                    port = ports[port_number]
            # Extract matcher information from Nuclei results
            # Matcher provides specific details about what triggered the template
            matcher = None
            if item.get("extracted-results", []):
                result = item.get("extracted-results", [])[0]
                # Skip generic "security" results, use specific extracted data as matcher
                if result not in ["security"]:
                    matcher = result
            elif item.get("matcher-name"):
                matcher = item.get("matcher-name")
            # Extract template metadata for finding classification
            info = item.get("info", {})
            name = info.get("name")
            description = info.get("description")
            reference = info.get("reference", [])
            tags = info.get("tags", []) or []
            # Classify findings based on Nuclei template tags
            # Different tags indicate different types of security findings
            if "tech" in tags:
                # Technology detection templates - create Technology findings
                tech_name = matcher or name
                version = None
                if matcher and item.get("extractor-name") == "version":
                    version = matcher
                    tech_name = name
                self.create_finding(
                    Technology,
                    **({"port": port, "linked_finding": True} if port else {}),
                    # Drop trailing detection descriptors so the technology name stays clean
                    name=re.split(r"\s+(?:End-of-Life|Detection|Detect|Version)\b", tech_name)[0].strip() or tech_name,
                    version=version,
                    description=description.strip() if description else (name if matcher else None),
                    reference=reference[0] if reference else None,
                )
            elif "default-login" in tags and item.get("meta"):
                # Default credential detection templates - create Credential findings
                self.create_finding(
                    Credential,
                    username=item.get("meta", {}).get("username"),
                    secret=item.get("meta", {}).get("password"),
                    context=matcher or name,
                )
            else:
                # All other templates are treated as vulnerability findings
                # Extract security classification data (severity, CVE, CWE)
                severity = info.get("severity")
                classification = info.get("classification", {})
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
                    for cve_value in cve:
                        attributes["cve"] = cve_value.upper()
                        self.create_finding(Vulnerability, **attributes)
                else:
                    attributes["cve"] = cve.upper() if cve else None
                    self.create_finding(Vulnerability, **attributes)
        # Create identified paths
        for path in paths:
            self.create_finding(Path, path=Path.clean_path(path), type=PathType.ENDPOINT)
