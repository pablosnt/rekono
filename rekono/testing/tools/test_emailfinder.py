from findings.enums import DataType
from findings.models import OSINT
from testing.tools.base import ToolParserTest


class EmailFinderParserTest(ToolParserTest):
    '''Test cases for EmailFinder parser.'''

    tool_name = 'EmailFinder'
