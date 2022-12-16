from authentications.enums import AuthenticationType
from authentications.models import Authentication
from testing.api.base import RekonoApiTestCase


class AuthenticationTest(RekonoApiTestCase):
    '''Test cases for Authentication entity.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        self.endpoint = '/api/authentications/'                                 # Authentication API endpoint
        super().setUp()
        super().initialize_environment()                                        # Initialize testing environment
        # Data for testing
        self.data = {
            'target_port': self.target_port.id,
            'name': 'admin',
            'credential': 'admin',
            'type': AuthenticationType.BASIC
        }

    def test_create(self) -> None:
        '''Test authentication creation.'''
        self.data['name'] = 'regularuser'
        expected = self.data.copy()
        expected['credential'] = len(self.data['credential']) * '*'             # Credential will be protected
        # Create new authentication
        content = self.api_test(self.client.post, self.endpoint, 201, data=self.data, expected=expected)
        self.api_test(self.client.get, f'{self.endpoint}{content["id"]}/', expected=expected)

    def test_create_with_invalid_target_port(self) -> None:
        '''Test authentication creation with invalid target port.'''
        self.data['target_port'] = self.target_port
        Authentication.objects.create(**self.data)                              # Create authentication
        self.data['target_port'] = self.target_port.id
        self.api_test(self.client.post, self.endpoint, 400, data=self.data)     # Authentication already exists

    def test_create_with_invalid_credential(self) -> None:
        '''Test authentication creation with invalid credential.'''
        self.data['credential'] = ';reverseshell'
        self.api_test(self.client.post, self.endpoint, 400, data=self.data)     # Invalid credential value

    def test_delete(self) -> None:
        '''Test authentication deletion feature.'''
        self.data['target_port'] = self.target_port
        authentication = Authentication.objects.create(**self.data)             # Create authentication
        self.api_test(self.client.delete, f'{self.endpoint}{authentication.id}/', 204)      # Delete authentication
        self.api_test(self.client.get, f'{self.endpoint}{authentication.id}/', 404)

    def test_model_representation(self) -> None:
        '''Test __str__ method for authentication model.'''
        self.data['target_port'] = self.target_port
        authentication = Authentication.objects.create(**self.data)             # Create authentication
        self.models = {                                                         # Models to test __str__ method
            authentication: f'{self.target_port.__str__()} - {authentication.name}'
        }
        super().test_model_representation()
