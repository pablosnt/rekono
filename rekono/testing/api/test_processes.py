from testing.api.base import RekonoApiTestCase
from tools.models import Configuration, Tool


class ProcessesTest(RekonoApiTestCase):
    '''Test cases for Process entity from Processes module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        self.endpoint = '/api/processes/'                                       # Processes API endpoint
        super().setUp()
        super().initialize_environment()                                        # Initialize testing environment
        # Data for testing
        self.used_data = {'name': self.process.name, 'description': self.process.description, 'tags': self.process.tags}
        self.new_data = {'name': 'New Process', 'description': 'New process', 'tags': ['new']}
        self.models = {self.process: self.process.name}                         # Models to test __str__ method

    def test_create(self) -> None:
        '''Test process creation feature.'''
        # Create new process
        content = self.api_test(self.client.post, self.endpoint, 201, data=self.new_data, expected=self.new_data)
        self.api_test(self.client.get, f'{self.endpoint}{content["id"]}/', expected=content)

    def test_invalid_create(self) -> None:
        '''Test process creation with invalid data.'''
        self.api_test(self.client.post, self.endpoint, 400, data=self.used_data)    # Process name already exists

    def test_update(self) -> None:
        '''Test process update feature.'''
        self.api_test(                                                          # Update process
            self.client.put, f'{self.endpoint}{self.process.id}/',
            data=self.new_data, expected=self.new_data
        )
        self.api_test(self.client.get, f'{self.endpoint}{self.process.id}/', expected=self.new_data)

    def test_invalid_update(self) -> None:
        '''Test process update with invalid data.'''
        # Create new process
        content = self.api_test(self.client.post, self.endpoint, 201, data=self.new_data, expected=self.new_data)
        # Process name already exists
        self.api_test(self.client.put, f'{self.endpoint}{content["id"]}/', 400, data=self.used_data)

    def test_delete(self) -> None:
        '''Test process deletion feature.'''
        self.api_test(self.client.delete, f'{self.endpoint}{self.process.id}/', 204)    # Delete process
        self.api_test(self.client.get, f'{self.endpoint}{self.process.id}/', 404)       # Check process not found

    def test_unauthorized_delete(self) -> None:
        '''Test process deletion feature without Admin or process creator.'''
        # Change user role to Auditor, because Admins can delete all processes
        data = {'role': 'Auditor'}
        self.api_test(self.client.put, f'/api/users/{self.other.id}/role/', data=data, expected=data)
        self.api_test(self.other_client.delete, f'{self.endpoint}{self.process.id}/', 403)      # User is not authorized

    def test_like_dislike(self) -> None:
        '''Test like and dislike features for processes.'''
        count = self.api_test(self.client.get, f'{self.endpoint}?order=-name')['count']  # Get total count of processes
        # Like testing process
        self.api_test(self.client.post, f'{self.endpoint}{self.process.id}/like/', 201)
        self.api_test(self.client.get, f'{self.endpoint}{self.process.id}/', expected={'liked': True, 'likes': 1})
        self.api_test(self.client.get, f'{self.endpoint}?liked=true', expected={'count': 1})
        self.api_test(self.client.get, f'{self.endpoint}?liked=false', expected={'count': count - 1})
        # Dislike testing process
        self.api_test(self.client.post, f'{self.endpoint}{self.process.id}/dislike/', 204)
        self.api_test(self.client.get, f'{self.endpoint}{self.process.id}/', expected={'liked': False, 'likes': 0})
        self.api_test(self.client.get, f'{self.endpoint}?liked=true', expected={'count': 0})
        self.api_test(self.client.get, f'{self.endpoint}?liked=false', expected={'count': count})


class StepsTest(RekonoApiTestCase):
    '''Test cases for Step entity from Processes module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        self.endpoint = '/api/steps/'                                           # Steps API endpoint
        super().setUp()
        super().initialize_environment()                                        # Initialize testing environment
        self.new_step_tool = Tool.objects.get(name='theHarvester')              # Tool and Configuration for testing
        self.new_step_config = Configuration.objects.get(tool=self.new_step_tool, default=True)
        self.new_data = {                                                       # Data for testing
            'tool_id': self.new_step_tool.id,
            'configuration_id': self.new_step_config.id,
            'process': self.process.id
        }
        self.models = {                                                         # Models to test __str__ method
            self.step: f'{self.process.__str__()} - {self.nmap_configuration.__str__()}'
        }

    def test_create(self) -> None:
        '''Test step creation feature.'''
        content = self.api_test(self.client.post, self.endpoint, 201, data=self.new_data)   # Create new step
        self.assertEqual(self.process.id, content['process'])
        self.check_fields(['id', 'name'], content['tool'], self.new_step_tool)
        self.check_fields(['id', 'name'], content['configuration'], self.new_step_config)
        self.assertEqual(1, content['priority'])
        self.api_test(self.client.get, f'{self.endpoint}{content["id"]}/', expected=content)

    def test_create_without_configuration(self) -> None:
        '''Test step creation feature without set one configuration.'''
        self.new_data.pop('configuration_id')                                   # Remove configuration from data
        # Default theHarvester configuration will be used
        self.test_create()

    def test_create_with_invalid_configuration(self) -> None:
        '''Test step creation feature with invalid configuration.'''
        # Invalid config for theHarvester
        invalid_config = Configuration.objects.get(tool__name='Dirsearch', default=True)
        self.new_data['configuration_id'] = invalid_config.id
        # Default theHarvester configuration will be used
        self.test_create()

    def test_invalid_create(self) -> None:
        '''Test step creation feature with invalid data.'''
        self.new_data['tool_id'] = self.nmap.id
        self.new_data['configuration_id'] = self.nmap_configuration.id
        # Step with this tool and configuration already exists
        self.api_test(self.client.post, self.endpoint, 400, data=self.new_data)

    def test_update(self) -> None:
        '''Test step priority update feature.'''
        data = {'priority': 2}
        # Update step priority
        self.api_test(self.client.put, f'{self.endpoint}{self.step.id}/', data=data, expected=data)
        self.api_test(self.client.get, f'{self.endpoint}{self.step.id}/', expected=data)

    def test_invalid_update(self) -> None:
        '''Test step priority update feature with invalid data.'''
        # Invalid priority
        self.api_test(self.client.put, f'{self.endpoint}{self.step.id}/', 400, data={'priority': -1})

    def test_delete(self) -> None:
        '''Test step deletion feature.'''
        self.api_test(self.client.delete, f'{self.endpoint}{self.step.id}/', 204)    # Delete step
        self.api_test(self.client.get, f'{self.endpoint}{self.step.id}/', 404)       # Check step is not found
