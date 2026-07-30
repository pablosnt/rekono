"""JoomScan Joomla CMS vulnerability scanner output parser.

Processes JoomScan plain text output to extract Joomla technology fingerprints,
vulnerabilities, exploits, and security findings from Joomla CMS scans.
"""

from urllib.parse import urlparse

from findings.enums import PathType, Severity
from findings.models import Exploit, Path, Technology, Vulnerability
from tools.parsers.base import BaseParser


class Joomscan(BaseParser):
    """Parser for JoomScan plain text output.

    Extracts Joomla CMS security findings including version detection, CVE
    vulnerabilities, exploit references, configuration issues, and discovered
    endpoints from comprehensive Joomla security scans.

    Attributes:
        Inherits all attributes from BaseParser
    """

    def _parse(self) -> None:
        """Parse JoomScan output and extract Joomla security findings.

        Processes plain text scan results to create Technology, Vulnerability,
        Exploit, and Path findings from Joomla CMS security analysis. JoomScan
        has no structured report format, so findings are recognized from fixed
        banner strings and, for some of them, by looking at the previous line.
        """
        technology = vulnerability_name = None
        # Seeded with "/" so the "Processing <url> ..." banner line at the top of the report,
        # which also matches the host substring check below, does not produce a redundant
        # root Path finding
        endpoints = set(["/"])
        backups = set()
        configurations = set()
        path_disclosure = set()
        directory_listing = set()
        host = urlparse(self.executor.arguments[self.executor.arguments.index("-u") + 1]).hostname
        lines = (self.output or "").split("\n")
        for index, line in enumerate(lines):
            data = line.strip()
            if not data:
                continue
            if "[++] Joomla" in data and lines[index - 1] == "[+] Detecting Joomla Version":
                # "[++] Joomla" also prefixes vulnerability headers like "[++] Joomla! <name>",
                # so the preceding banner line confirms this is the version detection line
                version = data.replace("[++] Joomla ", "").strip()
                technology = self.create_finding(
                    Technology,
                    name="Joomla",
                    version=version,
                    description=f"Joomla {version}",
                    reference="https://www.joomla.org/",
                )
            elif "CVE : " in data:
                # The vulnerability name is on the line right before its "CVE : " entry. The
                # first entry in a block is prefixed with "[++] Joomla!", later ones in the same
                # block are plain "Joomla! <name>" lines, so both prefixes are stripped here
                vulnerability_name = lines[index - 1].replace("[++]", "").replace("Joomla!", "").strip()
                # A single line can list several comma-separated CVE ids for the same vulnerability
                for cve in data.replace("CVE : ", "").strip().split(","):
                    self.create_finding(
                        Vulnerability,
                        linked_finding=True,
                        technology=technology,
                        name=vulnerability_name,
                        cve=cve.strip(),
                    )
            elif "EDB : " in data:
                link = data.replace("EDB : ", "").strip()
                self.create_finding(
                    Exploit,
                    linked_finding=True,
                    technology=technology,
                    title=vulnerability_name,
                    # JoomScan always emits Exploit-DB links in this exact URL form, so the
                    # numeric id is extracted by splitting on it instead of parsing the URL
                    edb_id=int(link.split("https://www.exploit-db.com/exploits/", 1)[1].replace("/", "")),
                    reference=link,
                )
            elif "Debug mode Enabled" in data:
                self.create_finding(
                    Vulnerability,
                    linked_finding=True,
                    technology=technology,
                    name="Debug mode enabled",
                    description="Joomla debug mode enabled",
                    severity=Severity.LOW,
                    cwes=["CWE-489"],  # CWE-489: Active Debug Code
                )

            elif host in data:
                # Any remaining line mentioning the host is treated as reporting an endpoint; the
                # endpoint itself is the text between the host and the next whitespace
                endpoint = data.split(host, 1)[1].split(" ", 1)[0]
                if endpoint and endpoint not in endpoints:
                    endpoints.add(endpoint)
                    for search, list in [
                        ("Path :", backups),
                        ("config file path :", configurations),
                        ("Full Path Disclosure (FPD) in", path_disclosure),
                        ("directory has directory listing :", directory_listing),
                    ]:
                        # The same line that reports the endpoint also carries one of these
                        # markers when it belongs to one of the aggregated categories below
                        if search in data:
                            list.add(endpoint)
                    self.create_finding(Path, path=Path.clean_path(endpoint), type=PathType.ENDPOINT)
        for name, paths, severity, cwe in [
            # CWE-530: Exposure of Backup File to an Unauthorized Control Sphere
            ("Backup files found", backups, Severity.HIGH, "CWE-530"),
            # CWE-497: Exposure of Sensitive System Information to an Unauthorized Control Sphere
            ("Configuration files found", configurations, Severity.MEDIUM, "CWE-497"),
            # CWE-497: Exposure of Sensitive System Information to an Unauthorized Control Sphere
            ("Full path disclosure", path_disclosure, Severity.LOW, "CWE-497"),
            # CWE-548: Exposure of Information Through Directory listing
            ("Directory listing", directory_listing, Severity.LOW, "CWE-548"),
        ]:
            if paths:
                self.create_finding(
                    Vulnerability,
                    linked_finding=True,
                    technology=technology,
                    name=name,
                    description=", ".join(paths),
                    severity=severity,
                    cwes=[cwe],
                )
