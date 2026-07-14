from functools import cached_property

from django.template.loader import get_template
from django.test import TestCase

from findings.enums import OSINTDataType, Severity
from findings.models import OSINT, Credential, Exploit, Host, Port, Technology, Vulnerability
from projects.models import Project
from rekono.settings import CONFIG
from reporting.enums import FindingName, ReportFormat, ReportStatus
from reporting.models import Report
from security.authorization.roles import Role
from targets.enums import TargetType
from targets.models import Target
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types,attribute-error


class ReportingTest(ApiTest):
    endpoint = "/api/reports/"
    format = None
    only_true_positives = False
    finding_types: list[str] | None = [name.value for name in FindingName]

    def test_cases(self) -> None:
        if self.format:
            report = {"format": self.format.value, "only_true_positives": self.only_true_positives}
            if self.finding_types:
                report["finding_types"] = self.finding_types
            self.cases = [
                ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
                PostApiTestCase(["not_members"], 403, {**report, "project": 1}),
                PostApiTestCase(["not_members"], 403, {**report, "target": 1}),
                PostApiTestCase(["not_members"], 403, {**report, "task": 1}),
                PostApiTestCase(["members"], 400, report),
                PostApiTestCase(
                    ["admin1"],
                    data={**report, "project": 1},
                    expected={
                        "id": 1,
                        "project": 1,
                        "task": None,
                        "target": None,
                        "format": self.format.value,
                        "user": 1,
                    },
                ),
                PostApiTestCase(
                    ["auditor1"],
                    data={**report, "task": 1},
                    expected={
                        "id": 2,
                        "project": None,
                        "task": 1,
                        "target": None,
                        "format": self.format.value,
                        "user": 3,
                    },
                ),
                PostApiTestCase(
                    ["reader1"],
                    data={**report, "target": 1},
                    expected={
                        "id": 3,
                        "project": None,
                        "task": None,
                        "target": 1,
                        "format": self.format.value,
                        "user": 5,
                    },
                ),
                DeleteApiTestCase(["admin1"], 400, endpoint="1/"),
                DeleteApiTestCase(["admin1"], 400, endpoint="2/"),
                DeleteApiTestCase(["admin1"], 400, endpoint="3/"),
                ApiTestCase(["not_members"], 404, endpoint="1"),
                ApiTestCase(["not_members"], 404, endpoint="2"),
                ApiTestCase(["not_members"], 404, endpoint="3"),
                ApiTestCase(["not_members"]),
                ApiTestCase(
                    ["members"],
                    expected={
                        "id": 1,
                        "project": {"id": 1},
                        "task": None,
                        "target": None,
                        "format": self.format.value,
                        "user": {"id": 1, "username": "admin1"},
                    },
                    endpoint="1",
                ),
                ApiTestCase(
                    ["members"],
                    expected={
                        "id": 2,
                        "project": None,
                        "task": {"id": 1, "target": {"id": 1}},
                        "target": None,
                        "format": self.format.value,
                        "user": {"id": 3, "username": "auditor1"},
                    },
                    endpoint="2",
                ),
                ApiTestCase(
                    ["members"],
                    expected={
                        "id": 3,
                        "project": None,
                        "task": None,
                        "target": {"id": 1},
                        "format": self.format.value,
                        "user": {"id": 5, "username": "reader1"},
                    },
                    endpoint="3",
                ),
                ApiTestCase(
                    ["members"],
                    expected=[
                        {
                            "id": 3,
                            "project": None,
                            "task": None,
                            "target": {"id": 1},
                            "format": self.format.value,
                            "user": {"id": 5, "username": "reader1"},
                        },
                        {
                            "id": 2,
                            "project": None,
                            "task": {"id": 1, "target": {"id": 1}},
                            "target": None,
                            "format": self.format.value,
                            "user": {"id": 3, "username": "auditor1"},
                        },
                        {
                            "id": 1,
                            "project": {"id": 1},
                            "task": None,
                            "target": None,
                            "format": self.format.value,
                            "user": {"id": 1, "username": "admin1"},
                        },
                    ],
                ),
                # Downloads return a 400 error because reports are created within a thread execution and having two
                # threads working on the same tables at the same time is not compatible with SQLite, so the reports are
                # still PENDING
                ApiTestCase(["members"], 400, endpoint="1/download"),
                ApiTestCase(["not_members"], 404, endpoint="1/download"),
                ApiTestCase(["members"], 400, endpoint="2/download"),
                ApiTestCase(["not_members"], 404, endpoint="2/download"),
                ApiTestCase(["members"], 400, endpoint="3/download"),
                ApiTestCase(["not_members"], 404, endpoint="3/download"),
            ]
            super().test_cases()
            # Mark reports as not-PENDING so they can be downloaded and deleted
            Report.objects.update(status=ReportStatus.READY)
            self.cases = [
                # Downloads return a 404 error because their status is READY but the files don't exist on disk
                ApiTestCase(["members", "not_members"], 404, endpoint="1/download"),
                ApiTestCase(["members", "not_members"], 404, endpoint="2/download"),
                ApiTestCase(["members", "not_members"], 404, endpoint="3/download"),
                DeleteApiTestCase(["auditor2", "reader2"], 404, endpoint="1"),
                DeleteApiTestCase(["auditor1", "reader1"], 403, endpoint="1"),
                DeleteApiTestCase(["admin1"], endpoint="1"),
                DeleteApiTestCase(["admin1"], endpoint="2"),
                DeleteApiTestCase(["reader1"], endpoint="3"),
                ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 404, endpoint="1"),
                ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 404, endpoint="2"),
                ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 404, endpoint="3"),
                ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
            ]
            super().test_cases()

    def test_string(self) -> None:
        if self.format:
            self.expected_string = f"{self.project.name} - {self.format.value} - {self.admin1.email}"
            super().test_string()

    @cached_property
    def object(self) -> Report:
        return Report(format=self.format, project=self.project, user=self.admin1)


