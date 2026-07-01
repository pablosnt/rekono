import json
from functools import cached_property
from typing import cast
from unittest import mock

from django.test import TestCase
from rest_framework.test import APIClient

from executions.models import Execution
from platforms.email.notifications import SMTP
from platforms.telegram_app.models import TelegramChat
from rekono.settings import JWT_ACCESS_COOKIE, JWT_REFRESH_COOKIE
from security.authorization.roles import Role
from tests.framework import ApiTest, ApiTestNoData
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase, PutApiTestCase
from tests.framework.data import SetupProject
from users.enums import Notification
from users.models import User

# pytype: disable=wrong-arg-types

invitation1 = {"email": "test1@rekono.com", "role": Role.READER.value}
invitation2 = {"email": "test2@rekono.com", "role": Role.AUDITOR.value}
invalid_invitation = {"email": "invalid email", "role": Role.ADMIN.value}

new_profile = {
    "first_name": "test",
    "last_name": "test",
    "notification_scope": Notification.MY_EXECUTIONS.value,
    "email_notifications": True,
    "telegram_notifications": False,
}
new_valid_password = "NeW.Pa$$W0rd"
invalid_password1 = "abcd"
invalid_password2 = "ANEWPASSWORD"
invalid_password3 = "anewpassword"
invalid_password4 = "aNEWpassword"
invalid_password5 = "aNEWpassword5"

user1 = {"username": "test1", "first_name": "test", "last_name": "test", "password": new_valid_password}
invalid_user1 = {**user1, "password": invalid_password1}
invalid_user2 = {**user1, "password": invalid_password2}
invalid_user3 = {**user1, "password": invalid_password3}
invalid_user4 = {**user1, "password": invalid_password4}
invalid_user5 = {**user1, "password": invalid_password5}
invalid_user6 = {**user1, "username": "test;1", "first_name": "test;1"}


