from tests.cases import ApiTestCase
from tests.framework import ApiTest

# TODO: Tests for all /api/stats/ endpoints


class RQStatsTest(ApiTest):
    endpoint = "/api/stats/rq/"
    cases = [
        ApiTestCase(["auditor1", "auditor2", "reader1", "reader2"], "get", 403),
        ApiTestCase(["admin1", "admin2"], "get", 200),
    ]
