from django.test import TestCase

from findings.enums import OSINTDataType, Severity
from findings.models import OSINT
from security.authorization.roles import Role
from targets.enums import TargetType
from tests.findings.base import FindingTest
from tests.framework.cases import ApiTestCase, PostApiTestCase

# pytype: disable=wrong-arg-types,attribute-error


class OSINTTest(FindingTest, TestCase):
    model = OSINT
    endpoint = "/api/osint/"
    expected_defectdojo = {
        "title": f"{OSINTDataType.USER.value} found on public sources",
        "description": "Data: admin10\nSource: Google",
        "severity": str(Severity.LOW),
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
