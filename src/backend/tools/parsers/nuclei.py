"""Nuclei vulnerability scanner output parser.

Processes Nuclei JSON output to extract vulnerabilities, technology fingerprints,
and credential findings from web application security scans.
"""

import json
from typing import cast
from urllib.parse import urlparse

from findings.enums import PathType, Severity
from findings.models import Credential, Path, Technology, Vulnerability
from tools.parsers.base import BaseParser


class Nuclei(BaseParser):
    """Parser for Nuclei JSON output files.

    Extracts vulnerability findings, technology detections, and exposed credentials
    from Nuclei template-based security scans. Handles multiple finding types based
    on template tags and metadata.

    Attributes:
        Inherits all attributes from BaseParser
    """

    def _parse(self) -> None:
        """Parse Nuclei JSON output and extract security findings.

        Processes line-delimited JSON output to create Vulnerability, Technology,
        and Credential findings based on template tags and extracted results.
        """
        # Parse each line of the JSON output as a separate finding
        data = [json.loads(line) for line in self.load_report_by_lines()]
        paths = []
        for item in data:
            # Save the path where the Nuclei alert was triggered
            matched_at = item.get("matched-at")
            if matched_at and "://" in matched_at:
                parse = urlparse(item.get("matched-at"))
                if parse.path and parse.path != "/" and parse.path not in paths:
                    paths.append(parse.path)
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
                self.create_finding(
                    Technology,
                    name=matcher or name,
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
                self.create_finding(
                    Vulnerability,
                    name=(f"{name}: {matcher}" if matcher else name).strip(),
                    description=description.strip() if description else None,
                    severity=(cast(dict[str, str], Severity)[severity.upper()] if severity else Severity.INFO),
                    cvss_vector=classification.get("cvss-metrics"),
                    cve=cve.upper() if cve else None,
                    cwe=cwe[0].upper() if cwe else None,
                    remediation=remediation.strip() if remediation else None,
                    reference=reference[0] if reference else None,
                )
        # Create identified paths
        for path in paths:
            # TODO: Update unit tests
            self.create_finding(Path, path=path, type=PathType.ENDPOINT)
