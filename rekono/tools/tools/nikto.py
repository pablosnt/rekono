import xml.etree.ElementTree as parser

from findings.enums import Severity
from findings.models import Endpoint, Vulnerability
from tools.tools.base_tool import BaseTool


class NiktoTool(BaseTool):
    '''Nikto tool class.'''

    # Exit code ignored because Nikto report will include findings until error occurs
    ignore_exit_code = True

    def parse_output_file(self) -> None:
        '''Parse tool output file to create finding entities.'''
        http_endpoints = set()                                                  # HTTP endpoints set
        root = parser.parse(self.path_output).getroot()                         # Report root
        items = root.findall('niktoscan')[-1].findall('scandetails')[0].findall('item')     # Get report items
        for item in items:                                                      # For each item
            osvdb = int(item.attrib['osvdbid'])                                 # Get OSVDB Id
            method = item.attrib['method']                                      # Get HTTP method
            name = None
            description_tag = item.find('description')                          # Get description tag
            if description_tag:
                description = description_tag.text                              # Get description value
                name = description                                              # Name initialization to description
            if osvdb:                                                           # If OSVDB exists
                name = str(osvdb)                                               # Set OSCDB as name
            endpoint = None
            endpoint_tag = item.find('uri')                                     # Get endpoint tag
            if endpoint_tag:
                endpoint = endpoint_tag.text                                    # Get endpoint value
                if endpoint and '<![DATA[' in endpoint:
                    endpoint = endpoint.split('<![DATA[', 1)[1].rsplit(']]>', 1)[0]     # Clean endpoint value
            if description:
                self.create_finding(                                            # Create Vulnerability
                    Vulnerability,
                    name=name,
                    description=f'[{method} {endpoint}] {description}' if endpoint else f'[{method}] {description}',
                    severity=Severity.MEDIUM,
                    osvdb=osvdb
                )
            if endpoint and endpoint not in http_endpoints:                     # If it's a new endpoint
                http_endpoints.add(endpoint)                                    # Add endpoint to HTTP endpoints set
                self.create_finding(Endpoint, endpoint=endpoint)                # Create Endpoint
