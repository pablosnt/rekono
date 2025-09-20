from django.test import TestCase

from findings.enums import TriageStatus
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types


class TriagingStatsTest(ApiTest, TestCase):
    endpoint = "/api/stats/triaging/"
    data = [
        SetupProject(
            osint_fields=[{"triage_status": TriageStatus.TRUE_POSITIVE}, {"is_fixed": True}, {}],
            credentials_fields=[{"triage_status": TriageStatus.WONT_FIX}, {"is_fixed": True}],
            vulnerabilities_fields=[
                {"triage_status": TriageStatus.TRUE_POSITIVE},
                {"triage_status": TriageStatus.FALSE_POSITIVE},
                {},
            ],
            exploits_fields=[{"triage_status": TriageStatus.WONT_FIX}],
        ),
        SetupProject(
            osint_fields=[],
            credentials_fields=[],
            vulnerabilities_fields=[
                {"triage_status": TriageStatus.TRUE_POSITIVE, "is_fixed": True},
                {"triage_status": TriageStatus.FALSE_POSITIVE},
            ],
            exploits_fields=[],
        ),
    ]
    cases = [
        ApiTestCase(
            ["members"],
            expected=[
                {"triage_status": TriageStatus.FALSE_POSITIVE.value, "open": 2, "fixed": 0},
                {"triage_status": TriageStatus.TRUE_POSITIVE.value, "open": 2, "fixed": 1},
                {"triage_status": TriageStatus.UNTRIAGED.value, "open": 2, "fixed": 2},
                {"triage_status": TriageStatus.WONT_FIX.value, "open": 4, "fixed": 0},
            ],
        ),
        ApiTestCase(["not_members"]),
        ApiTestCase(
            ["members"],
            expected=[
                {"triage_status": TriageStatus.FALSE_POSITIVE.value, "open": 1, "fixed": 0},
                {"triage_status": TriageStatus.TRUE_POSITIVE.value, "open": 2, "fixed": 0},
                {"triage_status": TriageStatus.UNTRIAGED.value, "open": 2, "fixed": 2},
                {"triage_status": TriageStatus.WONT_FIX.value, "open": 4, "fixed": 0},
            ],
            endpoint="{endpoint}?project=1",
        ),
        ApiTestCase(["not_members"], endpoint="{endpoint}?project=2"),
        ApiTestCase(
            ["members"],
            expected=[
                {"triage_status": TriageStatus.FALSE_POSITIVE.value, "open": 1, "fixed": 0},
                {"triage_status": TriageStatus.TRUE_POSITIVE.value, "open": 0, "fixed": 1},
            ],
            endpoint="{endpoint}?target=2",
        ),
        ApiTestCase(["not_members"], endpoint="{endpoint}?target=1"),
    ]