class UserTest(ApiTest, TestCase):
    endpoint = "/api/users/"
    expected_string = "admin1@rekono.com"
    data = [SetupProject(targets_and_tasks=0)]
    cases = [
        ApiTestCase(
            [Role.AUDITOR, Role.READER],
            expected=[
                {"id": 6, "username": "reader2", "email": None, "role": Role.READER.value, "is_active": True},
                {"id": 5, "username": "reader1", "email": None, "role": Role.READER.value, "is_active": True},
                {"id": 4, "username": "auditor2", "email": None, "role": Role.AUDITOR.value, "is_active": True},
                {"id": 3, "username": "auditor1", "email": None, "role": Role.AUDITOR.value, "is_active": True},
                {"id": 2, "username": "admin2", "email": None, "role": Role.ADMIN.value, "is_active": True},
                {"id": 1, "username": "admin1", "email": None, "role": Role.ADMIN.value, "is_active": True},
            ],
        ),
        ApiTestCase(
            [Role.ADMIN],
            expected=[
                {
                    "id": 6,
                    "username": "reader2",
                    "email": "reader2@rekono.com",
                    "role": Role.READER.value,
                    "is_active": True,
                },
                {
                    "id": 5,
                    "username": "reader1",
                    "email": "reader1@rekono.com",
                    "role": Role.READER.value,
                    "is_active": True,
                },
                {
                    "id": 4,
                    "username": "auditor2",
                    "email": "auditor2@rekono.com",
                    "role": Role.AUDITOR.value,
                    "is_active": True,
                },
                {
                    "id": 3,
                    "username": "auditor1",
                    "email": "auditor1@rekono.com",
                    "role": Role.AUDITOR.value,
                    "is_active": True,
                },
                {
                    "id": 2,
                    "username": "admin2",
                    "email": "admin2@rekono.com",
                    "role": Role.ADMIN.value,
                    "is_active": True,
                },
                {
                    "id": 1,
                    "username": "admin1",
                    "email": "admin1@rekono.com",
                    "role": Role.ADMIN.value,
                    "is_active": True,
                },
            ],
        ),
        ApiTestCase(
            ["admin1"],
            expected=[
                {
                    "id": 5,
                    "username": "reader1",
                    "email": "reader1@rekono.com",
                    "role": Role.READER.value,
                    "is_active": True,
                },
                {
                    "id": 3,
                    "username": "auditor1",
                    "email": "auditor1@rekono.com",
                    "role": Role.AUDITOR.value,
                    "is_active": True,
                },
                {
                    "id": 1,
                    "username": "admin1",
                    "email": "admin1@rekono.com",
                    "role": Role.ADMIN.value,
                    "is_active": True,
                },
            ],
            endpoint="{endpoint}?project=1",
        ),
        ApiTestCase(
            ["admin1"],
            expected=[
                {
                    "id": 6,
                    "username": "reader2",
                    "email": "reader2@rekono.com",
                    "role": Role.READER.value,
                    "is_active": True,
                },
                {
                    "id": 4,
                    "username": "auditor2",
                    "email": "auditor2@rekono.com",
                    "role": Role.AUDITOR.value,
                    "is_active": True,
                },
                {
                    "id": 2,
                    "username": "admin2",
                    "email": "admin2@rekono.com",
                    "role": Role.ADMIN.value,
                    "is_active": True,
                },
            ],
            endpoint="{endpoint}?no_project=1",
        ),
        ApiTestCase(["admin2"], endpoint="{endpoint}?project=1"),
        ApiTestCase(["admin2"], endpoint="{endpoint}?no_project=1"),
        PostApiTestCase([Role.AUDITOR, Role.READER], 403, invitation1),
        PostApiTestCase([Role.ADMIN], 400, invalid_invitation),
        PostApiTestCase(["admin1"], data=invitation1, expected={"id": 7, **invitation1, "is_active": None}),
        PostApiTestCase([Role.ADMIN], 400, invitation1),
        PostApiTestCase(["admin2"], data=invitation2, expected={"id": 8, **invitation2, "is_active": None}),
        PutApiTestCase(["admin1"], 403, {"role": Role.AUDITOR.value}, endpoint="1"),
        PutApiTestCase(
            [Role.ADMIN],
            data={"role": Role.ADMIN.value},
            expected={
                "id": 6,
                "username": "reader2",
                "email": "reader2@rekono.com",
                "role": Role.ADMIN.value,
                "is_active": True,
            },
            endpoint="6",
        ),
        ApiTestCase(
            [Role.ADMIN],
            expected=[
                {"id": 8, "username": None, "email": "test2@rekono.com", "role": Role.AUDITOR.value, "is_active": None},
                {"id": 7, "username": None, "email": "test1@rekono.com", "role": Role.READER.value, "is_active": None},
                {"id": 6, "username": "reader2", "role": Role.ADMIN.value, "is_active": True},
                {"id": 5, "username": "reader1", "role": Role.READER.value, "is_active": True},
                {"id": 4, "username": "auditor2", "role": Role.AUDITOR.value, "is_active": True},
                {"id": 3, "username": "auditor1", "role": Role.AUDITOR.value, "is_active": True},
                {"id": 2, "username": "admin2", "role": Role.ADMIN.value, "is_active": True},
                {"id": 1, "username": "admin1", "role": Role.ADMIN.value, "is_active": True},
            ],
        ),
        ApiTestCase(
            ["reader2"],
            expected=[
                {"id": 8, "username": None, "role": Role.AUDITOR.value, "is_active": None},
                {"id": 7, "username": None, "role": Role.READER.value, "is_active": None},
                {"id": 6, "username": "reader2", "role": Role.ADMIN.value, "is_active": True},
                {"id": 5, "username": "reader1", "role": Role.READER.value, "is_active": True},
                {"id": 4, "username": "auditor2", "role": Role.AUDITOR.value, "is_active": True},
                {"id": 3, "username": "auditor1", "role": Role.AUDITOR.value, "is_active": True},
                {"id": 2, "username": "admin2", "role": Role.ADMIN.value, "is_active": True},
                {"id": 1, "username": "admin1", "role": Role.ADMIN.value, "is_active": True},
            ],
        ),
        DeleteApiTestCase(["admin2"], 403, endpoint="2"),
        DeleteApiTestCase(["admin1", "reader2"], endpoint="2"),
        PostApiTestCase(None, 401, {"username": "admin2", "password": "admin2"}, endpoint="/api/security/login/"),
        ApiTestCase(
            [Role.AUDITOR, "reader1"],
            expected={"id": 2, "username": "admin2", "email": None, "role": Role.ADMIN.value, "is_active": False},
            endpoint="2",
        ),
        ApiTestCase(
            ["admin1", "reader2"],
            expected={"id": 2, "username": "admin2", "role": Role.ADMIN.value, "is_active": False},
            endpoint="2",
        ),
        PostApiTestCase(
            ["reader2"],
            200,
            expected={"id": 2, "username": "admin2", "role": Role.ADMIN.value, "is_active": True},
            endpoint="2/enable",
        ),
        ApiTestCase(
            [Role.ADMIN, "reader2"],
            expected={"id": 2, "username": "admin2", "role": Role.ADMIN.value, "is_active": True},
            endpoint="2",
        ),
        PutApiTestCase(
            [Role.ADMIN],
            data={"role": Role.READER.value},
            expected={
                "id": 6,
                "username": "reader2",
                "email": "reader2@rekono.com",
                "role": Role.READER.value,
                "is_active": True,
            },
            endpoint="6",
        ),
        ApiTestCase(
            [Role.ADMIN],
            expected={
                "id": 6,
                "username": "reader2",
                "email": "reader2@rekono.com",
                "role": Role.READER.value,
                "is_active": True,
            },
            endpoint="6",
        ),
        ApiTestCase(
            [Role.AUDITOR, Role.READER],
            expected={"id": 6, "username": "reader2", "email": None, "role": Role.READER.value, "is_active": True},
            endpoint="6",
        ),
        DeleteApiTestCase(["admin1"], endpoint="7"),
        DeleteApiTestCase(["admin2"], 404, endpoint="7"),
        ApiTestCase([Role.ADMIN], 404, endpoint="7"),
        DeleteApiTestCase(["admin2"], endpoint="8"),
        ApiTestCase([Role.ADMIN], 404, endpoint="8"),
    ]

    @mock.patch("platforms.email.notifications.SMTP.is_available", lambda self: True)
    def test_cases(self) -> None:
        super().test_cases()

    def test_invite_and_create_without_smtp(self) -> None:
        client = APIClient()
        client.force_authenticate(self.admin1)
        self.assertEqual(400, client.post(self.endpoint, data=invitation1).status_code)

    @mock.patch("platforms.email.notifications.SMTP.is_available", lambda self: True)
    def test_invite_and_create(self) -> None:
        client = APIClient()
        client.force_authenticate(self.admin1)
        self.assertEqual(201, client.post(self.endpoint, data=invitation1).status_code)
        self.assertEqual(204, client.post(f"{self.endpoint}7/resend/").status_code)

        new_user = User.objects.get(email=invitation1["email"])
        otp = User.objects.setup_otp(new_user)
        self.assertEqual(403, client.post(f"{self.endpoint}signup/", data={"otp": otp, **user1}).status_code)

        client = APIClient()
        self.assertEqual(401, client.post(f"{self.endpoint}signup/", data={"otp": "invalid otp", **user1}).status_code)

        for invalid_user in [invalid_user1, invalid_user2, invalid_user3, invalid_user4, invalid_user5, invalid_user6]:
            self.assertEqual(400, client.post(f"{self.endpoint}signup/", data={"otp": otp, **invalid_user}).status_code)

        new_user.is_active = True
        new_user.save(update_fields=["is_active"])
        self.assertEqual(401, client.post(f"{self.endpoint}signup/", data={"otp": otp, **user1}).status_code)

        new_user.is_active = None
        new_user.save(update_fields=["is_active"])
        response = client.post(f"{self.endpoint}signup/", data={"otp": otp, **user1})
        self.assertEqual(201, response.status_code)
        content = json.loads((response.content or "{}".encode()).decode())
        self.assertEqual(7, content["id"])
        self.assertTrue(content["is_active"])

        self.assertEqual(
            401,
            client.post(
                f"{self.endpoint}signup/", data={"otp": otp, **user1, "username": "unique new test"}
            ).status_code,
        )

        response = client.post(
            "/api/security/login/", data={"username": user1["username"], "password": new_valid_password}
        )
        self.assertEqual(200, response.status_code)

        client.force_authenticate(self.admin1)
        self.assertEqual(400, client.post(f"{self.endpoint}7/resend/").status_code)

        client.force_authenticate(new_user)
        self.assertEqual(200, client.get("/api/profile/").status_code)

    def test_create_superuser(self) -> None:
        superuser = User.objects.create_superuser("superuser", "superuser@rekono.com", "superuser")
        self.assertTrue(superuser.is_active)
        self.assertEqual(Role.ADMIN.value, superuser.groups.first().name)

    @cached_property
    def object(self) -> User:
        return self.admin1


