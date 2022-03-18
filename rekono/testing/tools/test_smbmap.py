from findings.enums import EndpointProtocol
from findings.models import Endpoint
from testing.tools.base import ToolParserTest


class SmbmapParserTest(ToolParserTest):
    '''Test cases for Smbmap parser.'''

    tool_name = 'smbmap'

    expected_shares = [
        {'model': Endpoint, 'endpoint': 'shared', 'extra': 'READ, WRITE', 'protocol': EndpointProtocol.SMB},
        {
            'model': Endpoint,
            'endpoint': 'IPC$',
            'extra': '[NO ACCESS] IPC Service (Samba 4.5.4)',
            'protocol': EndpointProtocol.SMB
        }
    ]

    def test_smbmap_only_with_shares(self) -> None:
        '''Test to parse report only with shares.'''
        self.check_tool_output_parser('shares.txt', self.expected_shares)

    def test_smbmap_with_directories(self) -> None:
        '''Test to parse report with shares and directories.'''
        self.check_tool_output_parser('directories.txt', self.expected_shares)
