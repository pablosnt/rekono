from functools import cached_property

from rest_framework.test import APIClient

from findings.enums import HostOS, OSINTDataType, PortStatus, Protocol, Severity, TriageStatus
from findings.models import OSINT, Credential, Exploit, Host, Path, Port, Technology, Vulnerability
from security.authorization.roles import Role
from targets.enums import TargetType
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase, PutApiTestCase

# pytype: disable=wrong-arg-types

findings_data = {
    OSINT: (
        {
            "title": f"{OSINTDataType.USER.value} found using OSINT techniques",
            "description": "Data: admin\nSource: Google",
            "severity": Severity.MEDIUM,
        },
        f"admin - {OSINTDataType.USER.value}",
        "/api/osint/",
    ),
    Host: (
        {
            "title": "Host discovered",
            "description": f"IP: 10.10.10.10\nOS type: {HostOS.LINUX.value}\nOS: some type of Linux",
            "severity": Severity.INFO,
        },
        "10.10.10.10",
        "/api/hosts/",
    ),
    Port: (
        {
            "title": "Port discovered",
            "description": f"Host: 10.10.10.10\nPort: 80\nStatus: {PortStatus.OPEN.value}\nProtocol: {Protocol.TCP.value}\nService: http",
            "severity": Severity.INFO,
        },
        f"10.10.10.10 - 80 - {Protocol.TCP.value}",
        "/api/ports/",
    ),
    Path: (
        {
            "title": "Path discovered",
            "description": "Host: 10.10.10.10\nPort: 80\nPath: /index.php\nType: ENDPOINT\nStatus: 200\nInfo: Main path",
            "severity": Severity.INFO,
        },
        f"10.10.10.10 - 80 - {Protocol.TCP.value} - /index.php",
        "/api/paths/",
    ),
    Technology: (
        {
            "title": "Technology WordPress detected",
            "description": "Typical CMS\n\nTechnology: WordPress\nVersion: 1.0.0",
            "severity": Severity.LOW,
            "cwe": 200,
            "references": "https://wordpress.org",
        },
        f"10.10.10.10 - 80 - {Protocol.TCP.value} - WordPress - 1.0.0",
        "/api/technologies/",
    ),
    Credential: (
        {
            "title": "Credentials exposure",
            "description": "Technology: WordPress\nEmail: admin@shop.com\nUsername: admin\nSecret: admin",
            "cwe": 200,
            "severity": Severity.HIGH,
        },
        f"10.10.10.10 - 80 - {Protocol.TCP.value} - WordPress - 1.0.0 - admin@shop.com - admin - admin",
        "/api/credentials/",
    ),
    Vulnerability: (
        {
            "title": "Test",
            "description": "Test",
            "severity": Severity.CRITICAL,
            "cve": "CVE-2023-1111",
            "cwe": 200,
            "references": "https://nvd.nist.gov/vuln/detail/CVE-2023-1111",
        },
        f"10.10.10.10 - 80 - {Protocol.TCP.value} - WordPress - 1.0.0 - Test - CVE-2023-1111",
        "/api/vulnerabilities/",
    ),
    Exploit: (
        {
            "title": "Exploit 1 found",
            "description": "ReverseShell",
            "severity": Severity.CRITICAL,
            "references": "https://www.exploit-db.com/exploits/1",
        },
        f"10.10.10.10 - 80 - {Protocol.TCP.value} - WordPress - 1.0.0 - Test - CVE-2023-1111 - 1 - https://www.exploit-db.com/exploits/1",
        "/api/exploits/",
    ),
}


