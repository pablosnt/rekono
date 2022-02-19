import json
import os
from typing import Any, Callable, Dict, List, Tuple

from django.http import HttpResponse
from django.test import TestCase
from django.utils import timezone
from executions.models import Execution
from processes.models import Process, Step
from projects.models import Project
from rest_framework.test import APIClient
from targets.models import Target, TargetEndpoint, TargetPort
from tasks.enums import Status
from tasks.models import Task
from tools.enums import IntensityRank
from tools.models import Configuration, Tool
from users.models import User


class RekonoTestCase(TestCase):
    '''Base test case.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        self.data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data')    # Testing data path
        # Create user for test authenticated requests
        self.credential = 'rekono'                                              # Credentials for testing user
        self.email = 'rekono@rekono.rekono'                                     # Email for testing user
        self.admin, self.access, self.refresh = self.create_and_login(self.credential, self.email)
        # Create other user for unauthorized requests
        self.other_credential = 'other'                                         # Credentials for other user
        self.other_email = 'other@other.other'                                  # Email for other user
        self.other, self.other_access, self.other_refresh = self.create_and_login(self.other_credential, self.other_email)  # noqa: E501
        # Rekono API clients
        self.client = APIClient(HTTP_AUTHORIZATION=f'Bearer {self.access}')     # Authenticated and Authorized
        self.other_client = APIClient(HTTP_AUTHORIZATION=f'Bearer {self.other_access}')     # Unauthorized
        self.unauthn_client = APIClient()                                       # Unauthenticated
        # Create project for testing
        self.project = Project.objects.create(name='Test', description='Test', tags=['test'], owner=self.admin)
        self.project.members.add(self.admin)
        self.models: Dict[Any, str] = {}                                        # Models to test __str__ method

    def initialize_environment(self) -> None:
        '''Initialize environment for testing.'''
        self.target = Target.objects.create(project=self.project, target='10.10.10.10')
        self.target_port = TargetPort.objects.create(target=self.target, port=80)
        self.target_endpoint = TargetEndpoint.objects.create(target_port=self.target_port, endpoint='/robots.txt')
        self.tool = Tool.objects.get(name='Nmap')
        self.configuration = Configuration.objects.get(tool=self.tool, default=True)
        self.process = Process.objects.create(name='Test', description='Test', tags=['test'], creator=self.admin)
        self.step = Step.objects.create(process=self.process, tool=self.tool, configuration=self.configuration)
        self.task = Task.objects.create(
            target=self.target,
            tool=self.tool,
            configuration=self.configuration,
            intensity=IntensityRank.NORMAL,
            status=Status.COMPLETED,
            start=timezone.now(),
            end=timezone.now()
        )
        self.execution = Execution.objects.create(
            task=self.task,
            status=Status.COMPLETED,
            start=timezone.now(),
            end=timezone.now()
        )

    def get_content(self, response: HttpResponse) -> Dict[Any, Any]:
        '''Get content from HTTP response.

        Args:
            response (HttpResponse): HTTP response

        Returns:
            Dict[Any, Any]: Response content
        '''
        return json.loads(response.content.decode('utf-8')) if response.content else {}

    def check_fields(self, fields: List[str], content: Dict[str, Any], expected: Dict[str, Any]) -> None:
        '''Check expected values for some response fields.

        Args:
            fields (List[str]): List of field names
            content (Dict[str, Any]): Response content
            expected (Dict[str, Any]): Expected data
        '''
        for field in fields:
            if hasattr(expected, field):
                self.assertEqual(getattr(expected, field), content[field])
            else:
                self.assertEqual(expected[field], content[field])

    def api_test(self, request: Callable, endpoint: str, status_code: int = 200, **kwargs: Any) -> Dict[Any, Any]:
        '''Make Rekono API request and check response.

        Args:
            request (Callable): Method to make Rekono API request
            endpoint (str): Rekono endpoint to call
            status_code (int, optional): Expected HTTP status code. Defaults to 200.

        Returns:
            Dict[Any, Any]: Response content
        '''
        if kwargs.get('data'):                                                  # HTTP body
            # Make Rekono API request
            response = request(endpoint, data=kwargs['data'], format=kwargs.get('format', 'json'))
        else:                                                                   # No HTTP body
            response = request(endpoint)                                        # Make Rekono API request
        self.assertEqual(response.status_code, status_code)                     # Check HTTP status code
        content = self.get_content(response)                                    # Get content from HTTP response
        if kwargs.get('expected'):                                              # Expected response content
            self.check_fields(list(kwargs['expected'].keys()), content, kwargs['expected'])     # Check expected data
        return content

    def login(self, username: str, password: str) -> Tuple[str, str]:
        '''Log in Rekono.

        Args:
            username (str): Username to login
            password (str): Password to login

        Returns:
            Tuple[str, str]: Access and refresh tokens
        '''
        data = {'username': username, 'password': password}                 # Login data
        content = self.api_test(APIClient().post, '/api/token/', 200, data=data)    # Login request
        return content['access'], content['refresh']

    def create_and_login(self, credential: str, email: str) -> Tuple[User, str, str]:
        '''Create new user and log in Rekono.

        Args:
            credential (str): Value to be used as username and password
            email (str): User email

        Returns:
            Tuple[User, str, str]: User entity, access and refresh tokens
        '''
        user = User.objects.create_superuser(credential, email, credential)     # Create user
        access, refresh = self.login(credential, credential)                    # Log in Rekono
        return user, access, refresh

    def test_model_representation(self) -> None:
        '''Test __str__ method for selected models.'''
        for model, expected in self.models.items():
            self.assertEqual(expected, model.__str__())
