from functools import cached_property

from django.test import TestCase

from findings.enums import HostOS, OSINTDataType, PortStatus, Severity, TransportProtocol, TriageStatus
from findings.framework.models import Finding
from findings.models import OSINT, Credential, Exploit, Host, Path, Port, Technology, Vulnerability
from security.authorization.roles import Role
from targets.enums import TargetType
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase, PutApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types


class FindingTest(ApiTest):
    model = Finding
    expected_defectdojo = {}
    data = [SetupProject()]
    false_positive = {"triage_status": TriageStatus.FALSE_POSITIVE.value, "triage_comment": "It isn't exploitable"}
    true_positive = {
        "triage_status": TriageStatus.TRUE_POSITIVE.value,
        "triage_comment": "Exploitation has been confirmed",
    }

    @cached_property
    def cases(self) -> list[ApiTestCase]:
        finding = self.model.objects.first()
        cases = [
            PostApiTestCase([Role.ADMIN, Role.AUDITOR], 405),
            ApiTestCase(["not_members"]),
            ApiTestCase(["members"], expected=[{"id": 1, "is_fixed": False}]),
            PostApiTestCase(["admin2", "auditor2"], 404, endpoint="1/fix/"),
            PostApiTestCase([Role.READER], 403, endpoint="1/fix/"),
            PostApiTestCase(["auditor1"], 204, endpoint="1/fix/"),
            PostApiTestCase(["admin1"], 400, endpoint="1/fix/"),
            ApiTestCase(["members"], expected=[{"id": 1, "is_fixed": True}]),
            DeleteApiTestCase(["admin2", "auditor2"], 404, endpoint="1/fix/"),
            DeleteApiTestCase([Role.READER], 403, endpoint="1/fix/"),
            DeleteApiTestCase(["admin1"], endpoint="1/fix/"),
            DeleteApiTestCase(["auditor1"], 400, endpoint="1/fix/"),
            ApiTestCase(["members"], expected=[{"id": 1, "is_fixed": False}]),
        ]
        if hasattr(finding, "triage_status"):
            cases.extend(
                [
                    ApiTestCase(["not_members"]),
                    ApiTestCase(
                        ["members"],
                        expected=[{"id": 1, "triage_status": TriageStatus.UNTRIAGED.value}],
                    ),
                    ApiTestCase(
                        ["members"],
                        expected=[{"id": 1, "triage_status": TriageStatus.UNTRIAGED.value}],
                        endpoint="{endpoint}?host=1",
                    ),
                    PutApiTestCase([Role.READER], 403, self.false_positive, endpoint="1/"),
                    PutApiTestCase(["admin2", "auditor2"], 404, self.false_positive, endpoint="1"),
                    PutApiTestCase(
                        ["admin1", "auditor1"],
                        data=self.false_positive,
                        expected={"id": 1, **self.false_positive},
                        endpoint="1",
                    ),
                    ApiTestCase(["members"], expected={"id": 1, **self.false_positive}, endpoint="1"),
                    PutApiTestCase(
                        ["admin1", "auditor1"],
                        data=self.true_positive,
                        expected={"id": 1, **self.true_positive},
                        endpoint="1",
                    ),
                    ApiTestCase(["members"], expected={"id": 1, **self.true_positive}, endpoint="1"),
                ]
            )
        return cases

    def test_defectdojo(self) -> None:
        if self.expected_defectdojo:
            finding = self.model.objects.first()
            parsed = finding.defectdojo_finding()
            for key, value in self.expected_defectdojo.items():
                self.assertEqual(value, parsed[key])

    @cached_property
    def object(self) -> Finding:
        return self.model.objects.first()


class OSINTTest(FindingTest, TestCase):
    model = OSINT
    endpoint = "/api/osint/"
    expected_defectdojo = {
        "title": f"{OSINTDataType.USER.value} found using OSINT techniques",
        "description": "Data: admin10\nSource: Google",
        "severity": Severity.MEDIUM,
    }
    expected_string = f"admin10 - {OSINTDataType.USER.value}"

    def test_cases(self):
        super().test_cases()
        self.osint1 = OSINT.objects.create(data="10.10.10.11", data_type=OSINTDataType.IP, source="Google")
        self.osint1.executions.add(self.execution)
        self.cases = [
            PostApiTestCase([Role.ADMIN, Role.AUDITOR], 405),
            PostApiTestCase([Role.READER], 403, endpoint="2/target"),
            PostApiTestCase(["admin2", "auditor2"], 404, endpoint="2/target"),
            PostApiTestCase(["admin1", "auditor1"], 400, endpoint="1/target"),
            PostApiTestCase(
                ["auditor1"],
                expected={"id": 2, "target": "10.10.10.11", "type": TargetType.PRIVATE_IP.value},
                endpoint="2/target",
            ),
            ApiTestCase(["not_members"], 404, endpoint="/api/targets/2"),
            ApiTestCase(
                ["members"],
                expected={"id": 2, "target": "10.10.10.11", "type": TargetType.PRIVATE_IP.value},
                endpoint="/api/targets/2",
            ),
        ]
        super().test_cases()


class HostTest(FindingTest, TestCase):
    model = Host
    endpoint = "/api/hosts/"
    expected_defectdojo = {
        "title": "Host discovered",
        "description": f"IP: 10.10.10.10\nOS type: {HostOS.LINUX.value}",
        "severity": Severity.INFO,
    }
    expected_string = "10.10.10.10"


