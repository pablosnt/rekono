"""Parser of the CMSeek CMS scanner."""

from urllib.parse import urlparse

from findings.enums import PathType, Severity
from findings.models import Credential, Path, Technology, Vulnerability
from tools.parsers.base import BaseParser


class Cmseek(BaseParser):
    """Findings discovered by CMSeek, read from its JSON report."""

    def _parse(self) -> None:
        """Create the CMS found and everything discovered in it.

        Every CMS that CMSeek supports writes its own fields in the report, named
        after the CMS itself, so the fields are recognized by what their name
        contains instead of by their exact name.
        """
        data = self.load_json_report()
        if not data or not isinstance(data, dict) or not data.get("cms_name") or not data.get("cms_id"):
            return
        # The version field is prefixed with cms_id for some CMS modules (e.g. "wp_version")
        # and with cms_name for others (e.g. "joomla_version" when cms_id is "joom")
        version = data.get(f"{data.get('cms_id')}_version") or data.get(f"{data.get('cms_name')}_version")
        base_url = data.get("url", "")
        parser = urlparse(base_url)
        if parser.path:
            # CMSeek's url can include a sub-path (e.g. a demo folder); strip it so base_url is
            # the host root, matching the full paths reported for the other fields below
            base_url = base_url.replace(parser.path, "/")
        cms = self.create_finding(
            Technology,
            name=data.get("cms_name", "").strip(),
            version=version.strip() if version is not None else None,
            description="CMS",
            reference=(data.get("cms_url", "").strip() if data.get("cms_url") else None),
        )
        if not cms:
            return
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
            # Fields hold their values as a list, a comma-separated string, or a single string
            # depending on the CMS module, so all three shapes are normalized into a list here.
            # Dict-valued fields, like the *_vulns block handled further below, never match
            # base_url and are filtered out here, leaving them to the "_vulns" branch instead
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
                        self.create_finding(Path, path=Path.clean_path(path.replace("//", "/")), type=PathType.ENDPOINT)
                for search_key, vulnerability_name, severity, cwe in [
                    # CWE-530: Exposure of Backup File to an Unauthorized Control Sphere
                    ("backup_file", "Backup files found", Severity.HIGH, "CWE-530"),
                    # CWE-497: Exposure of Sensitive System Information to an Unauthorized Control Sphere
                    ("config_file", "Configuration files found", Severity.MEDIUM, "CWE-497"),
                ]:
                    if search_key in key:
                        self.create_finding(
                            Vulnerability,
                            linked_finding=True,
                            technology=cms,
                            name=vulnerability_name,
                            description=", ".join(paths),
                            severity=severity,
                            cwes=[cwe],
                        )
            elif "_users" in key and value != "disabled":
                # CMSeek reports this field as the literal string "disabled" when there is
                # nothing to list, otherwise as a comma-separated string of usernames
                for user in value.split(","):
                    if user:
                        self.create_finding(
                            Credential,
                            linked_finding=True,
                            technology=cms,
                            username=user.strip(),
                            context=f"{cms.name} username",
                        )
            elif "_debug_mode" in key and value != "disabled":
                # CMSeek reports this field as "enabled" or "disabled"; any other value is
                # still treated as debug mode being on rather than assuming it means disabled
                self.create_finding(
                    Vulnerability,
                    linked_finding=True,
                    technology=cms,
                    name="Debug mode enabled",
                    description=f"{cms.name} debug mode enabled",
                    severity=Severity.LOW,
                    cwes=["CWE-489"],  # CWE-489: Active Debug Code
                )
            elif "_vulns" in key and "vulnerabilities" in value:
                for vulnerability in value["vulnerabilities"]:
                    base_score = vulnerability.get("cvss_score")
                    fixed_version = vulnerability.get("fixed_in")
                    self.create_finding(
                        Vulnerability,
                        linked_finding=True,
                        technology=cms,
                        name=vulnerability.get("type", "").strip(),
                        description=vulnerability.get("name", "").strip(),
                        # cve can be absent on some entries, so it is only read once its
                        # presence is confirmed rather than risking an exception here that
                        # would abandon the rest of this loop, see BaseParser._parse
                        cve=vulnerability.get("cve").strip() if vulnerability.get("cve") is not None else None,
                        cvss_base_score=float(base_score) if base_score else None,
                        # CMSeek uses the literal "N/A" as a sentinel for "no fixed version known"
                        remediation=f"Update {cms.name} to version {fixed_version}"
                        if fixed_version and fixed_version != "N/A"
                        else None,
                    )
            elif "Version" in value and "," in value:
                # Any field whose value looks like a "<name> Version <version>," list (plugins,
                # themes, etc.) is parsed generically here, regardless of the key name
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
