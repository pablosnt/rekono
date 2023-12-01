from findings.enums import OSINTDataType
from findings.models import OSINT
from tests.cases import ToolTestCase
from tests.framework import ToolTest


class EmailharvesterTest(ToolTest):
    tool_name = "EmailHarvester"
    cases = [
        ToolTestCase(
            "default.txt",
            [
                {
                    "model": OSINT,
                    "data": "support@test.com",
                    "data_type": OSINTDataType.EMAIL,
                },
                {
                    "model": OSINT,
                    "data": "education@test.com",
                    "data_type": OSINTDataType.EMAIL,
                },
                {
                    "model": OSINT,
                    "data": "ceo@test.com",
                    "data_type": OSINTDataType.EMAIL,
                },
                {
                    "model": OSINT,
                    "data": "someone@test.com",
                    "data_type": OSINTDataType.EMAIL,
                },
                {
                    "model": OSINT,
                    "data": "other@test.com",
                    "data_type": OSINTDataType.EMAIL,
                },
            ],
        )
    ]
