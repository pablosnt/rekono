import json

from findings.enums import DataType
from findings.models import OSINT

from tools.tools.base_tool import BaseTool


class Theharvester(BaseTool):
    '''theHarvester tool class.'''

    # Mapping between theHarvester types and OSINT data types
    data_types = [
        ('ips', DataType.IP),
        ('hosts', DataType.DOMAIN),
        ('vhosts', DataType.VHOST),
        ('urls', DataType.URL),
        ('trello_urls', DataType.URL),
        ('interesting_urls', DataType.URL),
        ('emails', DataType.EMAIL),
        ('linkedin_links', DataType.LINK),
        ('asns', DataType.ASN),
        ('twitter_people', DataType.USER),
        ('linkedin_people', DataType.USER)
    ]

    def parse_output_file(self) -> None:
        '''Parse tool output file to create finding entities.'''
        with open(self.path_output, 'r', encoding='utf-8') as output_file:
            data = json.load(output_file)                                       # Read output file
        for the_harvester_type, rekono_type in self.data_types:                 # For each data type
            if the_harvester_type in data:                                      # If theHarvester type in report data
                for item in data[the_harvester_type]:                           # For item associated to this type
                    self.create_finding(OSINT, data=item, data_type=rekono_type)    # Create OSINT finding
