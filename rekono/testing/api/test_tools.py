from testing.api.base import RekonoTestCase


class ToolsTest(RekonoTestCase):
    '''Test cases for Tools module.'''

    def test_get_tools_and_configurations(self) -> None:
        '''Test read tool and configuration data.'''
        stages = [(1, 'OSINT'), (2, 'Enumeration'), (3, 'Vulnerabilities'), (4, 'Services'), (5, 'Exploitation')]
        for stage_value, stage_name in stages:
            # Get tools by stage
            tools = self.api_test(self.rekono.get, f'/api/tools/?stage={stage_value}&limit=100', 200)
            for tool in tools['results']:
                self.assertEqual(stage_name, tool.get('stage_name'))
                # Get configurations by tool
                configs = self.api_test(self.rekono.get, f'/api/configurations/?tool={tool.get("id")}&limit=100', 200)
                for config in configs['results']:
                    self.assertEqual(tool.get('id'), config.get('tool'))
