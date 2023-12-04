from typing import Any, Dict

from django.db import models, transaction
from executions.models import Execution
from findings.enums import (
    HostOS,
    OSINTDataType,
    PathType,
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
from targets.models import Target
from tasks.models import Task
from tests.cases import ApiTestCase
from tests.framework import ApiTest
from tools.models import Configuration

findings = [
    (
        OSINT,
        {
            "data": "admin",
            "data_type": OSINTDataType.USER,
            "source": "Google",
            "reference": "https://any.com",
        },
        {
            "title": f"{OSINTDataType.USER.value} found using OSINT techniques",
            "description": "admin",
            "severity": Severity.MEDIUM,
        },
        "admin",
        "/api/osint/",
    ),
    (
        Host,
        {
            "address": "10.10.10.10",
            "os": "some type of Linux",
            "os_type": HostOS.LINUX,
        },
        {
            "title": "Host discovered",
            "description": f"10.10.10.10 - {HostOS.LINUX.value}",
            "severity": Severity.INFO.value,
        },
        "10.10.10.10",
        "/api/hosts/",
    ),
    (
        Port,
        {
            "host": 1,
            "port": 80,
            "status": PortStatus.OPEN,
            "protocol": Protocol.TCP,
            "service": "http",
        },
        {
            "title": "Port discovered",
            "description": f"Host: 10.10.10.10\nPort: 80\nStatus: {PortStatus.OPEN.value}\nProtocol: {Protocol.TCP.value}\nService: http",
            "severity": Severity.INFO,
        },
        "10.10.10.10 - 80",
        "/api/ports/",
    ),
    (
        Path,
        {
            "port": 1,
            "path": "/index.php",
            "status": 200,
            "extra_info": "Main path",
            "type": PathType.ENDPOINT,
        },
        {"protocol": "http", "host": "10.10.10.10", "port": 80, "path": "/index.php"},
        "10.10.10.10 - 80 - /index.php",
        "/api/paths/",
    ),
    (
        Technology,
        {
            "port": 1,
            "name": "WordPress",
            "version": "1.0.0",
            "description": "Typical CMS",
            "reference": "https://wordpress.org",
        },
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
    (
        Credential,
        {
            "technology": 1,
            "email": "admin@shop.com",
            "username": "admin",
            "secret": "admin",
            "context": "Default admin credentials",
        },
        {
            "title": "Credentials exposure",
            "description": "admin@shop.com - admin - admin",
            "cwe": 200,
            "severity": Severity.HIGH,
        },
        "10.10.10.10 - 80 - WordPress - admin@shop.com - admin - admin",
        "/api/credentials/",
    ),
    (
        Vulnerability,
        {
            "technology": 1,
            "name": "Test",
            "description": "Test",
            "severity": Severity.CRITICAL,
            "cve": "CVE-2023-1111",
            "cwe": "CWE-200",
            "reference": "https://nvd.nist.gov/vuln/detail/CVE-2023-1111",
        },
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
    (
        Exploit,
        {
            "vulnerability": 1,
            "title": "Reverse Shell",
            "edb_id": 1,
            "reference": "https://www.exploit-db.com/exploits/1",
        },
        {
            "title": "Exploit 1 found",
            "description": "Reverse Shell",
            "severity": Severity.CRITICAL,
            "references": "https://www.exploit-db.com/exploits/1",
        },
        "10.10.10.10 - 80 - WordPress - Test - CVE-2023-1111 - Reverse Shell",
        "/api/exploits/",
    ),
]
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

    def _create_finding(
        self, model: Any, data: Dict[str, Any], execution: Execution
    ) -> Any:
        new_finding = model.objects.create(
            **{
                k: getattr(self, k)
                if isinstance(v, int) and hasattr(self, k) and getattr(self, k).id == v
                else v
                for k, v in data.items()
            }
        )
        new_finding.executions.add(execution)
        return new_finding

    def setUp(self) -> None:
        super().setUp()
        self._setup_tasks_and_executions()
        self.cases = []
        for finding_model, finding_data, _, _, endpoint in findings:
            setattr(
                self,
                finding_model.__name__.lower(),
                self._create_finding(finding_model, finding_data, self.execution3),
            )
            self.cases.extend(
                [
                    ApiTestCase(
                        ["admin2", "auditor2", "reader2"], "get", 200, endpoint=endpoint
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
                                    for k, v in finding_data.items()
                                },
                            }
                        ],
                        endpoint=endpoint,
                    ),
                    ApiTestCase(
                        ["reader1", "reader2"],
                        "put",
                        403,
                        false_positive,
                        endpoint=f"{endpoint}1/",
                    ),
                    ApiTestCase(
                        ["admin2", "auditor2"],
                        "put",
                        404,
                        false_positive,
                        endpoint=f"{endpoint}1/",
                    ),
                    ApiTestCase(
                        ["admin1", "auditor1"],
                        "put",
                        200,
                        false_positive,
                        expected={"id": 1, **false_positive},
                        endpoint=f"{endpoint}1/",
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
                                for k, v in finding_data.items()
                            },
                        },
                        endpoint=f"{endpoint}1/",
                    ),
                    ApiTestCase(
                        ["admin1", "auditor1"],
                        "put",
                        200,
                        true_positive,
                        expected={"id": 1, **true_positive},
                        endpoint=f"{endpoint}1/",
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
                                for k, v in finding_data.items()
                            },
                        },
                        endpoint=f"{endpoint}1/",
                    ),
                ]
            )

    def test_str(self) -> None:
        for finding_model, _, _, expected_str, _ in findings:
            self.assertEqual(
                expected_str,
                getattr(self, finding_model.__name__.lower()).__str__(),
            )
        for finding_model, finding_data, pop_field, expected_str in [
            (
                Vulnerability,
                {**findings[6][1], "port": 1},
                "technology",
                "10.10.10.10 - 80 - Test - CVE-2023-1111",
            ),
            (
                Exploit,
                {**findings[7][1], "technology": 1},
                "vulnerability",
                "10.10.10.10 - 80 - WordPress - Reverse Shell",
            ),
        ]:
            finding_data.pop(pop_field)
            aux = self._create_finding(finding_model, finding_data, self.execution3)
            self.assertEqual(expected_str, aux.__str__())

    def test_anonymous_access(self) -> None:
        for _, _, _, _, endpoint in findings:
            response = APIClient().get(endpoint)
            self.assertEqual(
                200 if self.anonymous_allowed else 401, response.status_code
            )

    def test_defect_dojo(self) -> None:
        for finding_model, _, expected_data, _, _ in findings:
            parsed = getattr(self, finding_model.__name__.lower()).defect_dojo()
            for key, value in expected_data.items():
                self.assertEqual(value, parsed[key])


class OSINTTest(ApiTest):
    endpoint = "/api/osint/"
    anonymous_allowed = None
    cases = [
        ApiTestCase(["admin1", "admin2", "auditor1", "auditor2"], "post", 405),
        ApiTestCase(
            ["reader1", "reader2"], "post", 403, endpoint="{endpoint}1/target/"
        ),
        ApiTestCase(
            ["admin2", "auditor2"], "post", 404, endpoint="{endpoint}1/target/"
        ),
        ApiTestCase(
            ["admin1", "auditor1"], "post", 400, endpoint="{endpoint}2/target/"
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
            endpoint="{endpoint}1/target/",
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
        self.osint1 = OSINT.objects.create(
            data="10.10.10.11", data_type=OSINTDataType.IP, source="Google"
        )
        self.osint2 = OSINT.objects.create(**findings[0][1])
        for osint in [self.osint1, self.osint2]:
            osint.executions.add(self.execution3)
