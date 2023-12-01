from findings.models import Vulnerability
from tests.cases import ToolTestCase
from tests.framework import ToolTest


class Log4jscanTest(ToolTest):
    tool_name = "Log4j Scan"
    cases = [
        ToolTestCase(
            "cve_2021_44228.txt",
            [{"model": Vulnerability, "name": "Log4Shell", "cve": "CVE-2021-44228"}],
        ),
        ToolTestCase("not_vulnerable.txt"),
    ]
