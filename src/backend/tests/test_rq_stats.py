from tests.cases import ApiTestCase
from tests.framework import ApiTest
from rekono.views import exposed_fields


class RQStatsTest(ApiTest):
    endpoint = "/api/rq-stats/"
    cases = [
        ApiTestCase(["auditor1", "auditor2", "reader1", "reader2"], "get", 403),
        ApiTestCase(
            ["admin1", "admin2"],
            "get",
            200,
            expected={
                queue: {field: 0 for field in exposed_fields}
                for queue in ["executions-queue", "findings-queue", "tasks-queue"]
            },
        ),
    ]
