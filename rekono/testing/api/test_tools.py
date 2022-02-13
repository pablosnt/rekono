from testing.api.test_base import RekonoTestCase
from tools.enums import IntensityRank
from tools.models import Argument, Input, Intensity, Output


class ToolsTest(RekonoTestCase):
    '''Test cases for Tools module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        self.tools = '/api/tools/'                                              # Tools API endpoints
        self.configurations = '/api/configurations/'
        super().setUp()
        super().initialize_environment()                                        # Initialize testing environment
        # Data for testing
        self.stages = [(1, 'OSINT'), (2, 'Enumeration'), (3, 'Vulnerabilities'), (4, 'Services'), (5, 'Exploitation')]
        self.intensity = Intensity.objects.filter(tool=self.tool).first()
        self.argument = Argument.objects.filter(tool=self.tool).first()
        self.input = Input.objects.filter(argument=self.argument).first()
        self.output = Output.objects.filter(configuration=self.configuration).first()
        self.models = {                                                         # Models to test __str__ method
            self.tool: self.tool.name,
            self.configuration: f'{self.tool.name} - {self.configuration.name}',
            self.intensity: f'{self.tool.name} - {IntensityRank(self.intensity.value).name}',
            self.argument: f'{self.tool.__str__()} - {self.argument.name}',
            self.input: f'{self.argument.__str__()} - {self.input.type.__str__()}',
            self.output: f'{self.configuration.__str__()} - {self.output.type.__str__()}',
        }

    def test_get_tools_and_configurations(self) -> None:
        '''Test read tool and configuration data.'''
        for stage_value, stage_name in self.stages:
            # Get tools by stage
            tools = self.api_test(self.client.get, f'{self.tools}?stage={stage_value}&limit=100')
            for tool in tools['results']:
                self.assertEqual(stage_name, tool.get('stage_name'))
                # Get configurations by tool
                configs = self.api_test(self.client.get, f'{self.configurations}?tool={tool.get("id")}&limit=100')
                for config in configs['results']:
                    self.assertEqual(tool.get('id'), config.get('tool'))

    def test_like_dislike(self) -> None:
        '''Test like and dislike features for tools.'''
        no_likes = {'liked': False, 'likes': 0}
        tools = self.api_test(self.client.get, f'{self.tools}?limit=100', 200)
        for tool in tools['results']:
            self.check_fields(['liked', 'likes'], tool, no_likes)
            self.api_test(self.client.post, f'{self.tools}{tool["id"]}/like/', 201)      # Like tool
            self.api_test(self.client.get, f'{self.tools}{tool["id"]}/', expected={'liked': True, 'likes': 1})
            self.api_test(self.client.post, f'{self.tools}{tool["id"]}/dislike/', 204)   # Dislike tool
            self.api_test(self.client.get, f'{self.tools}{tool["id"]}/', expected=no_likes)
