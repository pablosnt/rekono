from testing.api.base import RekonoApiTestCase


class TargetsTest(RekonoApiTestCase):
    '''Test cases for Target entity from Targets module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        self.endpoint = '/api/targets/'                                         # Targets API endpoint
        super().setUp()
        super().initialize_environment()                                        # Initialize testing environment
        # Data for testing
        self.used_data = {'target': self.target.target, 'project': self.project.id}
        self.targets_data = [
            ('10.10.10.1', 'Private IP'),                                       # Private IP
            ('1.1.1.1', 'Public IP'),                                           # Public IP
            ('10.10.10.0/24', 'Network'),                                       # Network
            ('10.10.10.1-20', 'IP range'),                                      # IP range
            ('nmap.org', 'Domain')                                              # Domain
        ]
        self.models = {self.target: self.target.target}                         # Models to test __str__ method

    def test_create(self) -> None:
        '''Test target creation feature with different target types.'''
        data = {'project': self.project.id}
        for target, type in self.targets_data:
            data['target'] = target
            expected = data
            expected['type'] = type
            self.api_test(self.client.post, self.endpoint, 201, data=data, expected=expected)       # Create target

    def test_unauthorized_create(self) -> None:
        '''Test target creation feature with user that doesn't belong to related project.'''
        self.used_data['target'] = '10.10.10.2'
        self.api_test(self.other_client.post, self.endpoint, 403, data=self.used_data)  # User is not a project member

    def test_invalid_create(self) -> None:
        '''Test target creation feature with invalid data.'''
        self.api_test(self.client.post, self.endpoint, 400, data=self.used_data)    # Target already exists
        self.used_data['target'] = 'invalid'
        self.api_test(self.client.post, self.endpoint, 400, data=self.used_data)    # Invalid target
        self.used_data['target'] = '127.0.0.1'
        self.api_test(self.client.post, self.endpoint, 400, data=self.used_data)    # Invalid internal target

    def test_delete(self) -> None:
        '''Test target deletion feature.'''
        self.api_test(self.client.delete, f'{self.endpoint}{self.target.id}/', 204)     # Delete target
        self.api_test(self.client.get, f'{self.endpoint}{self.target.id}/', 404)        # Check target not found


class TargetPortsTest(RekonoApiTestCase):
    '''Test cases for Target Port entity from Targets module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        self.endpoint = '/api/target-ports/'                                    # Target Ports API endpoint
        super().setUp()
        super().initialize_environment()                                        # Initialize testing environment
        # Data for testing
        self.used_data = {'target': self.target.id, 'port': self.target_port.port}
        self.models = {                                                         # Models to test __str__ method
            self.target_port: f'{self.target.target} - {self.target_port.port}'
        }

    def test_create(self) -> None:
        '''Test target port creation feature.'''
        self.used_data['port'] = 8080
        # Create new target port
        content = self.api_test(self.client.post, self.endpoint, 201, data=self.used_data, expected=self.used_data)
        self.api_test(self.client.get, f'{self.endpoint}{content["id"]}/', expected=self.used_data)

    def test_invalid_create(self) -> None:
        '''Test target port creation feature with invalid data.'''
        self.api_test(self.client.post, self.endpoint, 400, data=self.used_data)    # Target port already exists
        self.used_data['port'] = 0
        self.api_test(self.client.post, self.endpoint, 400, data=self.used_data)    # Invalid port number

    def test_delete(self) -> None:
        '''Test target port deletion feature.'''
        self.api_test(self.client.delete, f'{self.endpoint}{self.target_port.id}/', 204)    # Delete target port
        self.api_test(self.client.get, f'{self.endpoint}{self.target_port.id}/', 404)
