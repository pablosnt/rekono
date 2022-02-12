from rest_framework.test import APIClient
from testing.api.base import RekonoTestCase
from users.models import User


class TargetsTestCase(RekonoTestCase):
    '''Base test case for Targets module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        self.targets = '/api/targets/'                                          # Targets API endpoint
        self.target_ports = '/api/target-ports/'                                # Target Ports API endpoint
        self.target_endpoints = '/api/target-endpoints/'                        # Target Endpoints API endpoint
        # Data for testing
        self.targets_data = [
            ('10.10.10.1', 'Private IP'),                                       # Private IP
            ('1.1.1.1', 'Public IP'),                                           # Public IP
            ('10.10.10.0/24', 'Network'),                                       # Network
            ('10.10.10.1-20', 'IP range'),                                      # IP range
            ('scanme.nmap.org', 'Domain')                                       # Domain
        ]
        # Create project for testing
        project_data = {'name': 'Project Test', 'description': 'Project Test', 'tags': ['test']}
        self.project = self.api_test(self.rekono.post, '/api/projects/', 201, project_data, project_data)
        # Create target for testing
        self.target_data = {'target': '10.10.10.10', 'project': self.project['id']}
        self.target = self.api_test(self.rekono.post, self.targets, 201, self.target_data, self.target_data)
        # Create target port for testing
        self.tp_data = {'target': self.target['id'], 'port': 80}
        self.target_port = self.api_test(self.rekono.post, self.target_ports, 201, self.tp_data, self.tp_data)
        # Create target endpoint for testing
        self.te_data = {'target_port': self.target_port['id'], 'endpoint': '/robots.txt'}
        self.target_endpoint = self.api_test(self.rekono.post, self.target_endpoints, 201, self.te_data, self.te_data)


class TargetsTest(TargetsTestCase):
    '''Test cases for Target entity from Targets module.'''

    def test_create(self) -> None:
        '''Test target creation feature with different target types.'''
        data = {'project': self.project['id']}
        for target, type in self.targets_data:
            data['target'] = target
            expected = data
            expected['type'] = type
            self.api_test(self.rekono.post, self.targets, 201, data, expected)  # Create target

    def test_unauthorized_create(self) -> None:
        '''Test target creation feature with user that doesn't belong to related project.'''
        credential = 'unauth'
        User.objects.create_superuser(credential, 'reader@reader.reader', credential)   # Create admin for testing
        data = {'username': credential, 'password': credential}
        content = self.api_test(APIClient().post, self.login, 200, data, {})    # Login request
        unauth = APIClient(HTTP_AUTHORIZATION=f'Bearer {content.get("access")}')        # Configure API client
        self.target_data['target'] = '10.10.10.2'
        self.api_test(unauth.post, self.targets, 403, self.target_data)                # User is not a project member

    def test_invalid_create(self) -> None:
        '''Test target creation feature with invalid data.'''
        self.api_test(self.rekono.post, self.targets, 400, self.target_data)    # Target already exists
        self.target_data['target'] = 'invalid'
        self.api_test(self.rekono.post, self.targets, 400, self.target_data)    # Invalid target

    def test_delete(self) -> None:
        '''Test target deletion feature.'''
        self.api_test(self.rekono.delete, f'/api/targets/{self.target["id"]}/', 204)    # Delete target
        self.api_test(self.rekono.delete, f'/api/targets/{self.target["id"]}/', 404)    # Delete removed target


class TargetPortsTest(TargetsTestCase):
    '''Test cases for Target Port entity from Targets module.'''

    def test_create(self) -> None:
        '''Test target port creation feature.'''
        self.tp_data['port'] = 8080
        # Create new target port
        content = self.api_test(self.rekono.post, self.target_ports, 201, self.tp_data, self.tp_data)
        self.api_test(self.rekono.get, f'{self.target_ports}{content["id"]}/', 200, {}, self.tp_data)

    def test_invalid_create(self) -> None:
        '''Test target port creation feature with invalid data.'''
        print('HELLo')
        self.api_test(self.rekono.post, self.target_ports, 400, self.tp_data)   # Target port already exists
        self.tp_data['port'] = -1
        self.api_test(self.rekono.post, self.target_ports, 400, self.tp_data)   # Invalid port number

    def test_delete(self) -> None:
        '''Test target port deletion feature.'''
        self.api_test(self.rekono.delete, f'{self.target_ports}{self.target_port["id"]}/', 204)     # Delete target port
        self.api_test(self.rekono.get, f'{self.target_ports}{self.target_port["id"]}/', 404)


class TargetEndpointsTest(TargetsTestCase):
    '''Test cases for Target Endpoint entity from Targets module.'''

    def test_create(self) -> None:
        '''Test target endpoint creation.'''
        self.te_data['endpoint'] = '/admin'
        # Create new target endpoint
        content = self.api_test(self.rekono.post, self.target_endpoints, 201, self.te_data, self.te_data)
        self.api_test(self.rekono.get, f'{self.target_endpoints}{content["id"]}/', 200, {}, self.te_data)

    def test_invalid_create(self) -> None:
        '''Test target endpoint creation with invalid data.'''
        self.api_test(self.rekono.post, self.target_endpoints, 400, self.te_data)   # Target endpoint already exists
        self.te_data['endpoint'] = '/invalid;endpoint;'
        self.api_test(self.rekono.post, self.target_endpoints, 400, self.te_data)   # Invalid endpoint value

    def test_delete(self) -> None:
        '''Test target endpoint deletion feature.'''
        # Delete target endpoint
        self.api_test(self.rekono.delete, f'{self.target_endpoints}{self.target_endpoint["id"]}/', 204)
        self.api_test(self.rekono.get, f'{self.target_endpoints}{self.target_endpoint["id"]}/', 404)
