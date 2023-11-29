import json
from pathlib import Path
from typing import Any, Dict, List

from django.test import TestCase
from projects.models import Project
from rest_framework.test import APIClient
from security.authorization.roles import Role
from targets.enums import TargetType
from targets.models import Target
from tests.cases import RekonoTestCase
from users.models import User


class RekonoTest(TestCase):
    login = "/api/security/login/"
    profile = "/api/profile/"
    endpoint = ""
    expected_str = ""
    data_dir = Path(__file__).resolve().parent / "data"
    cases: List[RekonoTestCase] = []
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
        self.project = Project.objects.create(
            name="test", description="test", owner=self.admin1
        )
        for user in [self.admin1, self.auditor1, self.reader1]:
            self.project.members.add(user)

    def _setup_target(self) -> None:
        self._setup_project()
        self.target = Target.objects.create(
            project=self.project, target="10.10.10.10", type=TargetType.PRIVATE_IP
        )

    def tearDown(self) -> None:
        pass

    def test_cases(self) -> None:
        for test_case in self.cases:
            test_case.test_case(endpoint=self.endpoint)

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
