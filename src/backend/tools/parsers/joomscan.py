from urllib.parse import urlparse

from findings.enums import PathType, Severity
from findings.models import Exploit, Path, Technology, Vulnerability
from tools.parsers.base import BaseParser


class Joomscan(BaseParser):
    def _parse_standard_output(self) -> None:
        technology = None
        vulnerability_name = None
        endpoints = set(["/"])
        backups = set()
        configurations = set()
        path_disclosure = set()
        directory_listing = set()
        host = urlparse(
            self.executor.arguments[self.executor.arguments.index("-u") + 1]
        ).hostname
        lines = self.output.split("\n")
        for index, line in enumerate(lines):
            data = line.strip()
            if not data:
                continue
            if (
                "[++] Joomla" in data
                and lines[index - 1] == "[+] Detecting Joomla Version"
            ):
                version = data.replace("[++] Joomla ", "").strip()
                technology = self.create_finding(
                    Technology,
                    name="Joomla",
                    version=version,
                    description=f"Joomla {version}",
                    reference="https://www.joomla.org/",
                )
            elif "CVE : " in data:
                vulnerability_name = (
                    lines[index - 1].replace("[++]", "").replace("Joomla!", "").strip()
                )
                for cve in data.replace("CVE : ", "").strip().split(","):
                    self.create_finding(
                        Vulnerability,
                        technology=technology,
                        name=vulnerability_name,
                        cve=cve.strip(),
                    )
            elif "EDB : " in data:
                link = data.replace("EDB : ", "").strip()
                self.create_finding(
                    Exploit,
                    technology=technology,
                    title=vulnerability_name,
                    edb_id=int(
                        link.split("https://www.exploit-db.com/exploits/", 1)[
                            1
                        ].replace("/", "")
                    ),
                    reference=link,
                )
            elif "Debug mode Enabled" in data:
                self.create_finding(
                    Vulnerability,
                    technology=technology,
                    name="Debug mode enabled",
                    description="Joomla debug mode enabled",
                    severity=Severity.LOW,
                    cwe="CWE-489",  # CWE-489: Active Debug Code
                )

            elif host in data:
                endpoint = data.split(host, 1)[1].split(" ", 1)[0]
                if endpoint and endpoint not in endpoints:
                    endpoints.add(endpoint)
                    for search, list in [
                        ("Path :", backups),
                        ("config file path :", configurations),
                        ("Full Path Disclosure (FPD) in", path_disclosure),
                        ("directory has directory listing :", directory_listing),
                    ]:
                        if search in data:
                            list.add(endpoint)
                    self.create_finding(Path, path=endpoint, type=PathType.ENDPOINT)
        for name, paths, severity, cwe in [
            # CWE-530: Exposure of Backup File to an Unauthorized Control Sphere
            ("Backup files found", backups, Severity.HIGH, "CWE-530"),
            # CWE-497: Exposure of Sensitive System Information to an Unauthorized Control Sphere
            ("Configuration files found", configurations, Severity.MEDIUM, "CWE-497"),
            # CWE-497: Exposure of Sensitive System Information to an Unauthorized Control Sphere
            ("Full path disclosure", path_disclosure, Severity.LOW, "CWE-497"),
            # CWE-548: Exposure of Information Through Directory Listing
            ("Directory listing", directory_listing, Severity.LOW, "CWE-548"),
        ]:
            if paths:
                self.create_finding(
                    Vulnerability,
                    technology=technology,
                    name=name,
                    description=", ".join(paths),
                    severity=severity,
                    cwe=cwe,
                )
