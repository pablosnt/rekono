from findings.models import Exploit
from tools.tools.base_tool import BaseTool


class MetasploitTool(BaseTool):
    '''Metasploit tool class.'''

    def parse_output_file(self) -> None:
        '''Parse tool output file to create finding entities.'''
        with open(self.path_output, 'r') as output_file:
            entry = 0
            for line in output_file:
                if line.strip() and line.strip().startswith(str(entry)):
                    entry += 1
                    data = [i.strip() for i in line.strip().split('  ') if i]
                    self.create_finding(Exploit, title=data[-1], reference=data[1])
