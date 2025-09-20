from django.test import TestCase

from findings.models import Vulnerability
from tests.framework import ParserTest
from tests.framework.cases import ParserTestCase


class Spring4shellscanTest(ParserTest, TestCase):
    tool_name = "Spring4Shell Scan"
    cases = [
        ParserTestCase(
            "cve_2022_22963.txt",
            [{"model": Vulnerability, "name": "Spring Cloud RCE", "cve": "CVE-2022-22963"}],
        ),
        ParserTestCase(
            "cve_2022_22965.txt",
            [{"model": Vulnerability, "name": "Spring4Shell RCE", "cve": "CVE-2022-22965"}],
        ),
        ParserTestCase("not_vulnerable.txt"),
    ]
