import json
import os

import yaml
from findings.models import OSINT
from tools.tools.base_tool import BaseTool


class TheHarvesterTool(BaseTool):
    
    data_types = [
        ('ips', OSINT.DataType.IP),
        ('hosts', OSINT.DataType.DOMAIN),
        ('vhosts', OSINT.DataType.DOMAIN),
        ('urls', OSINT.DataType.URL),
        ('trello_urls', OSINT.DataType.URL),
        ('emails', OSINT.DataType.EMAIL),
        ('linkedin_links', OSINT.DataType.LINK),
        ('asns', OSINT.DataType.ASN),
        ('twitter_people', OSINT.DataType.USER),
        ('linkedin_people', OSINT.DataType.USER)
    ]

    def parse_output(self, output: str) -> list:
        osint_data = []
        if os.path.isfile(self.path_output):
            with open(self.path_output) as output_file:
                data = json.load(output_file)
        for key, dt in self.data_types:
            if key in data:
                for item in data[key]:
                    osint = OSINT.objects.create(
                        data=item,
                        data_type=dt
                    )
                    osint_data.append(osint)
        return osint_data
