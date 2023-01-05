from testing.api.base import RekonoApiTestCase
from tools.enums import IntensityRank
from tools.models import Argument, Input, Intensity, Output


class ToolsTest(RekonoApiTestCase):
    '''Test cases for Tools module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        self.tools = '/api/tools/'                                              # Tools API endpoints
        self.configurations = '/api/configurations/'
        super().setUp()
        super().initialize_environment()                                        # Initialize testing environment
        # Data for testing
        self.stages = [(1, 'OSINT'), (2, 'Enumeration'), (3, 'Vulnerabilities'), (4, 'Services'), (5, 'Exploitation')]
        self.intensity = Intensity.objects.filter(tool=self.nmap).first()
        self.argument = Argument.objects.filter(tool=self.nmap).first()
        self.input = Input.objects.filter(argument=self.argument).first()
        self.output = Output.objects.filter(configuration=self.nmap_configuration).first()
        self.models = {                                                         # Models to test __str__ method
            self.nmap: self.nmap.name,
            self.nmap_configuration: f'{self.nmap.name} - {self.nmap_configuration.name}',
            self.intensity: f'{self.nmap.name} - {IntensityRank(self.intensity.value).name}',
            self.argument: f'{self.nmap.__str__()} - {self.argument.name}',
            self.input: f'{self.argument.__str__()} - {self.input.type.__str__()}',
            self.output: f'{self.nmap_configuration.__str__()} - {self.output.type.__str__()}',
        }

    def test_get_tools_and_configurations(self) -> None:
        '''Test read tool and configuration data.'''
        for stage_value, stage_name in self.stages:
            # Get tools by stage
            tools = self.api_test(self.client.get, f'{self.tools}?configurations__stage={stage_value}&limit=100')
            for tool in tools['results']:
                # Get configurations by tool
                configs = self.api_test(
                    self.client.get, f'{self.configurations}?tool={tool.get("id")}&stage={stage_value}&limit=100'
                )
                for config in configs['results']:
                    self.assertEqual(tool.get('id'), config.get('tool'))
                    self.assertEqual(stage_name, config.get('stage_name'))

    def test_like_dislike(self) -> None:
        '''Test like and dislike features for tools.'''
        no_likes = {'liked': False, 'likes': 0}
        tools = self.api_test(self.client.get, f'{self.tools}?limit=100', 200)
        for tool in tools['results']:
            self.check_fields(['liked', 'likes'], tool, no_likes)
            self.api_test(self.client.post, f'{self.tools}{tool["id"]}/like/', 201)      # Like tool
            self.api_test(self.client.get, f'{self.tools}{tool["id"]}/', expected={'liked': True, 'likes': 1})
            self.api_test(self.client.get, f'{self.tools}?liked=true', expected={'count': 1})
            self.api_test(self.client.get, f'{self.tools}?liked=false', expected={'count': tools['count'] - 1})
            self.api_test(self.client.post, f'{self.tools}{tool["id"]}/dislike/', 204)   # Dislike tool
            self.api_test(self.client.get, f'{self.tools}{tool["id"]}/', expected=no_likes)
            self.api_test(self.client.get, f'{self.tools}?liked=true', expected={'count': 0})
            self.api_test(self.client.get, f'{self.tools}?liked=false', expected={'count': tools['count']})