class ProfileTest(ApiTest, TestCase):
    endpoint = "/api/profile/"
    cases = [
        ApiTestCase(["admin1"], expected={"id": 1, "username": "admin1", "role": Role.ADMIN.value}),
        ApiTestCase(["auditor1"], expected={"id": 3, "username": "auditor1", "role": Role.AUDITOR.value}),
        ApiTestCase(["reader1"], expected={"id": 5, "username": "reader1", "role": Role.READER.value}),
        PutApiTestCase(
            ["admin2"],
            data={**new_profile, "email": "admin2@rekono.com"},
            expected={
                "id": 2,
                "username": "admin2",
                "email": "admin2@rekono.com",
                "role": Role.ADMIN.value,
                **new_profile,
            },
        ),
        PutApiTestCase(
            ["admin1"],
            401,
            data={"password": new_valid_password, "old_password": "invalid password"},
            endpoint="update-password/",
        ),
        PutApiTestCase(
            ["admin1"], 400, {"password": invalid_password1, "old_password": "admin1"}, endpoint="update-password/"
        ),
        PutApiTestCase(
            ["admin1"], data={"password": new_valid_password, "old_password": "admin1"}, endpoint="update-password/"
        ),
        PostApiTestCase(None, 401, {"username": "admin1", "password": "admin1"}, endpoint="/api/security/login/"),
        PostApiTestCase(
            None, 200, {"username": "admin1", "password": new_valid_password}, endpoint="/api/security/login/"
        ),
    ]

    def setUp(self) -> None:
        super().setUp()
        self.admin1_telegram_chat = TelegramChat.objects.create(user=cast(User, self.admin1), chat_id=1)

    def test_cases(self) -> None:
        self.assertEqual(self.admin1_telegram_chat.chat_id, cast(User, self.admin1).telegram_chat.chat_id)
        super().test_cases()
        # Linked Telegram Chats are removed after a password change
        self.assertFalse(hasattr(User.objects.get(pk=cast(User, self.admin1).id), "telegram_chat"))

    @mock.patch("platforms.email.notifications.SMTP.is_available", lambda self: True)
    def test_email_change(self) -> None:
        new_email = "new-admin1@rekono.com"
        client = APIClient()
        client.force_authenticate(self.admin1)

        # Request email address change
        response = client.put(self.endpoint, data={**new_profile, "email": new_email})
        self.assertEqual(200, response.status_code)
        self.admin1.refresh_from_db()
        self.assertEqual("admin1@rekono.com", self.admin1.email)
        self.assertEqual(new_email, self.admin1.pending_email)

        # Verify the new address
        verify_endpoint = "/api/users/verify-email/"
        otp = User.objects.setup_otp(self.admin1)
        self.assertEqual(200, client.post(verify_endpoint, data={"otp": otp}).status_code)
        self.admin1.refresh_from_db()
        self.assertEqual(new_email, self.admin1.email)
        self.assertIsNone(self.admin1.pending_email)
        self.assertIsNone(self.admin1.otp)

        anonymous = APIClient()
        # Invalid OTP
        self.assertEqual(401, anonymous.post(verify_endpoint, data={"otp": "invalid otp"}).status_code)
        # No pending email
        otp = User.objects.setup_otp(self.admin1)
        self.assertEqual(401, anonymous.post(verify_endpoint, data={"otp": otp}).status_code)

    def test_email_change_without_smtp(self) -> None:
        client = APIClient()
        client.force_authenticate(self.admin1)
        response = client.put(self.endpoint, data={**new_profile, "email": "another@rekono.com"})
        self.assertEqual(400, response.status_code)

    def test_notification_scope(self) -> None:
        notification = SMTP()
        users_to_notify = list(notification._get_users_to_notify_execution(self.execution))
        self.assertEqual(1, len(users_to_notify))
        self.assertEqual(self.auditor1, users_to_notify[0])

        for not_executor in [self.admin1, self.reader1]:
            not_executor.notification_scope = Notification.ALL_EXECUTIONS
            not_executor.save(update_fields=["notification_scope"])

        users_to_notify = list(notification._get_users_to_notify_execution(self.execution))
        self.assertEqual(3, len(users_to_notify))
        self.assertEqual(self.admin1, users_to_notify[0])
        self.assertEqual(self.auditor1, users_to_notify[1])
        self.assertEqual(self.reader1, users_to_notify[2])

        self.auditor1.notification_scope = Notification.DISABLED
        self.auditor1.save(update_fields=["notification_scope"])
        self.execution = Execution.objects.get(pk=self.execution.id)
        users_to_notify = list(notification._get_users_to_notify_execution(self.execution))
        self.assertEqual(2, len(users_to_notify))
        self.assertEqual(self.admin1, users_to_notify[0])
        self.assertEqual(self.reader1, users_to_notify[1])

        notification.process_findings(self.execution, [])


