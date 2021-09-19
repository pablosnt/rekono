from users.models import UserDetail
from findings.models import OSINT
from executions.models import Execution
from tools.tools.base_tool import BaseTool
import os
import json
import yaml


class TheHarvesterTool(BaseTool):
    
    file_output_enabled = True
    file_output_extension = '.json'
    configuration_file = 'api-keys.yaml'
    api_keys_config = {
        'apikeys': {
            'binaryedge': {},
            'bing': {},
            'censys': {},
            'github': {},
            'hunter': {},
            'intelx': {},
            'pentestTools': {},
            'projectDiscovery': {},
            'rocketreach': {},
            'securityTrails': {},
            'shodan': {},
            'spyse': {},
            'zoomeye': {}
        }
    }
    data_types = [
        ('ips', OSINT.DataType.IP),
        ('hosts', OSINT.DataType.DOMAIN),
        ('vhosts', OSINT.DataType.DOMAIN),
        ('urls', OSINT.DataType.URL),
        ('trello_urls', OSINT.DataType.URL),
        ('emails', OSINT.DataType.MAIL),
        ('linkedin_links', OSINT.DataType.LINK),
        ('asns', OSINT.DataType.ASN),
        ('twitter_people', OSINT.DataType.USER),
        ('linkedin_people', OSINT.DataType.USER)
    ]

    def prepare_environment(self, execution: Execution) -> None:
        details = UserDetail.objects.filter(user=execution.request.executor).first()
        for api in self.api_keys_config['apikeys'].keys():
            apikey = getattr(details, api + '_apikey')
            self.api_keys_config['apikeys'][api] = {
                'key': apikey if apikey else None
            }
        with open(self.configuration_file) as config_file:
            yaml.dump(self.api_keys_config, config_file, default_flow_style=False)


    def clean_environment(self, execution: Execution) -> None:
        if os.path.isfile(self.configuration_file):
            os.remove(self.configuration_file)

    def parse_output(self, output: str) -> list:
        osint_data = []
        if os.path.isfile(self.path_output):
            with open(self.path_output) as output_file:
                data = json.load(output_file)
        for key, dt in self.data_types:
            if key in data:
                for item in data['key']:
                    osint = OSINT.objects.create(
                        data=item,
                        data_type=dt
                    )
                    osint_data.append(osint)
        return osint_data
