from unittest import mock

from executions.models import Execution
from processes.models import Step
from tasks.enums import Status
from tasks.models import Task
from testing.api.defect_dojo_base import RekonoTestCaseWithDDImports
from testing.mocks.defectdojo import defect_dojo_success
from tools.models import Configuration, Tool


class TasksTest(RekonoTestCaseWithDDImports):
    '''Test cases for Tasks module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        self.endpoint = '/api/tasks/'
        super().setUp()
        super().initialize_environment()                                        # Initialize testing environment
        self.harvester = Tool.objects.get(name='theHarvester')
        self.harvester_config = Configuration.objects.get(tool=self.harvester, default=True)
        self.harvester_step = Step.objects.create(
            process=self.process, tool=self.harvester, configuration=self.harvester_config, priority=1
        )
        self.running_task = Task.objects.create(target=self.target, process=self.process, status=Status.RUNNING)
        Execution.objects.create(task=self.running_task, step=self.harvester_step, status=Status.RUNNING)
        Execution.objects.create(task=self.running_task, step=self.step, status=Status.REQUESTED)
        # Data for testing
        self.tool_data = {'target_id': self.target.id, 'tool_id': self.tool.id}
        self.process_data = {'target_id': self.target.id, 'process_id': self.process.id}
        self.expected_data = {'intensity_rank': 'Normal', 'status': 'Requested'}
        self.models = {                                                         # Models to test __str__ method
            self.task: f'{self.project.name} - {self.target.target} - {self.tool.name} - {self.configuration.name}',
            self.running_task: f'{self.project.name} - {self.target.target} - {self.process.name}',
        }
        self.dd_model = self.task                                               # Model to test Defect-Dojo integration

    def test_create_with_tool(self) -> None:
        '''Test creation feature with tool task.'''
        # Create task
        content = self.api_test(self.client.post, self.endpoint, 201, data=self.tool_data, expected=self.expected_data)
        self.check_fields(['id', 'target'], content['target'], self.target)
        self.check_fields(['id', 'name'], content['tool'], self.tool)
        self.check_fields(['id', 'name'], content['configuration'], self.configuration)

    def test_create_with_process(self) -> None:
        '''Test creation feature with process task.'''
        # Create task
        content = self.api_test(self.client.post, self.endpoint, 201, data=self.process_data, expected=self.expected_data)      # noqa: E501
        self.check_fields(['id', 'target'], content['target'], self.target)
        self.check_fields(['id', 'name'], content['process'], self.process)

    def test_create_without_scheduled_time_unit(self) -> None:
        '''Test creation feature with scheduled_in option but without time unit.'''
        self.tool_data['scheduled_in'] = 5
        # Create task. Schedule configuration will be ignored
        self.api_test(self.client.post, self.endpoint, 201, data=self.tool_data, expected=self.expected_data)

    def test_invalid_create_without_process_and_tool(self) -> None:
        '''Test creation feature without process or tool.'''
        self.process_data.pop('process_id')
        # Process or Tool are required
        self.api_test(self.client.post, self.endpoint, 400, data=self.process_data)

    def test_invalid_create_with_invalid_intensity(self) -> None:
        '''Test creation feature with invalid intensity.'''
        self.tool_data['tool_id'] = self.harvester.id
        self.tool_data['intensity_rank'] = 'Insane'                             # theHarvester has no Insane intensity
        self.api_test(self.client.post, self.endpoint, 400, data=self.tool_data)

    def test_invalid_create_with_invalid_schedule_date(self) -> None:
        '''Test creation feature with past scheduled date.'''
        self.process_data['scheduled_at'] = '2000-01-01T01:00:00.000Z'
        # Scheduled configuration should be future
        self.api_test(self.client.post, self.endpoint, 400, data=self.process_data)

    def test_unauthorized_create(self) -> None:
        '''Test creation feature with unauthorized user.'''
        # User is not a project member
        self.api_test(self.other_client.post, self.endpoint, 403, data=self.tool_data)

    def test_cancel(self) -> None:
        '''Test cancellation feature.'''
        self.api_test(self.client.delete, f'{self.endpoint}{self.running_task.id}/', 204)
        self.expected_data['status'] = 'Cancelled'
        self.api_test(self.client.get, f'{self.endpoint}{self.running_task.id}/', expected=self.expected_data)

    def test_invalid_cancel(self) -> None:
        '''Test cancellation feature in completed task.'''
        # It's not possible to cancel a completed task
        self.api_test(self.client.delete, f'{self.endpoint}{self.task.id}/', 400)

    def test_repeat(self) -> None:
        '''Test repeat task feature.'''
        # Repeat completed task
        content = self.api_test(self.client.post, f'{self.endpoint}{self.task.id}/repeat/', 201, expected=self.expected_data)   # noqa: E501
        self.check_fields(['id', 'target'], content['target'], self.target)
        self.check_fields(['id', 'name'], content['tool'], self.tool)
        self.check_fields(['id', 'name'], content['configuration'], self.configuration)

    def test_invalid_repeat(self) -> None:
        '''Test repeat task feature with running task.'''
        # It's not possible to repeat a running task
        self.api_test(self.client.post, f'{self.endpoint}{self.running_task.id}/repeat/', 400)

    @mock.patch('defectdojo.api.DefectDojo.request', defect_dojo_success)       # Mocks Defect-Dojo response
    def test_import_in_defect_dojo_without_executions_and_findings(self) -> None:
        '''Test Defect-Dojo import feature with no data to import.'''
        # Try to import executions from running task
        self.api_test(
            self.client.post,
            f'{self.endpoint}{self.running_task.id}/defect-dojo-scans/',
            400, data={'id': 1}
        )
        # Try to import findings from running task
        self.api_test(
            self.client.post,
            f'{self.endpoint}{self.running_task.id}/defect-dojo-findings/',
            400, data={'id': 1}
        )
