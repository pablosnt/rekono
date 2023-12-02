import json
from pathlib import Path
from typing import Any, Dict, List

from django.test import TestCase
from executions.enums import Status
from executions.models import Execution
from platforms.telegram_app.bot.mixins import process
from processes.models import Process, Step
from projects.models import Project
from rest_framework.test import APIClient
from security.authorization.roles import Role
from targets.enums import TargetType
from targets.models import Target
from tasks.models import Task
from tests.cases import RekonoTestCase
from tools.enums import Intensity
from tools.models import Configuration, Tool
from users.models import User


class RekonoTest(TestCase):
    data_dir = Path(__file__).resolve().parent / "data"
    cases: List[RekonoTestCase] = []

    def _create_user(self, username: str, role: Role) -> User:
        new_user = User.objects.create(
            username=username,
            first_name=username,
            last_name=username,
            email=f"{username}@rekono.com",
            is_active=True,
        )
        new_user.set_password(username)
        new_user.save(update_fields=["password"])
        User.objects.assign_role(new_user, role)
        return new_user

    def setUp(self) -> None:
        self.users: Dict[Role, List[User]] = {
            Role.ADMIN: [],
            Role.AUDITOR: [],
            Role.READER: [],
        }
        for username, role in [
            ("admin1", Role.ADMIN),
            ("admin2", Role.ADMIN),
            ("auditor1", Role.AUDITOR),
            ("auditor2", Role.AUDITOR),
            ("reader1", Role.READER),
            ("reader2", Role.READER),
        ]:
            setattr(self, username, self._create_user(username, role))
            self.users[role].append(getattr(self, username))

    def _setup_project(self) -> None:
        self.project, _ = Project.objects.get_or_create(
            name="test", description="test", owner=self.admin1
        )
        for user in [self.admin1, self.auditor1, self.reader1]:
            self.project.members.add(user)

    def _setup_target(self) -> None:
        self._setup_project()
        self.target, _ = Target.objects.get_or_create(
            project=self.project, target="10.10.10.10", type=TargetType.PRIVATE_IP
        )

    def _setup_tasks_and_executions(self) -> None:
        if not hasattr(self, "target"):
            self._setup_target()
        self.running_task = Task.objects.create(
            target=self.target,
            process=Process.objects.get(pk=1),
            executor=self.admin1,
        )
        process_step = Step.objects.filter(process__id=1).first()
        self.execution1 = Execution.objects.create(
            task=self.running_task,
            configuration=process_step.configuration,
            status=Status.COMPLETED,
        )
        self.execution2 = Execution.objects.create(
            task=self.running_task,
            configuration=process_step.configuration,
            status=Status.RUNNING,
        )
        configuration = Configuration.objects.get(pk=1)
        self.completed_task = Task.objects.create(
            target=self.target,
            configuration=configuration,
            executor=self.auditor1,
        )
        self.execution3 = Execution.objects.create(
            task=self.completed_task,
            configuration=configuration,
            status=Status.COMPLETED,
        )

    def _metadata(self) -> Dict[str, Any]:
        return {}

    def test_cases(self) -> None:
        for test_case in self.cases:
            test_case.test_case(**self._metadata())


class ApiTest(RekonoTest):
    endpoint = ""
    login = "/api/security/login/"
    profile = "/api/profile/"
    expected_str = ""

    anonymous_allowed = False

    def _get_object(self) -> Any:
        return None

    def _get_api_client(self, access: str = None, token: str = None):
        client = (
            APIClient(HTTP_AUTHORIZATION=f"Bearer {access}") if access else APIClient()
        )
        return APIClient(HTTP_AUTHORIZATION=f"Token {token}") if token else client

    def _get_content(self, raw: Any) -> Dict[str, Any]:
        return json.loads((raw or "{}".encode()).decode())

    def _metadata(self) -> Dict[str, Any]:
        return {"endpoint": self.endpoint}

    def test_str(self) -> None:
        object = self._get_object()
        if object and self.expected_str:
            self.assertEqual(self.expected_str, object.__str__())

    def test_anonymous_access(self) -> None:
        if self.anonymous_allowed is not None and self.endpoint:
            response = APIClient().get(self.endpoint)
            self.assertEqual(
                200 if self.anonymous_allowed else 401, response.status_code
            )


class ToolTest(RekonoTest):
    tool_name = ""
    execution = None
    executor_arguments = []
    data_dir = RekonoTest.data_dir / "reports"

    def setUp(self) -> None:
        if self.tool_name:
            super().setUp()
            self._setup_target()
            self.tool = Tool.objects.get(name=self.tool_name)
            self.configuration = self.tool.configurations.get(default=True)
            self.task = Task.objects.create(
                target=self.target,
                configuration=self.configuration,
                intensity=Intensity.NORMAL,
            )
            self.execution = Execution.objects.create(
                task=self.task, configuration=self.configuration
            )

    def _metadata(self) -> Dict[str, Any]:
        return {
            "execution": self.execution,
            "executor_arguments": self.executor_arguments,
            "reports": self.data_dir,
            "tool": self.tool_name,
        }
