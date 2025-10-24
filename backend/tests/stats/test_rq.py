from django.test import TestCase

from security.authorization.roles import Role
from tests.framework import ApiTestNoData
from tests.framework.cases import ApiTestCase

# pytype: disable=wrong-arg-types


class RQTest(ApiTestNoData, TestCase):
    endpoint = "/api/stats/rq/"
    cases = [
        ApiTestCase(
            [Role.ADMIN],
            expected={queue: {"scheduled_jobs": 0} for queue in ["tasks", "executions", "findings", "monitor"]},
        ),
        ApiTestCase([Role.AUDITOR, Role.READER], 403),
    ]
