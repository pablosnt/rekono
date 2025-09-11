from findings.enums import TriageStatus
from security.authorization.roles import Role
from tests.framework import ApiTest, StatsTest
from tests.framework.cases import ApiTestCase
from tests.framework.data import SetupProject


class RQTest(ApiTest):
    endpoint = "/api/stats/rq/"
    cases = [
        ApiTestCase(
            [Role.ADMIN],
            expected={queue: {"scheduled_jobs": 0} for queue in ["tasks", "executions", "findings", "monitor"]},
        ),
        ApiTestCase([Role.AUDITOR, Role.READER], 403),
    ]


class TopProjectsTest(StatsTest):
    endpoint = "/api/stats/top-projects/"
    data = [
        # Project #1 (self.project) -> 0 vulnerabilities
        SetupProject(1, 0),
        # Project #2 -> 1 open vulnerability x 3 executions x 2 tasks = 6 vulnerabilities
        SetupProject(
            2, 3, _vulnerabilities_fields=[{}, {"is_fixed": True}, {"triage_status": TriageStatus.FALSE_POSITIVE}]
        ),
        # Project #3 -> 1 open vulnerability x 1 executions x 1 tasks = 1 vulnerability
        SetupProject(_vulnerabilities_fields=[{}, {"is_fixed": True}, {"triage_status": TriageStatus.FALSE_POSITIVE}]),
    ]
    cases = [ApiTestCase(["members"], expected=[{"id": 2}, {"id": 3}, {"id": 1}]), ApiTestCase(["not_members"])]


class LatestTasksTest(StatsTest):
    endpoint = "/api/stats/latest-tasks/"
    data = [SetupProject(1, 0), SetupProject(6, 0)]
    cases = [
        ApiTestCase(["members"], expected=[{"id": value, "target": {"id": value}} for value in range(1, 6)]),
        ApiTestCase(["not_members"]),
        ApiTestCase(["members"], expected=[{"id": 1, "target": {"id": 1}}], endpoint="{endpoint}?project=1"),
        ApiTestCase(["not_members"], endpoint="{endpoint}?project=1"),
        ApiTestCase(["members"], expected=[{"id": 1, "target": {"id": 1}}], endpoint="{endpoint}?target=1"),
        ApiTestCase(
            ["members"],
            expected=[{"id": value, "target": {"id": value}} for value in range(2, 7)],
            endpoint="{endpoint}?project=2",
        ),
        ApiTestCase(["members"], expected=[{"id": 2, "target": {"id": 2}}], endpoint="{endpoint}?target=2"),
    ]
