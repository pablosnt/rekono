from findings.enums import DataType
from findings.models import OSINT
from testing.tools.base import ToolParserTest


class EmailFinderParserTest(ToolParserTest):
    '''Test cases for EmailFinder parser.'''

    tool_name = 'EmailFinder'

    def test_default(self) -> None:
        '''Test to parse report with emails.'''
        expected = [
            {'model': OSINT, 'data': 'support@test.com', 'data_type': DataType.EMAIL},
            {'model': OSINT, 'data': 'education@test.com', 'data_type': DataType.EMAIL},
            {'model': OSINT, 'data': 'ceo@test.com', 'data_type': DataType.EMAIL},
            {'model': OSINT, 'data': 'someone@test.com', 'data_type': DataType.EMAIL},
            {'model': OSINT, 'data': 'other@test.com', 'data_type': DataType.EMAIL},
        ]
        self.check_tool_output_parser('default.txt', expected)
