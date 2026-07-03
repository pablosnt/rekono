from functools import cached_property

from django.test import TestCase

from findings.enums import (
    AutoFixedReason,
    HostOS,
    OSINTDataType,
    PortStatus,
    Severity,
    TransportProtocol,
    TriageStatus,
)
from findings.framework.models import Finding
from findings.models import OSINT, Credential, Exploit, Host, Path, Port, Technology, Vulnerability
from security.authorization.roles import Role
from targets.enums import TargetType
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase, PutApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types,attribute-error


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
            ApiTestCase(["members"], expected=[{"id": 1, "is_fixed": True, "auto_fixed": None}]),
            DeleteApiTestCase(["admin2", "auditor2"], 404, endpoint="1/fix/"),
            DeleteApiTestCase([Role.READER], 403, endpoint="1/fix/"),
            DeleteApiTestCase(["admin1"], endpoint="1/fix/"),
            DeleteApiTestCase(["auditor1"], 400, endpoint="1/fix/"),
            ApiTestCase(["members"], expected=[{"id": 1, "is_fixed": False, "auto_fixed": None}]),
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

    def test_auto_fixed(self) -> None:
        finding = self.model.objects.first()
        related_findings = self.model.objects._get_related_findings(finding)

        # No longer detected
        self.model.objects.fix(finding)
        finding.refresh_from_db()
        self.assertTrue(finding.is_fixed)
        self.assertIsNone(finding.fixed_by)
        self.assertEqual(AutoFixedReason.NO_LONGER_DETECTED, finding.auto_fixed)
        # Related findings are auto-fixed because their parent finding got fixed
        for related_finding in related_findings:
            related_finding.refresh_from_db()
            self.assertTrue(related_finding.is_fixed)
            self.assertEqual(AutoFixedReason.PARENT_FIXED, related_finding.auto_fixed)

        # Auto-fix removed
        self.model.objects.remove_fix(finding)
        finding.refresh_from_db()
        self.assertFalse(finding.is_fixed)
        self.assertIsNone(finding.auto_fixed)

        # Manual fix
        self.model.objects.fix(finding, self.auditor1)
        finding.refresh_from_db()
        self.assertTrue(finding.is_fixed)
        self.assertEqual(self.auditor1, finding.fixed_by)
        self.assertIsNone(finding.auto_fixed)

    @cached_property
    def object(self) -> Finding:
        return self.model.objects.first()


