from datetime import datetime, timedelta

from executions.models import Execution
from processes.models import Step
from tasks.enums import Status, TimeUnit
from tasks.models import Task
from testing.api.base import RekonoApiTestCase
from tools.models import Configuration, Tool


class TasksTest(RekonoApiTestCase):
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
        Execution.objects.create(
            task=self.running_task,
            tool=self.harvester,
            configuration=self.harvester_config,
            status=Status.RUNNING
        )
        Execution.objects.create(
            task=self.running_task,
            tool=self.step.tool,
            configuration=self.step.configuration,
            status=Status.REQUESTED
        )
        # Data for testing
        self.tool_data = {'target_id': self.target.id, 'tool_id': self.nmap.id}
        self.process_data = {'target_id': self.target.id, 'process_id': self.process.id}
        self.expected_data = {'intensity_rank': 'Normal', 'status': Status.REQUESTED}
        self.models = {                                                         # Models to test __str__ method
            self.task: (
                f'{self.project.name} - {self.target.target} - {self.nmap.name} - {self.nmap_configuration.name}'
            ),
            self.running_task: f'{self.project.name} - {self.target.target} - {self.process.name}',
        }

    def run_task_and_check_status(self, task_id: int, expected_status: str = Status.COMPLETED) -> None:
        '''Run task (launch RQ worker for testing) and check that the task has been completed.'''
        self.launch_rq_worker()
        self.expected_data['status'] = expected_status
        self.api_test(self.client.get, f'{self.endpoint}{task_id}/', 200, expected=self.expected_data)

    def test_create_with_tool(self) -> None:
        '''Test creation feature with tool task.'''
        # Create task
        content = self.api_test(self.client.post, self.endpoint, 201, data=self.tool_data, expected=self.expected_data)
        self.check_fields(['id', 'target'], content['target'], self.target)
        self.check_fields(['id', 'name'], content['tool'], self.nmap)
        self.check_fields(['id', 'name'], content['configuration'], self.nmap_configuration)
        self.run_task_and_check_status(content['id'])

    def test_create_with_process(self) -> None:
        '''Test creation feature with process task.'''
        # Create task
        content = self.api_test(
            self.client.post, self.endpoint, 201, data=self.process_data, expected=self.expected_data
        )
        self.check_fields(['id', 'target'], content['target'], self.target)
        self.check_fields(['id', 'name'], content['process'], self.process)
        self.run_task_and_check_status(content['id'])

    def test_create_with_scheduled_at(self) -> None:
        '''Test creation feature with scheduled date.'''
        self.tool_data['scheduled_at'] = (datetime.now() + timedelta(minutes=1)).isoformat()
        # Create scheduled task
        content = self.api_test(self.client.post, self.endpoint, 201, data=self.tool_data, expected=self.expected_data)
        self.run_task_and_check_status(content['id'], Status.REQUESTED)

    def test_create_with_scheduled_in(self) -> None:
        '''Test creation feature with scheduled delay.'''
        self.tool_data['scheduled_in'] = 1
        self.tool_data['scheduled_time_unit'] = TimeUnit.MINUTES
        # Create scheduled task
        content = self.api_test(self.client.post, self.endpoint, 201, data=self.tool_data, expected=self.expected_data)
        self.run_task_and_check_status(content['id'], Status.REQUESTED)

    def test_create_with_repeat_in_and_cancellation(self) -> None:
        '''Test creation feature with repeat configuration.'''
        self.tool_data['repeat_in'] = 2
        self.tool_data['repeat_time_unit'] = TimeUnit.MINUTES
        # Create task with repeat configuration
        content = self.api_test(self.client.post, self.endpoint, 201, data=self.tool_data, expected=self.expected_data)
        self.run_task_and_check_status(content['id'])
        self.api_test(self.client.delete, f'{self.endpoint}{content["id"]}/', 204)      # Cancel loop task

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
        content = self.api_test(
            self.client.post, f'{self.endpoint}{self.task.id}/repeat/', 201, expected=self.expected_data
        )
        self.check_fields(['id', 'target'], content['target'], self.target)
        self.check_fields(['id', 'name'], content['tool'], self.nmap)
        self.check_fields(['id', 'name'], content['configuration'], self.nmap_configuration)

    def test_invalid_repeat(self) -> None:
        '''Test repeat task feature with running task.'''
        # It's not possible to repeat a running task
        self.api_test(self.client.post, f'{self.endpoint}{self.running_task.id}/repeat/', 400)
