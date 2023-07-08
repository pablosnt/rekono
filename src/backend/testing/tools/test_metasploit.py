from findings.models import Exploit
from testing.tools.base import ToolParserTest


class MetasploitParserTest(ToolParserTest):
    '''Test cases for Metasploit parser.'''

    tool_name = 'Metasploit'

    def test_metasploit_with_exploits(self) -> None:
        '''Test to parse report with exploits.'''
        expected = [
            {
                'model': Exploit,
                'title': 'HP Data Protector Encrypted Communication Remote Command Execution',
                'reference': 'exploit/windows/misc/hp_dataprotector_encrypted_comms'
            },
            {
                'model': Exploit,
                'title': 'Ruby on Rails ActionPack Inline ERB Code Execution',
                'reference': 'exploit/multi/http/rails_actionpack_inline_exec'
            },
            {
                'model': Exploit,
                'title': 'Xymon Daemon Gather Information',
                'reference': 'auxiliary/gather/xymon_info'
            },
            {
                'model': Exploit,
                'title': 'Xymon useradm Command Execution',
                'reference': 'exploit/unix/webapp/xymon_useradm_cmd_exec'
            }
        ]
        super().check_tool_output_parser('exploits.txt', expected)

    def test_metasploit_without_exploits(self) -> None:
        '''Test to parse an empty report.'''
        super().check_tool_output_parser('nothing.txt', [])
