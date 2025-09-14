from security.authorization.roles import Role
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase

# pytype: disable=wrong-arg-types


class RQTest(ApiTest):
    endpoint = "/api/stats/rq/"
    cases = [
        ApiTestCase(
            [Role.ADMIN],
            expected={queue: {"scheduled_jobs": 0} for queue in ["tasks", "executions", "findings", "monitor"]},
        ),
        ApiTestCase([Role.AUDITOR, Role.READER], 403),
    ]
