from django.utils import timezone
from executions.models import Execution
from tasks.enums import Status
from testing.api.base import RekonoApiTestCase


class ExecutionsTest(RekonoApiTestCase):
    '''Test cases for Executions module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        self.endpoint = '/api/executions/'                                      # Executions API endpoint
        super().setUp()
        super().initialize_environment()                                        # Initialize testing environment
        self.step_execution = Execution.objects.create(                         # Create execution related to step
            task=self.task,
            tool=self.step.tool,
            configuration=self.step.configuration,
            status=Status.COMPLETED,
            start=timezone.now(),
            end=timezone.now()
        )
        self.models = {                                                         # Models to test __str__ method
            self.execution: (
                f'{self.project.name} - {self.target.target} - {self.task.tool.name} - {self.task.configuration.name}'
            ),
            self.step_execution: (
                f'{self.project.name} - {self.target.target} - {self.step.tool.name} - {self.step.configuration.name}'
            )
        }

    def test_get_all(self) -> None:
        '''Test get all feature.'''
        content = self.api_test(self.client.get, self.endpoint, expected={'count': 2})  # Get all executions
        self.check_fields(['id'], content['results'][0], self.step_execution)
        self.check_fields(['id'], content['results'][1], self.execution)

    def test_tool_filter(self) -> None:
        '''Test filter by tool feature.'''
        # Get executions related to testing tool
        content = self.api_test(self.client.get, f'{self.endpoint}?tool={self.nmap.id}', 200, expected={'count': 2})
        self.check_fields(['id'], content['results'][0], self.step_execution)
        self.check_fields(['id'], content['results'][1], self.execution)

    def test_unauthorized_get_all(self) -> None:
        '''Test get all feature with an unauthorized user.'''
        self.api_test(self.other_client.get, self.endpoint, expected={'count': 0})      # Get all executions