class OSINTTest(FindingTest, TestCase):
    model = OSINT
    endpoint = "/api/osint/"
    expected_defectdojo = {
        "title": f"{OSINTDataType.USER.value} found on public sources",
        "description": "Data: admin10\nSource: Google",
        "severity": Severity.LOW,
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

    def test_deduplication(self):
        first = OSINT.objects.create_finding(
            self.execution, data="10.10.10.90", data_type=OSINTDataType.IP, source="Shodan"
        )
        second = OSINT.objects.create_finding(self.execution, data="10.10.10.90", data_type=OSINTDataType.IP)
        self.assertEqual(first.id, second.id)
        self.assertEqual(1, OSINT.objects.filter(data="10.10.10.90", data_type=OSINTDataType.IP).count())
        self.assertEqual("Shodan", second.source)
        self.assertNotEqual(
            second.id,
            OSINT.objects.create_finding(self.execution, data="10.10.10.90", data_type=OSINTDataType.DOMAIN).id,
        )


class HostTest(FindingTest, TestCase):
    model = Host
    endpoint = "/api/hosts/"
    expected_defectdojo = {
        "title": "Host discovered",
        "description": f"IP: 10.10.10.10\nOS type: {HostOS.LINUX.value}",
        "severity": Severity.INFO,
    }
    expected_string = "10.10.10.10"

    def test_deduplication(self):
        first = Host.objects.create_finding(self.execution, ip="10.10.10.60", os="Windows Server 2022")
        second = Host.objects.create_finding(self.execution, ip="10.10.10.60")
        self.assertEqual(first.id, second.id)
        self.assertEqual(1, Host.objects.filter(ip="10.10.10.60").count())
        self.assertEqual("Windows Server 2022", second.os)
        self.assertNotEqual(second.id, Host.objects.create_finding(self.execution, ip="10.10.10.61").id)

    def test_deduplication_with_user_input(self):
        user_finding = Host.objects.create_finding(self.execution, ip="10.10.10.62", created_from_user_input=True)
        detected_finding = Host.objects.create_finding(
            self.execution, ip="10.10.10.62", os="Ubuntu 22.04", created_from_user_input=False
        )
        self.assertEqual(user_finding.id, detected_finding.id)
        self.assertEqual(1, Host.objects.filter(ip="10.10.10.62").count())
        self.assertEqual("Ubuntu 22.04", detected_finding.os)
        self.assertFalse(detected_finding.created_from_user_input)

    def test_deduplication_with_new_user_input(self):
        detected_finding = Host.objects.create_finding(self.execution, ip="10.10.10.63", os="Debian 12")
        user_finding = Host.objects.create_finding(self.execution, ip="10.10.10.63", created_from_user_input=True)
        self.assertEqual(detected_finding.id, user_finding.id)
        self.assertEqual(1, Host.objects.filter(ip="10.10.10.63").count())
        self.assertEqual("Debian 12", user_finding.os)
        self.assertFalse(user_finding.created_from_user_input)


class PortTest(FindingTest, TestCase):
    model = Port
    endpoint = "/api/ports/"
    expected_defectdojo = {
        "title": "Port discovered",
        "description": f"Host: 10.10.10.10\nPort: 80\nStatus: {PortStatus.OPEN.value}\nProtocol: {TransportProtocol.TCP.value}\nService: http",
        "severity": Severity.INFO,
    }
    expected_string = f"10.10.10.10 - 80 - {TransportProtocol.TCP.value}"

    def test_deduplication(self):
        first = Port.objects.create_finding(
            self.execution, host=self.host, port=8443, protocol=TransportProtocol.TCP, service="https-alt"
        )
        second = Port.objects.create_finding(self.execution, host=self.host, port=8443)
        self.assertEqual(first.id, second.id)
        self.assertEqual(1, Port.objects.filter(host=self.host, port=8443).count())
        self.assertEqual(TransportProtocol.TCP, second.protocol)
        self.assertNotEqual(
            second.id,
            Port.objects.create_finding(
                self.execution, host=self.host, port=8443, protocol=TransportProtocol.UDP, service="unknown"
            ).id,
        )

    def test_deduplication_with_user_input(self):
        user_finding = Port.objects.create_finding(
            self.execution, host=self.host, port=8080, created_from_user_input=True
        )
        detected_finding = Port.objects.create_finding(
            self.execution,
            host=self.host,
            port=8080,
            protocol=TransportProtocol.TCP,
            service="http-alt",
            created_from_user_input=False,
        )
        self.assertEqual(user_finding.id, detected_finding.id)
        self.assertEqual(1, Port.objects.filter(host=self.host, port=8080).count())
        self.assertEqual(TransportProtocol.TCP, detected_finding.protocol)
        self.assertEqual("http-alt", detected_finding.service)
        self.assertFalse(detected_finding.created_from_user_input)

    def test_deduplication_with_new_user_input(self):
        detected_finding = Port.objects.create_finding(
            self.execution, host=self.host, port=9090, protocol=TransportProtocol.TCP, service="websocket"
        )
        user_finding = Port.objects.create_finding(
            self.execution, host=self.host, port=9090, created_from_user_input=True
        )
        self.assertEqual(detected_finding.id, user_finding.id)
        self.assertEqual(1, Port.objects.filter(host=self.host, port=9090).count())
        self.assertEqual(TransportProtocol.TCP, user_finding.protocol)
        self.assertEqual("websocket", user_finding.service)
        self.assertFalse(user_finding.created_from_user_input)


class PathTest(FindingTest, TestCase):
    model = Path
    endpoint = "/api/paths/"
    expected_defectdojo = None
    expected_string = f"10.10.10.10 - 80 - {TransportProtocol.TCP.value} - /index.html"

    def test_defectdojo(self):
        defectdojo_endpoint = {"protocol": "http", "host": "10.10.10.10", "port": 80, "path": "/index.html"}
        parsed = self.path.defectdojo_endpoint()
        for key, value in defectdojo_endpoint.items():
            self.assertEqual(value, parsed[key])

    def test_deduplication(self):
        first = Path.objects.create_finding(self.execution, port=self.port, path="/admin", status=403)
        second = Path.objects.create_finding(self.execution, port=self.port, path="/admin")
        self.assertEqual(first.id, second.id)
        self.assertEqual(1, Path.objects.filter(port=self.port, path="/admin").count())
        self.assertEqual(403, second.status)
        self.assertNotEqual(second.id, Path.objects.create_finding(self.execution, port=self.port, path="/login").id)


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

    def test_deduplication(self):
        first = Technology.objects.create_finding(self.execution, port=self.port, name="Grafana", version="10.1.0")
        second = Technology.objects.create_finding(self.execution, port=self.port, name="Grafana")
        self.assertEqual(first.id, second.id)
        self.assertEqual(1, Technology.objects.filter(port=self.port, name="Grafana").count())
        self.assertEqual("10.1.0", second.version)
        self.assertNotEqual(
            second.id,
            Technology.objects.create_finding(self.execution, port=self.port, name="Grafana", version="10.2.0").id,
        )

    def test_deduplication_with_user_input(self):
        user_finding = Technology.objects.create_finding(
            self.execution, port=self.port, name="Joomla", created_from_user_input=True
        )
        detected_finding = Technology.objects.create_finding(
            self.execution,
            port=self.port,
            name="Joomla",
            version="4.2.0",
            created_from_user_input=False,
        )
        self.assertEqual(user_finding.id, detected_finding.id)
        self.assertEqual(1, Technology.objects.filter(port=self.port, name="Joomla").count())
        self.assertEqual("4.2.0", detected_finding.version)
        self.assertFalse(detected_finding.created_from_user_input)

    def test_deduplication_with_new_user_input(self):
        detected_finding = Technology.objects.create_finding(
            self.execution, port=self.port, name="Drupal", version="9.5.0"
        )
        user_finding = Technology.objects.create_finding(
            self.execution, port=self.port, name="Drupal", created_from_user_input=True
        )
        self.assertEqual(detected_finding.id, user_finding.id)
        self.assertEqual(1, Technology.objects.filter(port=self.port, name="Drupal").count())
        self.assertEqual("9.5.0", user_finding.version)
        self.assertFalse(user_finding.created_from_user_input)


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

    def test_deduplication(self):
        first = Credential.objects.create_finding(
            self.execution,
            technology=self.technology,
            email="root@rekono.com",
            username="root",
            secret="toor",
            context="Found in backup file",
        )
        second = Credential.objects.create_finding(
            self.execution, technology=self.technology, email="root@rekono.com", username="root", secret="toor"
        )
        self.assertEqual(first.id, second.id)
        self.assertEqual(
            1,
            Credential.objects.filter(
                technology=self.technology, email="root@rekono.com", username="root", secret="toor"
            ).count(),
        )
        self.assertEqual("Found in backup file", second.context)
        self.assertNotEqual(
            second.id,
            Credential.objects.create_finding(
                self.execution, technology=self.technology, email="root@rekono.com", username="root", secret="different"
            ).id,
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

    def test_deduplication_with_user_input(self):
        user_finding = Vulnerability.objects.create_finding(
            self.execution,
            port=self.port,
            name="CVE-2025-9999",
            cve="CVE-2025-9999",
            created_from_user_input=True,
        )
        detected_finding = Vulnerability.objects.create_finding(
            self.execution,
            port=self.port,
            technology=self.technology,
            name="CVE-2025-9999",
            cve="CVE-2025-9999",
            created_from_user_input=False,
        )
        self.assertEqual(user_finding.id, detected_finding.id)
        self.assertEqual(1, Vulnerability.objects.filter(port=self.port, cve="CVE-2025-9999").count())
        self.assertEqual(self.technology, detected_finding.technology)
        self.assertFalse(detected_finding.created_from_user_input)

    def test_deduplication_with_new_user_input(self):
        detected_finding = Vulnerability.objects.create_finding(
            self.execution, port=self.port, name="Already enriched finding", cve="CVE-2024-1111"
        )
        user_finding = Vulnerability.objects.create_finding(
            self.execution, port=self.port, name="CVE-2024-1111", cve="CVE-2024-1111", created_from_user_input=True
        )
        self.assertEqual(detected_finding.id, user_finding.id)
        self.assertEqual("Already enriched finding", user_finding.name)
        self.assertEqual(1, Vulnerability.objects.filter(port=self.port, cve="CVE-2024-1111").count())
        self.assertFalse(user_finding.created_from_user_input)

    def test_deduplication_with_new_user_input_via_lookup(self):
        self.assertIsNone(self.vulnerability.port)
        original_name = self.vulnerability.name
        user_finding = Vulnerability.objects.create_finding(
            self.execution,
            port=self.vulnerability.technology.port,
            name=self.vulnerability.cve,
            cve=self.vulnerability.cve,
            created_from_user_input=True,
        )
        self.assertEqual(self.vulnerability.id, user_finding.id)
        self.assertEqual(1, Vulnerability.objects.filter(cve=self.vulnerability.cve).count())
        self.assertEqual(original_name, user_finding.name)
        self.assertFalse(user_finding.created_from_user_input)

    def test_deduplication_not_merged(self):
        algorithm_finding = Vulnerability.objects.create_finding(
            self.execution, technology=self.technology, name="Insecure MAC algorithm: hmac-md5"
        )
        cve_finding = Vulnerability.objects.create_finding(
            self.execution, technology=self.technology, name="CVE-2023-48795", cve="CVE-2023-48795"
        )
        self.assertNotEqual(algorithm_finding.id, cve_finding.id)


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

    def test_deduplication(self):
        first = Exploit.objects.create_finding(
            self.execution,
            vulnerability=self.vulnerability,
            title="Custom PoC",
            reference="https://example.com/poc",
            edb_id=99999,
        )
        second = Exploit.objects.create_finding(
            self.execution, vulnerability=self.vulnerability, title="Custom PoC", reference="https://example.com/poc"
        )
        self.assertEqual(first.id, second.id)
        self.assertEqual(
            1, Exploit.objects.filter(vulnerability=self.vulnerability, reference="https://example.com/poc").count()
        )
        self.assertEqual(99999, second.edb_id)
        self.assertNotEqual(
            second.id,
            Exploit.objects.create_finding(
                self.execution,
                vulnerability=self.vulnerability,
                title="Custom PoC",
                reference="https://example.com/poc",
                edb_id=11111,
            ).id,
        )


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