class ResetPasswordTest(ApiTestNoData, TestCase):
    endpoint = "/api/users/reset-password/"
    anonymous_access_allowed = None

    def test_reset_password(self) -> None:
        client = APIClient()
        client.force_authenticate(self.admin1)
        self.assertEqual(403, client.post(self.endpoint, data={"email": self.admin1.email}).status_code)

        client = APIClient()
        self.assertEqual(200, client.post(self.endpoint, data={"email": "notfound@rekono.com"}).status_code)
        self.assertEqual(200, client.post(self.endpoint, data={"email": self.admin1.email}).status_code)

        otp = User.objects.setup_otp(User.objects.get(email=self.admin1.email))
        self.assertEqual(
            401, client.put(self.endpoint, data={"otp": "invalid OTP", "password": new_valid_password}).status_code
        )
        self.assertEqual(400, client.put(self.endpoint, data={"otp": otp, "password": invalid_password2}).status_code)

        client.force_authenticate(self.admin1)
        self.assertEqual(403, client.put(self.endpoint, data={"otp": otp, "password": new_valid_password}).status_code)

        client = APIClient()
        response = client.put(self.endpoint, data={"otp": otp, "password": new_valid_password})
        self.assertEqual(200, response.status_code)
        for cookie in [JWT_ACCESS_COOKIE, JWT_REFRESH_COOKIE]:
            self.assertIn(cookie, response.cookies)
            self.assertEqual("", response.cookies[cookie].value)
        self.assertEqual(401, client.put(self.endpoint, data={"otp": otp, "password": new_valid_password}).status_code)

        response = client.post(
            "/api/security/login/", data={"username": self.admin1.username, "password": new_valid_password}
        )
        self.assertEqual(200, response.status_code)
