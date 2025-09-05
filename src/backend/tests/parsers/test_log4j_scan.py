from findings.models import Vulnerability
from tests.framework import ParserTest
from tests.framework.cases import ParserTestCase


class Log4jscanTest(ParserTest):
    tool_name = "Log4j Scan"
    cases = [
        ParserTestCase("cve_2021_44228.txt", [{"model": Vulnerability, "name": "Log4Shell", "cve": "CVE-2021-44228"}]),
        ParserTestCase("not_vulnerable.txt"),
    ]
