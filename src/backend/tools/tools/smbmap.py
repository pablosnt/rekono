from findings.enums import PathType
from findings.models import Path
from tools.tools.base_tool import BaseTool


class Smbmap(BaseTool):
    '''Smbmap tool class.'''

    def parse_plain_output(self, output: str) -> None:
        '''Parse tool plain output to create finding entities. This should be implemented by child tool classes.

        Args:
            output (str): Plain tool output
        '''
        for line in output.split('\n'):                                         # Get output by lines
            data = line.strip()
            if data and ('READ' in data or 'WRITE' in data or 'NO ACCESS' in data):     # Share entry
                share = [i.strip() for i in data.split('  ') if i.strip()]      # Get fields: disk, permissions, comment
                self.create_finding(
                    Path,
                    path=share[0],                                              # Disk
                    extra=f'[{share[1]}] {share[2]}' if len(share) >= 3 else share[1],  # Details
                    type=PathType.SHARE
                )
