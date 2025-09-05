from findings.enums import OSINTDataType
from findings.models import OSINT
from tests.framework import ParserTest
from tests.framework.cases import ParserTestCase


class EmailharvesterTest(ParserTest):
    tool_name = "EmailHarvester"
    cases = [
        ParserTestCase(
            "default.txt",
            [
                {"model": OSINT, "data": "support@test.com", "data_type": OSINTDataType.EMAIL},
                {"model": OSINT, "data": "education@test.com", "data_type": OSINTDataType.EMAIL},
                {"model": OSINT, "data": "ceo@test.com", "data_type": OSINTDataType.EMAIL},
                {"model": OSINT, "data": "someone@test.com", "data_type": OSINTDataType.EMAIL},
                {"model": OSINT, "data": "other@test.com", "data_type": OSINTDataType.EMAIL},
            ],
        )
    ]
