from testing.api.base import RekonoApiTestCase


class InputTechnologiesTest(RekonoApiTestCase):
    '''Test cases for Input Technology entity from Parameters module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        self.endpoint = '/api/parameters/technologies/'                         # Input Technologies API endpoint
        super().setUp()
        super().initialize_environment()                                        # Initialize testing environment
        # Data for testing
        self.used_data = {
            'target': self.target.id,
            'name': self.input_technology.name,
            'version': self.input_technology.version
        }
        self.models = {                                                         # Models to test __str__ method
            self.input_technology: (
                f'{self.target.__str__()} - {self.input_technology.name} - {self.input_technology.version}'
            )
        }

    def test_create(self) -> None:
        '''Test input technology creation.'''
        self.used_data['name'] = 'Joomla'
        # Create new input technology
        content = self.api_test(self.client.post, self.endpoint, 201, data=self.used_data, expected=self.used_data)
        self.api_test(self.client.get, f'{self.endpoint}{content["id"]}/', expected=self.used_data)

    def test_invalid_create(self) -> None:
        '''Test input technology creation with invalid data.'''
        self.api_test(self.client.post, self.endpoint, 400, data=self.used_data)   # Input technology already exists
        self.used_data['name'] = 'Word;Press'
        self.api_test(self.client.post, self.endpoint, 400, data=self.used_data)   # Invalid name value

    def test_delete(self) -> None:
        '''Test input technology deletion feature.'''
        # Delete input technology
        self.api_test(self.client.delete, f'{self.endpoint}{self.input_technology.id}/', 204)
        self.api_test(self.client.get, f'{self.endpoint}{self.input_technology.id}/', 404)


class InputVulnerabilitiesTest(RekonoApiTestCase):
    '''Test cases for Input Vulnerability entity from Parameters module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        self.endpoint = '/api/parameters/vulnerabilities/'                      # Input Technologies API endpoint
        super().setUp()
        super().initialize_environment()                                        # Initialize testing environment
        # Data for testing
        self.used_data = {'target': self.target.id, 'cve': self.input_vulnerability.cve}
        self.models = {                                                         # Models to test __str__ method
            self.input_vulnerability: f'{self.target.__str__()} - {self.input_vulnerability.cve}'
        }

    def test_create(self) -> None:
        '''Test input vulnerability creation.'''
        self.used_data['cve'] = 'CVE-2022-2022'
        # Create new input vulnerability
        content = self.api_test(self.client.post, self.endpoint, 201, data=self.used_data, expected=self.used_data)
        self.api_test(self.client.get, f'{self.endpoint}{content["id"]}/', expected=self.used_data)

    def test_invalid_create(self) -> None:
        '''Test input vulnerability creation with invalid data.'''
        self.api_test(self.client.post, self.endpoint, 400, data=self.used_data)   # Input vulnerability already exists
        self.used_data['cve'] = 'CVE'
        self.api_test(self.client.post, self.endpoint, 400, data=self.used_data)   # Invalid name value

    def test_delete(self) -> None:
        '''Test input vulnerability deletion feature.'''
        # Delete input vulnerability
        self.api_test(self.client.delete, f'{self.endpoint}{self.input_vulnerability.id}/', 204)
        self.api_test(self.client.get, f'{self.endpoint}{self.input_vulnerability.id}/', 404)
