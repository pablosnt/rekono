from django.db import models
from findings.enums import (
    HostOS,
    OSINTDataType,
    PortStatus,
    Protocol,
    Severity,
    TriageStatus,
)
from findings.models import (
    OSINT,
    Credential,
    Exploit,
    Host,
    Path,
    Port,
    Technology,
    Vulnerability,
)
from rest_framework.test import APIClient
from targets.enums import TargetType
from tests.cases import ApiTestCase
from tests.framework import ApiTest

findings_data = {
    OSINT: (
        {
            "title": f"{OSINTDataType.USER.value} found using OSINT techniques",
            "description": "admin",
            "severity": Severity.MEDIUM,
        },
        "admin",
        "/api/osint/",
    ),
    Host: (
        {
            "title": "Host discovered",
            "description": f"10.10.10.10 - {HostOS.LINUX.value}",
            "severity": Severity.INFO.value,
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
        "10.10.10.10 - 80",
        "/api/ports/",
    ),
    Path: (
        {
            "title": "Path discovered",
            "description": "Host: 10.10.10.10\nPort: 80\nPath: /index.php\nType: ENDPOINT\nStatus: 200\nInfo: Main path",
            "severity": Severity.INFO,
        },
        "10.10.10.10 - 80 - /index.php",
        "/api/paths/",
    ),
    Technology: (
        {
            "title": "Technology WordPress detected",
            "description": "Technology: WordPress\nVersion: 1.0.0\nDetails: Typical CMS",
            "severity": Severity.LOW,
            "cwe": 200,
            "references": "https://wordpress.org",
        },
        "10.10.10.10 - 80 - WordPress",
        "/api/technologies/",
    ),
    Credential: (
        {
            "title": "Credentials exposure",
            "description": "admin@shop.com - admin - admin",
            "cwe": 200,
            "severity": Severity.HIGH,
        },
        "10.10.10.10 - 80 - WordPress - admin@shop.com - admin - admin",
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
        "10.10.10.10 - 80 - WordPress - Test - CVE-2023-1111",
        "/api/vulnerabilities/",
    ),
    Exploit: (
        {
            "title": "Exploit 1 found",
            "description": "ReverseShell",
            "severity": Severity.CRITICAL,
            "references": "https://www.exploit-db.com/exploits/1",
        },
        "10.10.10.10 - 80 - WordPress - Test - CVE-2023-1111 - ReverseShell",
        "/api/exploits/",
    ),
}
false_positive = {
    "triage_status": TriageStatus.FALSE_POSITIVE.value,
    "triage_comment": "It isn't exploitable",
}
true_positive = {
    "triage_status": TriageStatus.TRUE_POSITIVE.value,
    "triage_comment": "Exploitation has been confirmed",
}


class FindingTest(ApiTest):
    endpoint = "/api/findings/"

    def setUp(self) -> None:
        super().setUp()
        self._setup_tasks_and_executions()
        self._setup_findings(self.execution3)
        self.cases = []
        for finding in self.findings:
            self.cases.extend(
                [
                    ApiTestCase(
                        ["admin2", "auditor2", "reader2"],
                        "get",
                        200,
                        endpoint=findings_data[finding.__class__][2],
                    ),
                    ApiTestCase(
                        ["admin1", "auditor1", "reader1"],
                        "get",
                        200,
                        expected=[
                            {
                                "id": 1,
                                "triage_status": TriageStatus.UNTRIAGED.value,
                                "triage_comment": "",
                                **{
                                    k: v
                                    if not isinstance(v, models.TextChoices)
                                    else v.value
                                    for k, v in self.raw_findings[
                                        finding.__class__
                                    ].items()
                                },
                            }
                        ],
                        endpoint=findings_data[finding.__class__][2],
                    ),
                    ApiTestCase(
                        ["admin1", "auditor1", "reader1"],
                        "get",
                        200,
                        expected=[
                            {
                                "id": 1,
                                "triage_status": TriageStatus.UNTRIAGED.value,
                                "triage_comment": "",
                                **{
                                    k: v
                                    if not isinstance(v, models.TextChoices)
                                    else v.value
                                    for k, v in self.raw_findings[
                                        finding.__class__
                                    ].items()
                                },
                            }
                        ],
                        endpoint=f"{findings_data[finding.__class__][2]}?host=1",
                    ),
                    ApiTestCase(
                        ["reader1", "reader2"],
                        "put",
                        403,
                        false_positive,
                        endpoint=f"{findings_data[finding.__class__][2]}1/",
                    ),
                    ApiTestCase(
                        ["admin2", "auditor2"],
                        "put",
                        404,
                        false_positive,
                        endpoint=f"{findings_data[finding.__class__][2]}1/",
                    ),
                    ApiTestCase(
                        ["admin1", "auditor1"],
                        "put",
                        200,
                        false_positive,
                        expected={"id": 1, **false_positive},
                        endpoint=f"{findings_data[finding.__class__][2]}1/",
                    ),
                    ApiTestCase(
                        ["admin1", "auditor1", "reader1"],
                        "get",
                        200,
                        expected={
                            "id": 1,
                            **false_positive,
                            **{
                                k: v
                                if not isinstance(v, models.TextChoices)
                                else v.value
                                for k, v in self.raw_findings[finding.__class__].items()
                            },
                        },
                        endpoint=f"{findings_data[finding.__class__][2]}1/",
                    ),
                    ApiTestCase(
                        ["admin1", "auditor1"],
                        "put",
                        200,
                        true_positive,
                        expected={"id": 1, **true_positive},
                        endpoint=f"{findings_data[finding.__class__][2]}1/",
                    ),
                    ApiTestCase(
                        ["admin1", "auditor1", "reader1"],
                        "get",
                        200,
                        expected={
                            "id": 1,
                            **true_positive,
                            **{
                                k: v
                                if not isinstance(v, models.TextChoices)
                                else v.value
                                for k, v in self.raw_findings[finding.__class__].items()
                            },
                        },
                        endpoint=f"{findings_data[finding.__class__][2]}1/",
                    ),
                ]
            )

    def test_str(self) -> None:
        for finding in self.findings:
            self.assertEqual(
                findings_data[finding.__class__][1],
                finding.__str__(),
            )

    def test_anonymous_access(self) -> None:
        for _, _, endpoint in findings_data.values():
            self.assertEqual(401, APIClient().get(endpoint).status_code)

    def test_defect_dojo(self) -> None:
        for finding in self.findings:
            parsed = finding.defect_dojo()
            for key, value in findings_data[finding.__class__][0].items():
                self.assertEqual(value, parsed[key])
        defect_dojo_endpoint = {
            "protocol": "http",
            "host": "10.10.10.10",
            "port": 80,
            "path": "/index.php",
        }
        parsed = self.path.defect_dojo_endpoint(self.target)
        for key, value in defect_dojo_endpoint.items():
            self.assertEqual(value, parsed[key])


class OSINTTest(ApiTest):
    endpoint = "/api/osint/"
    anonymous_allowed = None
    cases = [
        ApiTestCase(["admin1", "admin2", "auditor1", "auditor2"], "post", 405),
        ApiTestCase(
            ["reader1", "reader2"], "post", 403, endpoint="{endpoint}2/target/"
        ),
        ApiTestCase(
            ["admin2", "auditor2"], "post", 404, endpoint="{endpoint}2/target/"
        ),
        ApiTestCase(
            ["admin1", "auditor1"], "post", 400, endpoint="{endpoint}1/target/"
        ),
        ApiTestCase(
            ["auditor1"],
            "post",
            201,
            expected={
                "id": 2,
                "target": "10.10.10.11",
                "type": TargetType.PRIVATE_IP.value,
            },
            endpoint="{endpoint}2/target/",
        ),
        ApiTestCase(
            ["admin2", "auditor2", "reader2"], "get", 404, endpoint="/api/targets/2/"
        ),
        ApiTestCase(
            ["admin1", "auditor1", "reader1"],
            "get",
            200,
            expected={
                "id": 2,
                "target": "10.10.10.11",
                "type": TargetType.PRIVATE_IP.value,
            },
            endpoint="/api/targets/2/",
        ),
    ]

    def setUp(self) -> None:
        super().setUp()
        self._setup_tasks_and_executions()
        self._setup_findings(self.execution3)
        self.osint1 = self._create_finding(
            OSINT,
            {"data": "10.10.10.11", "data_type": OSINTDataType.IP, "source": "Google"},
            self.execution3,
        )
