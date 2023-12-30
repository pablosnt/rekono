from tests.cases import ApiTestCase
from tests.framework import ApiTest


class RQStatsTest(ApiTest):
    endpoint = "/api/rq-stats/"
    cases = [
        ApiTestCase(["auditor1", "auditor2", "reader1", "reader2"], "get", 403),
        ApiTestCase(["admin1", "admin2"], "get", 200),
    ]
