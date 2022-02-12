from django.utils import timezone
from executions.models import Execution
from projects.models import Project
from rest_framework.test import APIClient
from targets.models import Target
from tasks.enums import Status
from tasks.models import Task
from testing.base import RekonoTestCase
from tools.enums import IntensityRank
from tools.models import Configuration, Tool
from users.models import User


class ExecutionsTest(RekonoTestCase):
    '''Test cases for Executions module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        self.endpoint = '/api/executions/'                                      # Executions API endpoint
        # Create environment for testing
        self.project = Project.objects.create(
            name='Project Test', description='Project Test', tags=['test'], owner=self.admin
        )
        self.project.members.add(self.admin)
        self.target = Target.objects.create(project=self.project, target='10.10.10.10')
        self.tool = Tool.objects.get(name='Nmap')
        self.configuration = Configuration.objects.get(tool=self.tool, default=True)
        self.task = Task.objects.create(
            target=self.target,
            tool=self.tool,
            configuration=self.configuration,
            intensity=IntensityRank.NORMAL,
            status=Status.COMPLETED,
            start=timezone.now(),
            end=timezone.now()
        )
        # Create execution for testing
        self.execution = Execution.objects.create(
            task=self.task,
            status=Status.COMPLETED,
            start=timezone.now(),
            end=timezone.now()
        )

    def test_get_all(self) -> None:
        '''Test get all feature.'''
        content = self.api_test(self.rekono.get, self.endpoint, 200, {}, {'count': 1})  # Get all executions
        self.assertEqual(content['results'][0]['id'], self.execution.id)        # Check execution data

    def test_unauthorized_get_all(self) -> None:
        '''Test get all feature with an unauthorized user.'''
        credential = 'other'
        User.objects.create_superuser(credential, 'other@other.other', credential)  # Create other user
        data = {'username': credential, 'password': credential}                 # Login data
        content = self.api_test(APIClient().post, self.login, 200, data, {})    # Login request
        unauth = APIClient(HTTP_AUTHORIZATION=f'Bearer {content.get("access")}')   # Configure API client
        self.api_test(unauth.get, self.endpoint, 200, {}, {'count': 0})         # No executions for this user