class JsonReportTest(ReportingTest, TestCase):
    format = ReportFormat.JSON


class JsonReportTruePositivesTest(ReportingTest, TestCase):
    format = ReportFormat.JSON
    only_true_positives = False


class XmlReportTest(ReportingTest, TestCase):
    format = ReportFormat.XML


class XmlReportTruePositivesTest(ReportingTest, TestCase):
    format = ReportFormat.XML
    only_true_positives = False


class PdfReportTest(ReportingTest, TestCase):
    format = ReportFormat.PDF
    finding_types = None

    def setup_testing_data(self) -> None:
        super().setup_testing_data()
        Target.objects.create(project=self.project, target="10.10.10.15", type=TargetType.PRIVATE_IP)


class PdfReportWithFindingTypesTest(PdfReportTest):
    # PDF reports ignore the requested finding types, but providing them must not break report creation
    finding_types: list[str] | None = [name.value for name in FindingName]


class PdfReportTemplateRenderingTest(ApiTest, TestCase):
    data = [
        SetupProject(
            osint_fields=[
                {"data": "osint.example.com", "data_type": OSINTDataType.DOMAIN},
                {
                    "data": "http://scanme.example.org/index.php/option/com_fields/view/fields/layout/modal/list/fullordering/updatexml/concat/user/verylongunbrokensegmenttoforcewrapping",
                    "data_type": OSINTDataType.URL,
                },
            ],
            hosts_fields=[
                {
                    "os": "Ubuntu 22.04 LTS",
                    "domain": "host.example.com",
                    "country": "Germany",
                    "city": "Berlin",
                    "reputation": -13,
                    "malicious_analysis": 0,
                    "suspicious_analysis": 3,
                    "total_analysis": 70,
                }
            ],
            credentials_fields=[
                {"secret": "TopSecretValue", "username": "secretuser"},
                {"secret": None, "username": "plainuser"},
            ],
            vulnerabilities_fields=[
                {
                    "severity": Severity.CRITICAL,
                    "description": "Line one\nLine two",
                    "euvd_id": "EUVD-2025-0001",
                    "ghsa_id": "GHSA-aaaa-bbbb-cccc",
                    "osv_generic_id": "OSV-2025-0001",
                    "cvss_version": "4.0",
                    "cvss_vector": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N",
                    "cvss_base_score": 9.8,
                    "cwes": ["CWE-79", "CWE-89"],
                    "epss_score": 0.94215,
                    "epss_percentile": 0.99011,
                    "remediation": "Patch now.\nUpgrade to latest.",
                    "trending": True,
                },
                {"severity": Severity.HIGH},
                {"severity": Severity.MEDIUM},
                {"severity": Severity.LOW},
                {"severity": Severity.INFO},
            ],
            exploits_fields=[
                {
                    "title": "Exploit Database entry",
                    "edb_id": 12345,
                    "reference": "https://www.exploit-db.com/exploits/12345",
                },
                {"title": "Public proof of concept", "edb_id": None, "reference": "https://github.com/poc"},
                {
                    "title": "Metasploit module",
                    "edb_id": None,
                    "reference": "exploit/multi/http/wp_admin_shell_upload",
                },
            ],
        )
    ]

    def test_pdf_template_renders_all_findings_and_stats_chart(self) -> None:
        project = Project.objects.first()
        target = project.targets.first()
        host = Host.objects.first()
        osint = OSINT.objects.filter(executions__task__target=target).distinct()
        ports = Port.objects.filter(host=host)
        technologies = Technology.objects.filter(port__host=host)
        credentials = Credential.objects.filter(technology__port__host=host)
        vulnerabilities = Vulnerability.objects.filter(technology__port__host=host).order_by("-severity")
        exploits = Exploit.objects.filter(vulnerability__technology__port__host=host)
        findings = {
            target.id: {
                FindingName.OSINT.value: osint,
                FindingName.HOST.value: [
                    {
                        FindingName.HOST.value: host,
                        FindingName.PORT.value: ports,
                        FindingName.TECHNOLOGY.value: technologies,
                        FindingName.CREDENTIAL.value: credentials,
                        FindingName.VULNERABILITY.value: vulnerabilities,
                        FindingName.EXPLOIT.value: exploits,
                    }
                ],
            }
        }
        # Compute stats
        stats = {severity.name.lower(): 0 for severity in Severity}
        for vulnerability in vulnerabilities:
            stats[Severity(vulnerability.severity).name.lower()] += 1
        for credential in credentials:
            stats[(Severity.HIGH if credential.secret else Severity.LOW).name.lower()] += 1
        html = get_template(CONFIG.pdf_report_template).render(
            {
                "project": project,
                "targets": [target],
                "findings": findings,
                "stats_by_target": {target.id: stats},
                "stats": stats,
            }
        )

        # Project header
        self.assertIn(project.name, html)

        # OSINT
        for finding in osint:
            self.assertIn(finding.data, html)

        # Host
        self.assertIn(host.ip, html)
        self.assertIn("Ubuntu 22.04 LTS", html)
        self.assertNotIn(f"[{host.os_type}]", html)
        self.assertIn("host.example.com", html)
        self.assertIn("Germany", html)
        self.assertIn("Berlin", html)
        self.assertIn("-13", html)
        self.assertIn("0/70", html)
        self.assertIn("3/70", html)

        # Ports
        for port in ports:
            self.assertIn(str(port.port), html)

        # Technologies
        for technology in technologies:
            self.assertIn(technology.name, html)

        # Credentials, both the secret and the non-secret rendering branches
        for credential in credentials:
            self.assertIn(credential.username, html)
        self.assertIn("Credential found", html)
        self.assertIn("User found", html)

        # Vulnerabilities
        for vulnerability in vulnerabilities:
            self.assertIn(vulnerability.name, html)
            self.assertIn(vulnerability.description.replace("\n", "<br>"), html)
            for value in [
                vulnerability.remediation,
                vulnerability.cve,
                vulnerability.euvd_id,
                vulnerability.ghsa_id,
                vulnerability.osv_generic_id,
                vulnerability.cvss_base_score,
                vulnerability.cvss_vector,
                vulnerability.epss_score,
                vulnerability.epss_percentile,
            ]:
                if value:
                    self.assertIn(str(value).replace("\n", "<br>"), html)
            for cwe in vulnerability.cwes:
                self.assertIn(f'href="https://cwe.mitre.org/data/definitions/{cwe.replace("CWE-", "")}.html"', html)
            if vulnerability.trending:
                self.assertIn("Trending on CVECrowd", html)
            
        # Exploits
        for exploit in exploits:
            if exploit.edb_id:
                self.assertIn(
                    f'<a href="https://www.exploit-db.com/exploits/{exploit.edb_id}">EDB-{exploit.edb_id}</a>', html
                )
            elif exploit.reference.startswith("http"):
                self.assertIn(f'<a href="{exploit.reference}">{exploit.title}</a>', html)
            else:
                self.assertIn(exploit.reference, html)
                self.assertNotIn(f'href="{exploit.reference}"', html)

        # Stats chart with the severity counts
        self.assertIn('<canvas type="graph"', html)
        self.assertIn('"title": {"_text": "Vulnerabilities by Severity"', html)
        self.assertIn(
            f'"data": [[{stats["critical"]}, {stats["high"]}, {stats["medium"]}, {stats["low"]}, {stats["info"]}]]',
            html,
        )


class PdfReportWithoutFindingsTest(ApiTest, TestCase):
    endpoint = "/api/reports/"
    data = [SetupProject(executions_per_task=0)]
    cases = [
        PostApiTestCase(
            ["members"],
            404,
            data={"format": ReportFormat.PDF.value, "only_true_positives": True, "project": 1},
        )
    ]
