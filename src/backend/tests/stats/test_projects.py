from findings.enums import TriageStatus
from tests.framework import StatsTest
from tests.framework.cases import ApiTestCase
from tests.framework.data import SetupProject

# pytype: disable=wrong-arg-types


class TopProjectsTest(StatsTest):
    endpoint = "/api/stats/top-projects/"
    data = [
        # Project #1 (self.project) -> 0 vulnerabilities
        SetupProject(1, 0),
        # Project #2 -> 1 open vulnerability x 3 executions x 2 tasks = 6 vulnerabilities
        SetupProject(
            2, 3, vulnerabilities_fields=[{}, {"is_fixed": True}, {"triage_status": TriageStatus.FALSE_POSITIVE}]
        ),
        # Project #3 -> 1 open vulnerability x 1 executions x 1 tasks = 1 vulnerability
        SetupProject(vulnerabilities_fields=[{}, {"is_fixed": True}, {"triage_status": TriageStatus.FALSE_POSITIVE}]),
    ]
    cases = [ApiTestCase(["members"], expected=[{"id": 2}, {"id": 3}, {"id": 1}]), ApiTestCase(["not_members"])]
