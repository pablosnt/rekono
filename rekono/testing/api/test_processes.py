from typing import Any, Dict

from testing.api.base import RekonoTestCase
from tools.models import Configuration, Tool


class ProcessesTestCase(RekonoTestCase):
    '''Base test case for Processes module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        self.processes = '/api/processes/'                                      # Processes API endpoint
        self.steps = '/api/steps/'                                              # Steps API endpoint
        # Data for testing
        self.create_data = {'name': 'Process Test', 'description': 'Process Test', 'tags': ['test']}
        self.new_data = {'name': 'New Process', 'description': 'New process', 'tags': ['test', 'new']}
        # Create testing process
        self.process = self.api_test(self.rekono.post, self.processes, 201, self.create_data, self.create_data)
        self.step = self.create_step(self.process['id'], 'Nmap')                # Create testing step

    def create_step(self, process_id: int, tool_name: str, status_code: int = 201) -> Dict[str, Any]:
        '''Create step and check response.

        Args:
            process_id (int): Process Id where the step will be created
            tool_name (str): Tool name to include in the step
            status_code (int, optional): Expected HTTP status code. Defaults to 201.

        Returns:
            Dict[str, Any]: Created step data
        '''
        tool = Tool.objects.get(name=tool_name)                                 # Get tool by name
        configuration = Configuration.objects.get(tool=tool, default=True)      # Get default configuration for tool
        data = {'process': process_id, 'tool_id': tool.id, 'configuration_id': configuration.id}
        content = self.api_test(self.rekono.post, self.steps, status_code, data)    # Create step
        if status_code == 201:                                                  # Step created successfully: check data
            self.assertEqual(process_id, content['process'])
            self.assertEqual(tool.name, content['tool']['name'])
            self.assertEqual(configuration.name, content['configuration']['name'])
            self.assertEqual(1, content['priority'])
        return content


class ProcessesTest(ProcessesTestCase):
    '''Test cases for Process entity from Processes module.'''        

    def test_create(self) -> None:
        '''Test process creation feature.'''
        # Create new process
        content = self.api_test(self.rekono.post, self.processes, 201, self.new_data, self.new_data)
        self.api_test(self.rekono.get, f'{self.processes}{content["id"]}/', 200, {}, content)   # Check process creation

    def test_invalid_create(self) -> None:
        '''Test process creation with invalid data.'''
        self.api_test(self.rekono.post, self.processes, 400, self.create_data)  # Process name already exists

    def test_update(self) -> None:
        '''Test process update feature.'''
        data = {'name': 'Updated process', 'description': 'Updated process', 'tags': ['updated']}
        self.api_test(self.rekono.put, f'{self.processes}{self.process["id"]}/', 200, data, data)   # Update process
        self.api_test(self.rekono.get, f'{self.processes}{self.process["id"]}/', 200, {}, data)     # Check process data

    def test_invalid_update(self) -> None:
        '''Test process update with invalid data.'''
        # Create new process
        content = self.api_test(self.rekono.post, self.processes, 201, self.new_data, self.new_data)
        # Process name already exists
        self.api_test(self.rekono.put, f'{self.processes}{content["id"]}/', 400, self.create_data)

    def test_delete(self) -> None:
        '''Test process deletion feature.'''
        self.api_test(self.rekono.delete, f'{self.processes}{self.process["id"]}/', 204)    # Delete process
        self.api_test(self.rekono.get, f'{self.processes}{self.process["id"]}/', 404)       # Check process not found

    def test_like_dislike(self) -> None:
        '''Test like and dislike features for processes.'''
        # Like testing process
        self.api_test(self.rekono.post, f'{self.processes}{self.process["id"]}/like/', 201)
        self.api_test(self.rekono.get, f'{self.processes}{self.process["id"]}/', 200, {}, {'liked': True, 'likes': 1})
        # Dislike testing process
        self.api_test(self.rekono.post, f'{self.processes}{self.process["id"]}/dislike/', 204)
        self.api_test(self.rekono.get, f'{self.processes}{self.process["id"]}/', 200, {}, {'liked': False, 'likes': 0})


class StepsTest(ProcessesTestCase):
    '''Test cases for Step entity from Processes module.'''

    def test_create(self) -> None:
        '''Test step creation feature.'''
        content = self.create_step(self.process['id'], 'theHarvester')
        self.api_test(self.rekono.get, f'{self.steps}{content["id"]}/', 200, {}, content)

    def test_create_without_configuration(self) -> None:
        '''Test step creation feature without set one configuration.'''
        tool = Tool.objects.get(name='Dirsearch')                               # Get dirsearch tool
        configuration = Configuration.objects.get(tool=tool, default=True)      # Get dirsearch default configuration
        data = {'process': self.process['id'], 'tool_id': tool.id}              # Creation data without configuration
        expected = {'process': self.process['id'], 'priority': 1}
        content = self.api_test(self.rekono.post, self.steps, 201, data, expected)      # Create step
        self.assertEqual(tool.name, content['tool']['name'])
        self.assertEqual(configuration.name, content['configuration']['name'])  # Check default configuration is used

    def test_create_with_invalid_configuration(self) -> None:
        '''Test step creation feature with invalid configuration.'''
        tool = Tool.objects.get(name='Dirsearch')                               # Get dirsearch tool
        configuration = Configuration.objects.get(tool=tool, default=True)      # Get dirsearch default configuration
        other_tool = Tool.objects.get(name='Nmap')                              # Get other tool
        invalid = Configuration.objects.get(tool=other_tool, default=True)
        # Creation data with invalid configuration for dirsearch
        data = {'process': self.process['id'], 'tool_id': tool.id, 'configuration_id': invalid.id}
        expected = {'process': self.process['id'], 'priority': 1}
        content = self.api_test(self.rekono.post, self.steps, 201, data, expected)   # Create step
        self.assertEqual(tool.name, content['tool']['name'])
        self.assertEqual(configuration.name, content['configuration']['name'])  # Check dirsearch configuration is used

    def test_invalid_create(self) -> None:
        '''Test step creation feature with invalid data.'''
        # Step with this tool and configuration already exists
        self.create_step(self.process['id'], 'Nmap', 400)

    def test_update(self) -> None:
        '''Test step priority update feature.'''
        data = {'priority': 2}
        self.api_test(self.rekono.put, f'{self.steps}{self.step["id"]}/', 200, data, data)   # Update step priority
        self.api_test(self.rekono.get, f'{self.steps}{self.step["id"]}/', 200, {}, data)     # Check step priority

    def test_invalid_update(self) -> None:
        '''Test step priority update feature with invalid data.'''
        self.api_test(self.rekono.put, f'{self.steps}{self.step["id"]}/', 400, {'priority': -1})     # Invalid priority

    def test_delete(self) -> None:
        '''Test step deletion feature.'''
        self.api_test(self.rekono.delete, f'{self.steps}{self.step["id"]}/', 204)    # Delete step
        self.api_test(self.rekono.get, f'{self.steps}{self.step["id"]}/', 404)       # Check step is not found
