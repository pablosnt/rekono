import json

from findings.models import Exploit
from tools.tools.base_tool import BaseTool


class Searchsploit(BaseTool):
    '''SearchSploit tool class.'''

    def parse_output_file(self) -> None:
        '''Parse tool output file to create finding entities.'''
        with open(self.path_output, 'r', encoding='utf-8') as output_file:
            data = json.load(output_file)                                       # Read output file
        for exploit in data.get('RESULTS_EXPLOIT'):                             # For each exploit
            edb_id = exploit.get('EDB-ID')                                      # Get Exploit-DB Id
            self.create_finding(                                                # Create exploit finding
                Exploit,
                title=exploit.get('Title'),
                edb_id=int(edb_id) if edb_id else None,
                reference=f'https://www.exploit-db.com/exploits/{edb_id}' if edb_id else None
            )
