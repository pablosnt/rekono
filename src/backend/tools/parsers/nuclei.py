"""Nuclei vulnerability scanner output parser.

Processes Nuclei JSON output to extract vulnerabilities, technology fingerprints,
and credential findings from web application security scans.
"""

import json
from typing import cast

from findings.enums import Severity
from findings.models import Credential, Technology, Vulnerability
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
        data = [json.loads(line) for line in self.load_report_by_lines()]
        for item in data:
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
            reference = info.get("reference", [])
            tags = info.get("tags", []) or []
            """
            TODO: Don't lose information!

            - Paths
            - Matched at: we don't save in which path a vulnerability has been found
            - Remediation: save it in the vulnerability model and check if other tools provide that info
            """
            if "tech" in tags:
                self.create_finding(
                    Technology,
                    name=matcher or name,
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
                cve = info.get("classification", {}).get("cve-id")
                cwe = info.get("classification", {}).get("cwe-id", [])
                self.create_finding(
                    Vulnerability,
                    name=(f"{name}: {matcher}" if matcher else name).strip(),
                    description=description.strip() if description else None,
                    severity=(cast(dict[str, str], Severity)[severity.upper()] if severity else Severity.INFO),
                    cve=cve.upper() if cve else None,
                    cwe=cwe[0].upper() if cwe else None,
                    reference=reference[0] if reference else None,
                )
