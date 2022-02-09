from rest_framework.test import APIClient
from testing.unit.base import RekonoTestCase
from users.models import User


class TargetsTest(RekonoTestCase):
    '''Test cases for Targets module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        data = {'name': 'Project Test', 'description': 'Project Test', 'tags': ['test']}
        self.project = self.api_test(self.rekono.post, '/api/projects/', 201, data, data)   # Create project for testing

    def test_targets(self) -> None:
        '''Test targets creation, including ports and endpoints.'''
        data = {'target': 'invalid', 'project': self.project['id']}
        self.api_test(self.rekono.post, '/api/targets/', 400, data)             # Invalid target
        data['target'] = '10.10.10.10'
        expected = data
        expected['type'] = 'Private IP'
        target = self.api_test(self.rekono.post, '/api/targets/', 201, data, expected)      # Create target
        self.api_test(self.rekono.post, '/api/targets/', 400, data)             # Existing target
        data = {'target': target['id'], 'port': -1}
        self.api_test(self.rekono.post, '/api/target-ports/', 400, data)        # Invalid port number
        data['port'] = 80
        target_port = self.api_test(self.rekono.post, '/api/target-ports/', 201, data, data)    # Create target port
        self.api_test(self.rekono.post, '/api/target-ports/', 400, data)        # Existing target port
        data = {'target_port': target_port['id'], 'endpoint': ';invalid;endpoint;'}
        self.api_test(self.rekono.post, '/api/target-endpoints/', 400, data)    # Invalid endpoint value
        data['endpoint'] = '/robots.txt'
        # Create target endpoint
        target_endpoint = self.api_test(self.rekono.post, '/api/target-endpoints/', 201, data, data)
        self.api_test(self.rekono.post, '/api/target-endpoints/', 400, data)    # Existing target endpoint
        # Delete target endpoint
        self.api_test(self.rekono.delete, f'/api/target-endpoints/{target_endpoint["id"]}/', 204)
        # Delete removed target endpoint
        self.api_test(self.rekono.delete, f'/api/target-endpoints/{target_endpoint["id"]}/', 404)
        self.api_test(self.rekono.delete, f'/api/target-ports/{target_port["id"]}/', 204)           # Delete target port
        # Delete removed target port
        self.api_test(self.rekono.delete, f'/api/target-ports/{target_port["id"]}/', 404)
        self.api_test(self.rekono.delete, f'/api/targets/{target["id"]}/', 204)     # Delete target
        self.api_test(self.rekono.delete, f'/api/targets/{target["id"]}/', 404)     # Delete removed target

    def test_target_types(self) -> None:
        '''Test target creation with different types.'''
        data = {'target': 'target', 'project': self.project['id']}
        for target, type in [
            ('10.10.10.10', 'Private IP'),                                      # Private IP
            ('1.1.1.1', 'Public IP'),                                           # Public IP
            ('10.10.10.0/24', 'Network'),                                       # Network
            ('10.10.10.1-20', 'IP range'),                                      # IP range
            ('scanme.nmap.org', 'Domain')                                       # Domain
        ]:
            data['target'] = target
            expected = data
            expected['type'] = type
            self.api_test(self.rekono.post, '/api/targets/', 201, data, expected)   # Create target

    def test_unauthorized_creation(self) -> None:
        '''Test target creation with user that doesn't belong to related project.'''
        username = 'unauthproject'
        password = 'rekono'
        User.objects.create_superuser(username, 'reader@reader.reader', password)   # Create admin for testing
        data = {'username': username, 'password': password}
        content = self.api_test(APIClient().post, '/api/token/', 200, data, {})     # Login request
        unauth = APIClient(HTTP_AUTHORIZATION=f'Bearer {content.get("access")}')    # Configure API client
        data = {'target': '10.10.10.10', 'project': self.project['id']}
        self.api_test(unauth.post, '/api/targets/', 403, data)                  # User is not a project member
