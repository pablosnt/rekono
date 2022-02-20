from unittest import mock

from django.utils import timezone
from executions.models import Execution
from tasks.enums import Status
from testing.api.defect_dojo_base import RekonoTestCaseWithDDImports
from testing.mocks.defectdojo import defect_dojo_success


class ExecutionsTest(RekonoTestCaseWithDDImports):
    '''Test cases for Executions module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        self.endpoint = '/api/executions/'                                      # Executions API endpoint
        super().setUp()
        super().initialize_environment()                                        # Initialize testing environment
        self.step_execution = Execution.objects.create(                         # Create execution related to step
            task=self.task,
            step=self.step,
            status=Status.COMPLETED,
            start=timezone.now(),
            end=timezone.now()
        )
        self.models = {                                                         # Models to test __str__ method
            self.execution: self.task.__str__(),
            self.step_execution: f'{self.task.__str__()} - {self.step.tool.name} - {self.step.configuration.name}'
        }
        self.dd_model = self.execution                                          # Model to test Defect-Dojo integration

    def test_get_all(self) -> None:
        '''Test get all feature.'''
        content = self.api_test(self.client.get, self.endpoint, expected={'count': 2})  # Get all executions
        self.check_fields(['id'], content['results'][0], self.step_execution)
        self.check_fields(['id'], content['results'][1], self.execution)

    def test_unauthorized_get_all(self) -> None:
        '''Test get all feature with an unauthorized user.'''
        self.api_test(self.other_client.get, self.endpoint, expected={'count': 0})      # Get all executions

    @mock.patch('defectdojo.api.DefectDojo.request', defect_dojo_success)       # Mocks Defect-Dojo response
    def test_import_in_defect_dojo_without_executions_and_findings(self) -> None:
        '''Test Defect-Dojo import feature with no data to import.'''
        running_execution = Execution.objects.create(task=self.task, status=Status.RUNNING)
        self.api_test(                                                          # Try to import running execution
            self.client.post,
            f'{self.endpoint}{running_execution.id}/defect-dojo-scans/',
            400, data={'id': 1}
        )
        # Try to import findings from running execution
        self.api_test(
            self.client.post,
            f'{self.endpoint}{self.step_execution.id}/defect-dojo-findings/',
            400, data={'id': 1}
        )
