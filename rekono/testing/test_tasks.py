from executions.models import Execution
from processes.models import Process, Step
from projects.models import Project
from rest_framework.test import APIClient
from targets.models import Target
from tasks.enums import Status
from tasks.models import Task
from testing.test_base import RekonoTestCase
from tools.models import Configuration, Tool
from users.models import User


class TasksTest(RekonoTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.endpoint = '/api/tasks/'
        self.project = Project.objects.create(
            name='Project Test', description='Project Test', tags=['test'], owner=self.admin
        )
        self.project.members.add(self.admin)
        self.target = Target.objects.create(project=self.project, target='scanme.nmap.org')
        self.nmap = Tool.objects.get(name='Nmap')
        self.nmap_config = Configuration.objects.get(tool=self.nmap, default=True)
        self.the_harvester = Tool.objects.get(name='theHarvester')
        self.the_harvester_config = Configuration.objects.get(tool=self.the_harvester, default=True)
        self.process = Process.objects.create(
            name='Process Test', description='Process Test', tags=['test'], creator=self.admin
        )
        self.nmap_step = Step.objects.create(
            process=self.process, tool=self.nmap, configuration=self.nmap_config, priority=1
        )
        self.the_harvester_step = Step.objects.create(
            process=self.process, tool=self.the_harvester, configuration=self.the_harvester_config, priority=1
        )
        self.completed_task = Task.objects.create(
            target=self.target, tool=self.nmap, configuration=self.nmap_config, status=Status.COMPLETED
        )
        self.running_task_with_executions = Task.objects.create(
            target=self.target, process=self.process, status=Status.RUNNING
        )
        Execution.objects.create(
            task=self.running_task_with_executions, step=self.the_harvester_step, status=Status.RUNNING
        )
        Execution.objects.create(task=self.running_task_with_executions, step=self.nmap_step, status=Status.REQUESTED)
        self.tool_data = {'target_id': self.target.id, 'tool_id': self.nmap.id}
        self.process_data = {'target_id': self.target.id, 'process_id': self.process.id}
        self.expected_data = {'intensity_rank': 'Normal', 'status': 'Requested'}

    def test_tool_execution(self) -> None:
        content = self.api_test(self.rekono.post, self.endpoint, 201, self.tool_data, self.expected_data)
        self.assertEqual(self.target.target, content['target']['target'])
        self.assertEqual(self.nmap.name, content['tool']['name'])
        self.assertEqual(self.nmap_config.name, content['configuration']['name'])

    def test_process_execution(self) -> None:
        content = self.api_test(self.rekono.post, self.endpoint, 201, self.process_data, self.expected_data)
        self.assertEqual(self.target.target, content['target']['target'])
        self.assertEqual(self.process.name, content['process']['name'])

    def test_create_without_scheduled_time_unit(self) -> None:
        self.tool_data['scheduled_in'] = 5
        self.expected_data['scheduled_in'] = None
        self.api_test(self.rekono.post, self.endpoint, 201, self.tool_data, self.expected_data)

    def test_invalid_create_without_process_and_tool(self) -> None:
        self.process_data.pop('process_id')
        self.api_test(self.rekono.post, self.endpoint, 400, self.process_data)
    
    def test_invalid_create_with_invalid_intensity(self) -> None:
        self.tool_data['tool_id'] = self.the_harvester.id
        self.tool_data['intensity_rank'] = 'Insane'
        self.api_test(self.rekono.post, self.endpoint, 400, self.tool_data)
    
    def test_invalid_create_with_invalid_schedule_date(self) -> None:
        self.process_data['scheduled_at'] = '2000-01-01T01:00:00.000Z'
        self.api_test(self.rekono.post, self.endpoint, 400, self.process_data)

    def test_unauthorized_create(self) -> None:
        credential = 'other'
        User.objects.create_superuser(credential, 'other@other.other', credential)  # Create other user
        data = {'username': credential, 'password': credential}                 # Login data
        content = self.api_test(APIClient().post, self.login, 200, data, {})    # Login request
        unauth = APIClient(HTTP_AUTHORIZATION=f'Bearer {content.get("access")}')   # Configure API client
        self.api_test(unauth.post, self.endpoint, 403, self.tool_data)

    def test_cancel(self) -> None:
        self.api_test(self.rekono.delete, f'{self.endpoint}{self.running_task_with_executions.id}/', 204)
        self.expected_data['status'] = 'Cancelled'
        self.api_test(
            self.rekono.get, f'{self.endpoint}{self.running_task_with_executions.id}/', 200, {}, self.expected_data
        )

    def test_invalid_cancel(self) -> None:
        self.api_test(self.rekono.delete, f'{self.endpoint}{self.completed_task.id}/', 400)

    def test_repeat(self) -> None:
        content = self.api_test(
            self.rekono.post, f'{self.endpoint}{self.completed_task.id}/repeat/',
            201, {}, self.expected_data
        )
        self.assertEqual(self.completed_task.target.target, content['target']['target'])
        self.assertEqual(self.completed_task.tool.name, content['tool']['name'])
        self.assertEqual(self.completed_task.configuration.name, content['configuration']['name'])

    def test_invalid_repeat(self) -> None:
        content = self.api_test(self.rekono.post, self.endpoint, 201, self.process_data, self.expected_data)
        self.api_test(self.rekono.post, f'{self.endpoint}{content["id"]}/repeat/', 400)
