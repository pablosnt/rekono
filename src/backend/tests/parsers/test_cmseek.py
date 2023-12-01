from findings.enums import PathType, Severity
from findings.models import Credential, Path, Technology, Vulnerability
from tests.cases import ToolTestCase
from tests.framework import ToolTest


class CmseekTest(ToolTest):
    tool_name = "CMSeeK"
    cases = [
        ToolTestCase(
            "dvwp.json",
            [
                {
                    "model": Technology,
                    "name": "WordPress",
                    "version": "5.3",
                    "description": "CMS",
                    "reference": "https://wordpress.org",
                },
                {"model": Path, "path": "/license.txt", "type": PathType.ENDPOINT},
                {
                    "model": Technology,
                    "name": "social-warfare",
                    "version": "3.5.2",
                    "description": "WordPress plugins",
                },
                {
                    "model": Technology,
                    "name": "wp-file-upload",
                    "version": "5.3",
                    "description": "WordPress plugins",
                },
                {
                    "model": Technology,
                    "name": "wp-advanced-search",
                    "version": "1.0",
                    "description": "WordPress plugins",
                },
                {"model": Path, "path": "/readme.html", "type": PathType.ENDPOINT},
                {
                    "model": Technology,
                    "name": "twentytwenty",
                    "version": "1.0",
                    "description": "WordPress themes",
                },
            ],
        ),
        ToolTestCase(
            "joomla.json",
            [
                {
                    "model": Technology,
                    "name": "joomla",
                    "version": "1.0",
                    "description": "CMS",
                    "reference": "https://joomla.org",
                },
                {"model": Path, "path": "/demo/2.back", "type": PathType.ENDPOINT},
                {"model": Path, "path": "/demo/2.save", "type": PathType.ENDPOINT},
                {"model": Path, "path": "/demo/2.tmp", "type": PathType.ENDPOINT},
                {"model": Path, "path": "/demo/2.backup", "type": PathType.ENDPOINT},
                {"model": Path, "path": "/demo/2.txt", "type": PathType.ENDPOINT},
                {
                    "model": Vulnerability,
                    "name": "Backup files found",
                    "description": "/demo/2.back, /demo/2.save, /demo/2.tmp, /demo/2.backup, /demo/2.txt",
                    "severity": Severity.HIGH,
                    "cwe": "CWE-530",
                },
                {
                    "model": Vulnerability,
                    "name": "Debug mode enabled",
                    "description": "joomla debug mode enabled",
                    "severity": Severity.LOW,
                    "cwe": "CWE-489",
                },
            ],
        ),
        ToolTestCase(
            "vwp.json",
            [
                {
                    "model": Technology,
                    "name": "WordPress",
                    "version": "4.8.3",
                    "description": "CMS",
                    "reference": "https://wordpress.org",
                },
                {"model": Path, "path": "/license.txt", "type": PathType.ENDPOINT},
                {
                    "model": Technology,
                    "name": "wp-advanced-search",
                    "version": "1.0",
                    "description": "WordPress plugins",
                },
                {
                    "model": Technology,
                    "name": "social-warfare",
                    "version": "3.5.2",
                    "description": "WordPress plugins",
                },
                {
                    "model": Technology,
                    "name": "simple-file-list",
                    "version": "5",
                    "description": "WordPress plugins",
                },
                {
                    "model": Technology,
                    "name": "wp-file-upload",
                    "version": "4.8.3",
                    "description": "WordPress plugins",
                },
                {"model": Path, "path": "/readme.html", "type": PathType.ENDPOINT},
                {
                    "model": Technology,
                    "name": "twentyseventeen",
                    "version": "4.8.3",
                    "description": "WordPress themes",
                },
                {"model": Vulnerability, "cve": "CVE-2019-16223"},
                {"model": Vulnerability, "cve": "CVE-2019-16222"},
                {"model": Vulnerability, "cve": "CVE-2019-16221"},
                {"model": Vulnerability, "cve": "CVE-2019-16220"},
                {"model": Vulnerability, "cve": "CVE-2019-16219"},
                {"model": Vulnerability, "cve": "CVE-2019-16218"},
                {"model": Vulnerability, "cve": "CVE-2019-16217"},
                {"model": Vulnerability, "cve": "CVE-2019-9787"},
                {"model": Vulnerability, "cve": "CVE-2019-8942"},
                {"model": Vulnerability, "cve": "CVE-2018-20153"},
                {"model": Vulnerability, "cve": "CVE-2018-20152"},
                {"model": Vulnerability, "cve": "CVE-2018-20151"},
                {"model": Vulnerability, "cve": "CVE-2018-20150"},
                {"model": Vulnerability, "cve": "CVE-2018-20149"},
                {"model": Vulnerability, "cve": "CVE-2018-20148"},
                {"model": Vulnerability, "cve": "CVE-2018-20147"},
                {"model": Vulnerability, "cve": "CVE-2018-12895"},
                {"model": Vulnerability, "cve": "CVE-2017-1000600"},
            ],
        ),
        ToolTestCase(
            "wordpress.json",
            [
                {
                    "model": Technology,
                    "name": "WordPress",
                    "version": "5.8.3",
                    "description": "CMS",
                    "reference": "https://wordpress.org",
                },
                {"model": Path, "path": "/license.txt", "type": PathType.ENDPOINT},
                {
                    "model": Technology,
                    "name": "orbisius-simple-notice",
                    "version": "1.0",
                    "description": "WordPress plugins",
                },
                {
                    "model": Technology,
                    "name": "qs_site_app",
                    "version": "1642244787",
                    "description": "WordPress plugins",
                },
                {
                    "model": Technology,
                    "name": "monarch",
                    "version": "1.4.14",
                    "description": "WordPress plugins",
                },
                {"model": Path, "path": "/readme.html", "type": PathType.ENDPOINT},
                {
                    "model": Technology,
                    "name": "primer",
                    "version": "1590756562",
                    "description": "WordPress themes",
                },
                {
                    "model": Technology,
                    "name": "qs-on-primer",
                    "version": "1617278312",
                    "description": "WordPress themes",
                },
                {"model": Credential, "username": "wpdemohelper1"},
                {"model": Credential, "username": "superadmin"},
                {"model": Credential, "username": "wpdemo"},
            ],
        ),
    ]
