from django.test import TestCase

from findings.enums import OSINTDataType
from findings.models import OSINT
from tests.framework import ParserTest
from tests.framework.cases import ParserTestCase


class TheharvesterTest(ParserTest, TestCase):
    tool_name = "theHarvester"
    cases = [
        ParserTestCase(
            "scanme.json",
            [
                {"model": OSINT, "data": "AS63949", "data_type": OSINTDataType.ASN},
                {"model": OSINT, "data": "http://scanme.nmap.org", "data_type": OSINTDataType.URL},
                {"model": OSINT, "data": "http://scanme.nmap.org/", "data_type": OSINTDataType.URL},
                {"model": OSINT, "data": "http://scanme.nmap.org//r/n/r/nUser:/r/n-", "data_type": OSINTDataType.URL},
                {"model": OSINT, "data": "45.33.32.156", "data_type": OSINTDataType.IP},
                {"model": OSINT, "data": "74.207.244.221", "data_type": OSINTDataType.IP},
                {"model": OSINT, "data": "2600:3c01::f03c:91ff:fe18:bb2f", "data_type": OSINTDataType.IP},
            ],
        )
    ]
