from testing.api.base import RekonoTestCase


class ToolsTest(RekonoTestCase):
    '''Test cases for Tools module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        self.tools = '/api/tools/'                                              # Tools API endpoints
        self.configurations = '/api/configurations/'
        self.stages = [(1, 'OSINT'), (2, 'Enumeration'), (3, 'Vulnerabilities'), (4, 'Services'), (5, 'Exploitation')]

    def test_get_tools_and_configurations(self) -> None:
        '''Test read tool and configuration data.'''
        for stage_value, stage_name in self.stages:
            # Get tools by stage
            tools = self.api_test(self.rekono.get, f'{self.tools}?stage={stage_value}&limit=100', 200)
            for tool in tools['results']:
                self.assertEqual(stage_name, tool.get('stage_name'))
                # Get configurations by tool
                configs = self.api_test(self.rekono.get, f'{self.configurations}?tool={tool.get("id")}&limit=100', 200)
                for config in configs['results']:
                    self.assertEqual(tool.get('id'), config.get('tool'))

    def test_like_dislike(self) -> None:
        '''Test like and dislike features for tools.'''
        no_likes = {'liked': False, 'likes': 0}
        tools = self.api_test(self.rekono.get, f'{self.tools}?limit=100', 200)
        for tool in tools['results']:
            self.check_fields(['liked', 'likes'], tool, no_likes)
            self.api_test(self.rekono.post, f'{self.tools}{tool["id"]}/like/', 201)      # Like tool
            self.api_test(self.rekono.get, f'{self.tools}{tool["id"]}/', 200, {}, {'liked': True, 'likes': 1})
            self.api_test(self.rekono.post, f'{self.tools}{tool["id"]}/dislike/', 204)   # Dislike tool
            self.api_test(self.rekono.get, f'{self.tools}{tool["id"]}/', 200, {}, no_likes)
