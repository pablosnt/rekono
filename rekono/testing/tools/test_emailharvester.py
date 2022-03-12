from findings.enums import DataType
from findings.models import OSINT
from testing.tools.base import ToolParserTest


class EmailHarvesterParserTest(ToolParserTest):
    '''Test cases for EmailHarvester parser.'''

    tool_name = 'EmailHarvester'
