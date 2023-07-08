from findings.models import Exploit

from tools.tools.base_tool import BaseTool


class Metasploit(BaseTool):
    '''Metasploit tool class.'''

    def parse_plain_output(self, output: str) -> None:
        '''Parse tool plain output to create finding entities. This should be implemented by child tool classes.

        Args:
            output (str): Plain tool output
        '''
        entry = 0
        for line in output.split('\n'):                                         # Get output by lines
            if line.strip() and line.strip().startswith(str(entry)):            # Expected line
                entry += 1
                data = [i.strip() for i in line.strip().split('  ') if i]       # Clean line
                self.create_finding(Exploit, title=data[-1], reference=data[1])
