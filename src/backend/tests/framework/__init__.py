from functools import cached_property
from typing import Any

from django.test import TestCase
from rest_framework.test import APIClient

from executions.models import Execution
from tasks.models import Task
from tasks.queues import TasksQueue
from tests.framework.cases import RekonoTestCase
from tests.framework.data import TestingDataMixin
from tools.enums import Intensity
from tools.models import Tool


class BaseTest(TestCase, TestingDataMixin):
    cases: list[RekonoTestCase] = []

    def setUp(self):
        super().setUp()
        self.setup_testing_data()

    @cached_property
    def kwargs(self) -> dict[str, Any]:
        return {}

    def test_cases(self) -> None:
        for test_case_index, test_case in enumerate(self.cases):
            test_case.test_case(test_case_number=test_case_index + 1, test_case=self, **self.kwargs)


class ApiTest(BaseTest):
    endpoint = ""
    expected_string = ""
    anonymous_access_allowed = False
    setup_entities = ["users"]

    @cached_property
    def object(self) -> Any:
        return None

    @cached_property
    def kwargs(self) -> dict[str, Any]:
        return {"base_endpoint": self.endpoint}

    def test_string(self) -> None:
        if self.object and self.expected_string:
            self.assertEqual(self.expected_string, self.object.__str__())

    def test_anonymous_access(self) -> None:
        if self.anonymous_access_allowed is not None and self.endpoint:
            self.assertEqual(200 if self.anonymous_access_allowed else 401, APIClient().get(self.endpoint).status_code)


class ParserTest(BaseTest):
    tool_name = ""
    setup_entities = ["target_and_task_parameters"]
    arguments = []

    def setUp(self):
        super().setUp()
        if self.tool_name:
            self.tool = Tool.objects.get(name=self.tool_name)
            self.configuration = self.tool.configurations.get(default=True)
            self.task = Task.objects.create(
                target=self.target, configuration=self.configuration, intensity=Intensity.NORMAL
            )
            self.task.wordlists.set([self.wordlist])
            self.task.input_technologies.set([self.input_technology])
            self.task.input_vulnerabilities.set([self.input_vulnerability])
            self.execution = Execution.objects.create(task=self.task, configuration=self.configuration)


class QueueTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.queue = TasksQueue()
