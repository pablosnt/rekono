import defusedxml.ElementTree as parser
from findings.enums import PathType, Severity
from findings.models import Path, Vulnerability
from tools.tools.base_tool import BaseTool


class Nikto(BaseTool):
    '''Nikto tool class.'''

    # Exit code ignored because Nikto report will include findings until error occurs
    ignore_exit_code = True

    def parse_output_file(self) -> None:
        '''Parse tool output file to create finding entities.'''
        http_endpoints = set(['/'])                                             # HTTP endpoints set
        root = parser.parse(self.path_output).getroot()                         # Report root
        items = root.findall('niktoscan')[-1].findall('scandetails')[0].findall('item')     # Get report items
        for item in items:                                                      # For each item
            osvdb = int(item.attrib['osvdbid'])                                 # Get OSVDB Id
            method = item.attrib['method']                                      # Get HTTP method
            description = item.findtext('description')                          # Get description value
            endpoint = item.findtext('uri')                                     # Get endpoint tag
            if description:
                self.create_finding(                                            # Create Vulnerability
                    Vulnerability,
                    name=description,
                    description=f'[{method} {endpoint}] {description}' if endpoint else f'[{method}] {description}',
                    severity=Severity.MEDIUM,
                    osvdb=f'OSVDB-{osvdb}'                                      # Get OSVDB name
                )
            if endpoint and endpoint not in http_endpoints:                     # If it's a new endpoint
                http_endpoints.add(endpoint)                                    # Add endpoint to HTTP endpoints set
                self.create_finding(Path, path=endpoint, type=PathType.ENDPOINT)    # Create Path
