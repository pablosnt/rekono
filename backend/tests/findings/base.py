from functools import cached_property

from findings.enums import AutoFixedReason, TriageStatus
from findings.framework.models import Finding
from security.authorization.roles import Role
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
