from authentication.enums import AuthenticationType
from authentication.models import Authentication
from testing.api.base import RekonoApiTestCase


class AuthenticationTest(RekonoApiTestCase):
    '''Test cases for Authentication entity.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        self.endpoint = '/api/authentications/'                                 # Authentication API endpoint
        super().setUp()
        self.initialize_environment()                                           # Initialize testing environment
        # Data for testing
        self.used_data = {
            'target_port': self.target_port.id,
            'name': self.target_credential.name,
            'credential': self.target_credential.credential,
            'type': self.target_credential.type
        }
        self.models = {                                                         # Models to test __str__ method
            self.target_credential: f'{self.target_port.__str__()} - {self.target_credential.name}'
        }

    def initialize_environment(self) -> None:
        '''Initialize environment for testing.'''
        super().initialize_environment()
        self.target_credential = Authentication.objects.create(
            target_port=self.target_port,
            name='admin',
            credential='admin',
            type=AuthenticationType.BASIC
        )

    def test_create(self) -> None:
        '''Test authentication creation.'''
        self.used_data['name'] = 'regularuser'
        expected = self.used_data.copy()
        expected['credential'] = len(self.used_data['credential']) * '*'
        # Create new authentication
        content = self.api_test(self.client.post, self.endpoint, 201, data=self.used_data, expected=expected)
        self.api_test(self.client.get, f'{self.endpoint}{content["id"]}/', expected=expected)

    def test_invalid_create(self) -> None:
        '''Test authentication creation with invalid data.'''
        self.api_test(self.client.post, self.endpoint, 400, data=self.used_data)  # Target authentication already exists
        self.used_data['credential'] = ';reverseshell'
        self.api_test(self.client.post, self.endpoint, 400, data=self.used_data)   # Invalid credential value

    def test_delete(self) -> None:
        '''Test authentication deletion feature.'''
        # Delete authentication
        self.api_test(self.client.delete, f'{self.endpoint}{self.target_credential.id}/', 204)
        self.api_test(self.client.get, f'{self.endpoint}{self.target_credential.id}/', 404)
