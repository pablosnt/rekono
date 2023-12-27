from findings.models import Vulnerability
from tests.cases import ToolTestCase
from tests.framework import ToolTest


class Spring4shellscanTest(ToolTest):
    tool_name = "Spring4Shell Scan"
    cases = [
        ToolTestCase(
            "cve_2022_22963.txt",
            [
                {
                    "model": Vulnerability,
                    "name": "Spring Cloud RCE",
                    "cve": "CVE-2022-22963",
                }
            ],
        ),
        ToolTestCase(
            "cve_2022_22965.txt",
            [
                {
                    "model": Vulnerability,
                    "name": "Spring4Shell RCE",
                    "cve": "CVE-2022-22965",
                }
            ],
        ),
        ToolTestCase("not_vulnerable.txt"),
    ]
