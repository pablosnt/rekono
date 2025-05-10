from urllib.parse import urlparse

from findings.enums import PathType, Severity
from findings.models import Credential, Path, Technology, Vulnerability
from tools.parsers.base import BaseParser


class Cmseek(BaseParser):
    def _parse_report(self) -> None:
        data = self._load_report_as_json()
        if not data.get("cms_name") or not data.get("cms_id"):
            return
        version = data.get(f"{data.get('cms_id')}_version") or data.get(f"{data.get('cms_name')}_version")
        base_url = data.get("url", "")
        parser = urlparse(base_url)
        if parser.path:
            base_url = base_url.replace(parser.path, "/")
        cms = self.create_finding(
            Technology,
            name=data.get("cms_name").strip(),
            version=version.strip() if version is not None else None,
            description="CMS",
            reference=(data.get("cms_url", "").strip() if data.get("cms_url") else data.get("cms_url")),
        )
        for key, value in data.items():
            if key in [
                "cms_id",
                "cms_name",
                "cms_url",
                f"{data.get('cms_id')}_version",
                f"{data.get('cms_name')}_version",
                "url",
            ]:
                continue
            paths = [
                path.replace(base_url, "/").strip()
                for path in (
                    value
                    if isinstance(value, list)
                    else (value.split(",") if isinstance(value, str) and "," in value else [value])
                )
                if base_url in path
            ]
            if paths:
                for path in paths:
                    if path and path != "/":
                        self.create_finding(
                            Path,
                            path=path.replace("//", "/"),
                            type=PathType.ENDPOINT,
                        )
                for search_key, vulnerability_name, severity, cwe in [
                    # CWE-530: Exposure of Backup File to an Unauthorized Control Sphere
                    ("backup_file", "Backup files found", Severity.HIGH, "CWE-530"),
                    # CWE-497: Exposure of Sensitive System Information to an Unauthorized Control Sphere
                    (
                        "config_file",
                        "Configuration files found",
                        Severity.MEDIUM,
                        "CWE-497",
                    ),
                ]:
                    if search_key in key:
                        self.create_finding(
                            Vulnerability,
                            technology=cms,
                            name=vulnerability_name,
                            description=", ".join(paths),
                            severity=severity,
                            cwe=cwe,
                        )
            elif "_users" in key and value != "disabled":
                for user in value.split(","):
                    if user:
                        self.create_finding(
                            Credential,
                            technology=cms,
                            username=user.strip(),
                            context=f"{cms.name} username",
                        )
            elif "_debug_mode" in key and value != "disabled":
                self.create_finding(
                    Vulnerability,
                    technology=cms,
                    name="Debug mode enabled",
                    description=f"{cms.name} debug mode enabled",
                    severity=Severity.LOW,
                    cwe="CWE-489",  # CWE-489: Active Debug Code
                )
            elif "_vulns" in key and "vulnerabilities" in value:
                for vulnerability in value["vulnerabilities"]:
                    self.create_finding(
                        Vulnerability,
                        technology=cms,
                        name=vulnerability.get("name", "").strip(),
                        cve=(vulnerability.get("cve").strip() if vulnerability.get("cve") is not None else None),
                    )
            elif "Version" in value and "," in value:
                for component in value.split(","):
                    technology = component
                    version = None
                    if "Version" in component:
                        technology, version = component.split("Version", 1)
                    name = key.replace(f"{data.get('cms_name')}_", "").replace(f"{data.get('cms_id')}_", "")
                    if technology:
                        self.create_finding(
                            Technology,
                            name=technology.strip(),
                            version=version.strip() if version is not None else None,
                            description=f"{cms.name} {name}",
                        )
