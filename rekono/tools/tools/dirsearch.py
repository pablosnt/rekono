import json

from findings.enums import PathType
from findings.models import Path
from tools.tools.base_tool import BaseTool


class Dirsearch(BaseTool):
    '''Dirsearch tool class.'''

    # Exit code ignored because Dirsearch report will include findings until error occurs
    ignore_exit_code = True

    def parse_output_file(self) -> None:
        '''Parse tool output file to create finding entities.'''
        with open(self.path_output, 'r', encoding='utf-8') as output_file:
            data = json.load(output_file)                                       # Read output file
        for url in data.get('results', []):                                     # For each URL
            for item in url.values():                                           # For each item
                for endpoint in item:                                           # For each endpoint
                    self.create_finding(                                        # Create Path
                        Path,
                        path=endpoint.get('path', ''),
                        status=endpoint.get('status', 0),
                        type=PathType.ENDPOINT
                    )