class FindingTest(ApiTest):
    endpoint = "/api/findings/"
    setup_entities = ["findings"]
    false_positive = {"triage_status": TriageStatus.FALSE_POSITIVE.value, "triage_comment": "It isn't exploitable"}
    true_positive = {
        "triage_status": TriageStatus.TRUE_POSITIVE.value,
        "triage_comment": "Exploitation has been confirmed",
    }

    @cached_property
    def cases(self) -> list[ApiTestCase]:
        cases = []
        for finding in self.findings:
            endpoint = findings_data[finding.__class__][2]
            cases.extend(
                [
                    PostApiTestCase([Role.ADMIN, Role.AUDITOR], 405, endpoint=endpoint),
                    ApiTestCase(["not_members"], endpoint=endpoint),
                    ApiTestCase(
                        ["members"],
                        expected=[
                            {
                                "id": 1,
                                "is_fixed": False,
                                **{
                                    k: str(v) if isinstance(v, Severity) else v
                                    for k, v in self.raw_findings[finding.__class__].items()
                                },
                            }
                        ],
                        endpoint=endpoint,
                    ),
                    PostApiTestCase(["admin2", "auditor2"], 404, endpoint=f"{endpoint}1/fix/"),
                    PostApiTestCase([Role.READER], 403, endpoint=f"{endpoint}1/fix/"),
                    PostApiTestCase(["auditor1"], 204, endpoint=f"{endpoint}1/fix/"),
                    PostApiTestCase(["admin1"], 400, endpoint=f"{endpoint}1/fix/"),
                    ApiTestCase(
                        ["members"],
                        expected=[
                            {
                                "id": 1,
                                "is_fixed": True,
                                **{
                                    k: str(v) if isinstance(v, Severity) else v
                                    for k, v in self.raw_findings[finding.__class__].items()
                                },
                            }
                        ],
                        endpoint=endpoint,
                    ),
                    DeleteApiTestCase(["admin2", "auditor2"], 404, endpoint=f"{endpoint}1/fix/"),
                    DeleteApiTestCase([Role.READER], 403, endpoint=f"{endpoint}1/fix/"),
                    DeleteApiTestCase(["admin1"], endpoint=f"{endpoint}1/fix/"),
                    DeleteApiTestCase(["auditor1"], 400, endpoint=f"{endpoint}1/fix/"),
                    ApiTestCase(
                        ["members"],
                        expected=[
                            {
                                "id": 1,
                                "is_fixed": False,
                                **{
                                    k: str(v) if isinstance(v, Severity) else v
                                    for k, v in self.raw_findings[finding.__class__].items()
                                },
                            }
                        ],
                        endpoint=endpoint,
                    ),
                ]
            )
            if hasattr(finding, "triage_status"):
                cases.extend(
                    [
                        ApiTestCase(["not_members"], endpoint=endpoint),
                        ApiTestCase(
                            ["members"],
                            expected=[
                                {
                                    "id": 1,
                                    "triage_status": TriageStatus.UNTRIAGED.value,
                                    **{
                                        k: str(v) if isinstance(v, Severity) else v
                                        for k, v in self.raw_findings[finding.__class__].items()
                                    },
                                }
                            ],
                            endpoint=endpoint,
                        ),
                        ApiTestCase(
                            ["members"],
                            expected=[
                                {
                                    "id": 1,
                                    "triage_status": TriageStatus.UNTRIAGED.value,
                                    **{
                                        k: str(v) if isinstance(v, Severity) else v
                                        for k, v in self.raw_findings[finding.__class__].items()
                                    },
                                }
                            ],
                            endpoint=f"{endpoint}?host=1",
                        ),
                        PutApiTestCase([Role.READER], 403, self.false_positive, endpoint=f"{endpoint}1/"),
                        PutApiTestCase(
                            ["admin2", "auditor2"],
                            404,
                            self.false_positive,
                            endpoint=f"{endpoint}1/",
                        ),
                        PutApiTestCase(
                            ["admin1", "auditor1"],
                            data=self.false_positive,
                            expected={"id": 1, **self.false_positive},
                            endpoint=f"{endpoint}1/",
                        ),
                        ApiTestCase(
                            ["members"],
                            expected={
                                "id": 1,
                                **self.false_positive,
                                **{
                                    k: str(v) if isinstance(v, Severity) else v
                                    for k, v in self.raw_findings[finding.__class__].items()
                                },
                            },
                            endpoint=f"{endpoint}1/",
                        ),
                        PutApiTestCase(
                            ["admin1", "auditor1"],
                            data=self.true_positive,
                            expected={"id": 1, **self.true_positive},
                            endpoint=f"{endpoint}1/",
                        ),
                        ApiTestCase(
                            ["members"],
                            expected={
                                "id": 1,
                                **self.true_positive,
                                **{
                                    k: str(v) if isinstance(v, Severity) else v
                                    for k, v in self.raw_findings[finding.__class__].items()
                                },
                            },
                            endpoint=f"{endpoint}1/",
                        ),
                    ]
                )
        return cases

    def test_string(self) -> None:
        for finding in self.findings:
            self.assertEqual(findings_data[finding.__class__][1], finding.__str__())

    def test_anonymous_access(self) -> None:
        for _, _, endpoint in findings_data.values():
            self.assertEqual(401, APIClient().get(endpoint).status_code)

    def test_defectdojo(self) -> None:
        for finding in self.findings:
            parsed = finding.defectdojo_finding()
            for key, value in findings_data[finding.__class__][0].items():
                self.assertEqual(value, parsed[key])
        defectdojo_endpoint = {"protocol": "http", "host": "10.10.10.10", "port": 80, "path": "/index.php"}
        parsed = self.path.defectdojo_endpoint(self.target)
        for key, value in defectdojo_endpoint.items():
            self.assertEqual(value, parsed[key])


class OSINTTest(ApiTest):
    endpoint = "/api/osint/"
    anonymous_allowed = None
    setup_entities = ["findings"]
    cases = [
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

    def setUp(self) -> None:
        super().setUp()
        self.osint1 = OSINT.objects.create(data="10.10.10.11", data_type=OSINTDataType.IP, source="Google")
        self.osint1.executions.add(self.execution21)
