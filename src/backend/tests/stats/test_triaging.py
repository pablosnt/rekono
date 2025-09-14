from executions.models import Execution
from findings.enums import TriageStatus
from findings.models import Credential, Vulnerability
from tests.framework import StatsTest
from tests.framework.cases import ApiTestCase
from tests.framework.data import SetupProject


class TriagingStatsTest(StatsTest):
    endpoint = "/api/stats/triaging/"
    data = [SetupProject()]
    cases = [
        ApiTestCase(["members"], expected=[{"triage_status": TriageStatus.UNTRIAGED.value, "open": 4, "fixed": 0}])
    ]
