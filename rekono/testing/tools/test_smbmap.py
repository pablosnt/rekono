from findings.enums import PathType
from findings.models import Path
from testing.tools.base import ToolParserTest


class SMBMapParserTest(ToolParserTest):
    '''Test cases for SMBMap parser.'''

    tool_name = 'SMBMap'

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        self.expected_shares = [
            {'model': Path, 'path': 'shared', 'extra': 'READ, WRITE', 'type': PathType.SHARE},
            {
                'model': Path,
                'path': 'IPC$',
                'extra': '[NO ACCESS] IPC Service (Samba 4.5.4)',
                'type': PathType.SHARE
            }
        ]

    def test_smbmap_only_with_shares(self) -> None:
        '''Test to parse report only with shares.'''
        self.check_tool_output_parser('shares.txt', self.expected_shares)

    def test_smbmap_with_directories(self) -> None:
        '''Test to parse report with shares and directories.'''
        self.check_tool_output_parser('directories.txt', self.expected_shares)