class PortTest(FindingTest, TestCase):
    model = Port
    endpoint = "/api/ports/"
    expected_defectdojo = {
        "title": "Port discovered",
        "description": f"Host: 10.10.10.10\nPort: 80\nStatus: {PortStatus.OPEN.value}\nProtocol: {TransportProtocol.TCP.value}\nService: http",
        "severity": Severity.INFO,
    }
    expected_string = f"10.10.10.10 - 80 - {TransportProtocol.TCP.value}"


class PathTest(FindingTest, TestCase):
    model = Path
    endpoint = "/api/paths/"
    expected_defectdojo = {
        "title": "Path discovered",
        "description": "Host: 10.10.10.10\nPort: 80\nPath: /index.html\nType: Endpoint\nStatus: 200",
        "severity": Severity.INFO,
    }
    expected_string = f"10.10.10.10 - 80 - {TransportProtocol.TCP.value} - /index.html"

    def test_defectdojo(self):
        super().test_defectdojo()
        defectdojo_endpoint = {"protocol": "http", "host": "10.10.10.10", "port": 80, "path": "/index.html"}
        parsed = self.path.defectdojo_endpoint(self.target)
        for key, value in defectdojo_endpoint.items():
            self.assertEqual(value, parsed[key])


class TechnologyTest(FindingTest, TestCase):
    model = Technology
    endpoint = "/api/technologies/"
    expected_defectdojo = {
        "title": "Technology WordPress detected",
        "description": "Typical CMS\n\nTechnology: WordPress\nVersion: 1.0.10",
        "severity": Severity.LOW,
        "cwe": 200,
        "references": "https://wordpress.org",
    }
    expected_string = f"10.10.10.10 - 80 - {TransportProtocol.TCP.value} - WordPress - 1.0.10"


class CredentialTest(FindingTest, TestCase):
    model = Credential
    endpoint = "/api/credentials/"
    expected_defectdojo = {
        "title": "Credentials exposure",
        "description": "Technology: WordPress\nEmail: admin10@rekono.com\nUsername: admin10\nSecret: admin",
        "cwe": 200,
        "severity": Severity.HIGH,
    }
    expected_string = (
        f"10.10.10.10 - 80 - {TransportProtocol.TCP.value} - WordPress - 1.0.10 - admin10@rekono.com - admin10 - admin"
    )


class VulnerabilityTest(FindingTest, TestCase):
    model = Vulnerability
    endpoint = "/api/vulnerabilities/"
    expected_defectdojo = {
        "title": "Vulnerability 10",
        "description": "Vulnerability 10",
        "severity": Severity.MEDIUM,
        "cve": "CVE-2025-3010",
        "cwe": 200,
    }
    expected_string = (
        f"10.10.10.10 - 80 - {TransportProtocol.TCP.value} - WordPress - 1.0.10 - Vulnerability 10 - CVE-2025-3010"
    )


class ExploitTest(FindingTest, TestCase):
    model = Exploit
    endpoint = "/api/exploits/"
    expected_defectdojo = {
        "title": "Exploit 1 found",
        "description": "ReverseShell 10",
        "severity": Severity.MEDIUM,
        "references": "https://www.exploit-db.com/exploits/1",
    }
    expected_string = f"10.10.10.10 - 80 - {TransportProtocol.TCP.value} - WordPress - 1.0.10 - Vulnerability 10 - CVE-2025-3010 - 1 - https://www.exploit-db.com/exploits/1"


class LatestHostsTest(ApiTest, TestCase):
    endpoint = "/api/hosts/latest/"
    data = [SetupProject(2, 6)]
    cases = [
        ApiTestCase(["members"], expected=[{"id": value} for value in range(1, 6)]),
        ApiTestCase(["not_members"]),
        ApiTestCase(["members"], expected=[{"id": value} for value in range(1, 6)], endpoint="{endpoint}?project=1"),
        ApiTestCase(["not_members"], endpoint="{endpoint}?project=1"),
        ApiTestCase(["members"], expected=[{"id": value} for value in range(1, 6)], endpoint="{endpoint}?target=1"),
        ApiTestCase(["members"], expected=[{"id": value} for value in range(7, 12)], endpoint="{endpoint}?target=2"),
        ApiTestCase(["not_members"], endpoint="{endpoint}?target=2"),
    ]


class LatestVulnerabilitiesTest(ApiTest, TestCase):
    endpoint = "/api/vulnerabilities/latest/"
    data = [
        SetupProject(1, 6),
        SetupProject(vulnerabilities_fields=[{"is_fixed": True}, {"triage_status": TriageStatus.FALSE_POSITIVE}]),
    ]
    cases = [
        ApiTestCase(
            ["members"],
            expected=[
                {"id": value, "is_fixed": False, "triage_status": TriageStatus.UNTRIAGED.value} for value in range(1, 6)
            ],
        ),
        ApiTestCase(["not_members"]),
        ApiTestCase(
            ["members"],
            expected=[
                {"id": value, "is_fixed": False, "triage_status": TriageStatus.UNTRIAGED.value} for value in range(1, 6)
            ],
            endpoint="{endpoint}?project=1",
        ),
        ApiTestCase(["members", "not_members"], endpoint="{endpoint}?project=2"),
        ApiTestCase(
            ["members"],
            expected=[
                {"id": value, "is_fixed": False, "triage_status": TriageStatus.UNTRIAGED.value} for value in range(1, 6)
            ],
            endpoint="{endpoint}?target=1",
        ),
        ApiTestCase(["members", "not_members"], endpoint="{endpoint}?target=2"),
    ]
