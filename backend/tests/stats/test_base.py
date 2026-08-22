from findings.enums import HostOS, Severity, TransportProtocol, TriageStatus
from projects.models import Project
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types


class BaseStatsAuthorizationTest(ApiTest):
    data = [
        SetupProject(
            osint_fields=[{"triage_status": TriageStatus.TRUE_POSITIVE}],
            hosts_fields=[{"os_type": HostOS.LINUX}],
            ports_fields=[{"port": 80, "service": "http", "protocol": TransportProtocol.TCP}],
            paths_fields=[{}],
            technologies_fields=[{"name": "WordPress"}],
            credentials_fields=[{}],
            vulnerabilities_fields=[
                {
                    "severity": Severity.CRITICAL,
                    "cve": "CVE-2025-1001",
                    "cwes": ["CWE-79"],
                    "triage_status": TriageStatus.TRUE_POSITIVE,
                }
            ],
            exploits_fields=[{}],
        ),
        SetupProject(
            osint_fields=[{"triage_status": TriageStatus.WONT_FIX}],
            hosts_fields=[{"os_type": HostOS.WINDOWS}],
            ports_fields=[{"port": 443, "service": "https", "protocol": TransportProtocol.TCP}],
            paths_fields=[{}],
            technologies_fields=[{"name": "Nginx"}],
            credentials_fields=[{"triage_status": TriageStatus.WONT_FIX}],
            vulnerabilities_fields=[
                {
                    "severity": Severity.LOW,
                    "cve": "CVE-2025-2002",
                    "cwes": ["CWE-22"],
                    "triage_status": TriageStatus.TRUE_POSITIVE,
                }
            ],
            exploits_fields=[{"triage_status": TriageStatus.WONT_FIX}],
        ),
    ]
    project_1_members_expected: list[dict] = []
    project_2_members_expected: list[dict] = []

    def setUp(self) -> None:
        super().setUp()
        # Project 2 is only accessible by the users that aren't members of project 1
        Project.objects.get(pk=2).members.set(self.not_members)

    @property
    def cases(self) -> list[ApiTestCase]:
        """Build the test cases from the stats expected for the members of each project."""
        return [
            ApiTestCase(["members"], expected=self.project_1_members_expected),
            ApiTestCase(["not_members"], expected=self.project_2_members_expected),
        ]
