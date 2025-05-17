from typing import Any, cast
from unittest import mock

from platforms.mail.notifications import SMTP
from platforms.telegram_app.models import TelegramChat
from security.authorization.roles import Role
from tests.cases import ApiTestCase
from tests.framework import ApiTest
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

user1 = {
    "username": "test1",
    "first_name": "test",
    "last_name": "test",
    "password": new_valid_password,
}

invalid_user1 = {**user1, "password": invalid_password1}
invalid_user2 = {**user1, "password": invalid_password2}
invalid_user3 = {**user1, "password": invalid_password3}
invalid_user4 = {**user1, "password": invalid_password4}
invalid_user5 = {**user1, "password": invalid_password5}
invalid_user6 = {**user1, "username": "test;1", "first_name": "test;1"}


class UserTest(ApiTest):
    endpoint = "/api/users/"
    expected_str = "admin1@rekono.com"
    cases = [
        ApiTestCase(["auditor1", "auditor2", "reader1", "reader2"], "get", 403),
        ApiTestCase(
            ["admin1", "admin2"],
            "get",
            200,
            expected=[
                {
                    "id": 6,
                    "username": "reader2",
                    "role": Role.READER.value,
                    "is_active": True,
                },
                {
                    "id": 5,
                    "username": "reader1",
                    "role": Role.READER.value,
                    "is_active": True,
                },
                {
                    "id": 4,
                    "username": "auditor2",
                    "role": Role.AUDITOR.value,
                    "is_active": True,
                },
                {
                    "id": 3,
                    "username": "auditor1",
                    "role": Role.AUDITOR.value,
                    "is_active": True,
                },
                {
                    "id": 2,
                    "username": "admin2",
                    "role": Role.ADMIN.value,
                    "is_active": True,
                },
                {
                    "id": 1,
                    "username": "admin1",
                    "role": Role.ADMIN.value,
                    "is_active": True,
                },
            ],
        ),
        ApiTestCase(
            ["admin1"],
            "get",
            200,
            expected=[
                {
                    "id": 5,
                    "username": "reader1",
                    "role": Role.READER.value,
                    "is_active": True,
                },
                {
                    "id": 3,
                    "username": "auditor1",
                    "role": Role.AUDITOR.value,
                    "is_active": True,
                },
                {
                    "id": 1,
                    "username": "admin1",
                    "role": Role.ADMIN.value,
                    "is_active": True,
                },
            ],
            endpoint="{endpoint}?project=1",
        ),
        ApiTestCase(
            ["admin1"],
            "get",
            200,
            expected=[
                {
                    "id": 6,
                    "username": "reader2",
                    "role": Role.READER.value,
                    "is_active": True,
                },
                {
                    "id": 4,
                    "username": "auditor2",
                    "role": Role.AUDITOR.value,
                    "is_active": True,
                },
                {
                    "id": 2,
                    "username": "admin2",
                    "role": Role.ADMIN.value,
                    "is_active": True,
                },
            ],
            endpoint="{endpoint}?no_project=1",
        ),
        ApiTestCase(["admin2"], "get", 200, endpoint="{endpoint}?project=1"),
        ApiTestCase(
            ["admin2"],
            "get",
            200,
            expected=[],
            endpoint="{endpoint}?no_project=1",
        ),
        ApiTestCase(["auditor1", "auditor2", "reader1", "reader2"], "post", 403, invitation1),
        ApiTestCase(["admin1", "admin2"], "post", 400, invalid_invitation),
        ApiTestCase(
            ["admin1"],
            "post",
            201,
            invitation1,
            {"id": 7, **invitation1, "is_active": None},
        ),
        ApiTestCase(["admin1", "admin2"], "post", 400, invitation1),
        ApiTestCase(
            ["admin2"],
            "post",
            201,
            invitation2,
            {"id": 8, **invitation2, "is_active": None},
        ),
        ApiTestCase(
            ["admin1"],
            "put",
            403,
            {"role": Role.AUDITOR.value},
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin1", "admin2"],
            "put",
            200,
            {"role": Role.ADMIN.value},
            expected={
                "id": 6,
                "username": "reader2",
                "role": Role.ADMIN.value,
                "is_active": True,
            },
            endpoint="{endpoint}6/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "reader2"],
            "get",
            200,
            expected=[
                {
                    "id": 8,
                    "username": None,
                    "email": "test2@rekono.com",
                    "role": Role.AUDITOR.value,
                    "is_active": None,
                },
                {
                    "id": 7,
                    "username": None,
                    "email": "test1@rekono.com",
                    "role": Role.READER.value,
                    "is_active": None,
                },
                {
                    "id": 6,
                    "username": "reader2",
                    "role": Role.ADMIN.value,
                    "is_active": True,
                },
                {
                    "id": 5,
                    "username": "reader1",
                    "role": Role.READER.value,
                    "is_active": True,
                },
                {
                    "id": 4,
                    "username": "auditor2",
                    "role": Role.AUDITOR.value,
                    "is_active": True,
                },
                {
                    "id": 3,
                    "username": "auditor1",
                    "role": Role.AUDITOR.value,
                    "is_active": True,
                },
                {
                    "id": 2,
                    "username": "admin2",
                    "role": Role.ADMIN.value,
                    "is_active": True,
                },
                {
                    "id": 1,
                    "username": "admin1",
                    "role": Role.ADMIN.value,
                    "is_active": True,
                },
            ],
        ),
        ApiTestCase(["admin2"], "delete", 403, endpoint="{endpoint}2/"),
        ApiTestCase(["admin1", "reader2"], "delete", 204, endpoint="{endpoint}2/"),
        ApiTestCase(["admin2"], "get", 401),
        ApiTestCase(["auditor1", "auditor2", "reader1"], "get", 403, endpoint="{endpoint}2/"),
        ApiTestCase(
            ["admin1", "reader2"],
            "get",
            200,
            expected={
                "id": 2,
                "username": "admin2",
                "role": Role.ADMIN.value,
                "is_active": False,
            },
            endpoint="{endpoint}2/",
        ),
        ApiTestCase(
            ["reader2"],
            "post",
            200,
            expected={
                "id": 2,
                "username": "admin2",
                "role": Role.ADMIN.value,
                "is_active": True,
            },
            endpoint="{endpoint}2/enable/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "reader2"],
            "get",
            200,
            expected={
                "id": 2,
                "username": "admin2",
                "role": Role.ADMIN.value,
                "is_active": True,
            },
            endpoint="{endpoint}2/",
        ),
        ApiTestCase(
            ["admin1", "admin2"],
            "put",
            200,
            {"role": Role.READER.value},
            expected={
                "id": 6,
                "username": "reader2",
                "role": Role.READER.value,
                "is_active": True,
            },
            endpoint="{endpoint}6/",
        ),
        ApiTestCase(
            ["admin1", "admin2"],
            "get",
            200,
            expected={
                "id": 6,
                "username": "reader2",
                "role": Role.READER.value,
                "is_active": True,
            },
            endpoint="{endpoint}6/",
        ),
        ApiTestCase(
            ["auditor1", "auditor2", "reader1", "reader2"],
            "get",
            403,
            endpoint="{endpoint}6/",
        ),
        ApiTestCase(["admin1"], "delete", 204, endpoint="{endpoint}7/"),
        ApiTestCase(["admin2"], "delete", 404, endpoint="{endpoint}7/"),
        ApiTestCase(["admin1", "admin2"], "get", 404, endpoint="{endpoint}7/"),
        ApiTestCase(["admin2"], "delete", 204, endpoint="{endpoint}8/"),
        ApiTestCase(["admin1", "admin2"], "get", 404, endpoint="{endpoint}8/"),
    ]

    def setUp(self) -> None:
        super().setUp()
        self._setup_project()

    @mock.patch("platforms.mail.notifications.SMTP.is_available", lambda self: True)
    def test_cases(self) -> None:
        super().test_cases()

    def test_invite_and_create_without_smtp(self) -> None:
        client = self._get_api_client()
        response = client.post(
            self.login,
            data={"username": self.admin1.username, "password": self.admin1.username},
        )
        self.assertEqual(200, response.status_code)
        authenticated_client = self._get_api_client(self._get_content(response.content)["access"])

        self.assertEqual(400, authenticated_client.post(self.endpoint, data=invitation1).status_code)

    @mock.patch("platforms.mail.notifications.SMTP.is_available", lambda self: True)
    def test_invite_and_create(self) -> None:
        client = self._get_api_client()
        response = client.post(
            self.login,
            data={"username": self.admin1.username, "password": self.admin1.username},
        )
        self.assertEqual(200, response.status_code)
        authenticated_client = self._get_api_client(self._get_content(response.content)["access"])

        self.assertEqual(201, authenticated_client.post(self.endpoint, data=invitation1).status_code)
        new_user = User.objects.get(email=invitation1["email"])
        otp = User.objects.setup_otp(new_user)

        self.assertEqual(
            403,
            authenticated_client.post(f"{self.endpoint}signup/", data={"otp": otp, **user1}).status_code,
        )

        self.assertEqual(
            401,
            client.post(f"{self.endpoint}signup/", data={"otp": "invalid otp", **user1}).status_code,
        )

        for invalid_user in [
            invalid_user1,
            invalid_user2,
            invalid_user3,
            invalid_user4,
            invalid_user5,
            invalid_user6,
        ]:
            self.assertEqual(
                400,
                client.post(f"{self.endpoint}signup/", data={"otp": otp, **invalid_user}).status_code,
            )

        new_user.is_active = True
        new_user.save(update_fields=["is_active"])
        self.assertEqual(
            401,
            client.post(f"{self.endpoint}signup/", data={"otp": otp, **user1}).status_code,
        )

        new_user.is_active = None
        new_user.save(update_fields=["is_active"])
        response = client.post(f"{self.endpoint}signup/", data={"otp": otp, **user1})
        self.assertEqual(201, response.status_code)
        content = self._get_content(response.content)
        self.assertEqual(7, content["id"])
        self.assertTrue(content["is_active"])

        self.assertEqual(
            401,
            client.post(
                f"{self.endpoint}signup/",
                data={"otp": otp, **user1, "username": "unique new test"},
            ).status_code,
        )

        response = client.post(
            self.login,
            data={"username": user1["username"], "password": new_valid_password},
        )
        self.assertEqual(200, response.status_code)
        authenticated_client = self._get_api_client(self._get_content(response.content)["access"])

        self.assertEqual(200, authenticated_client.get(self.profile).status_code)

    def test_create_superuser(self) -> None:
        value = "superuser"
        superuser = User.objects.create_superuser(value, f"{value}@rekono.com", value)
        self.assertTrue(superuser.is_active)
        self.assertEqual(Role.ADMIN.value, superuser.groups.first().name)

    def _get_object(self) -> Any:
        return self.admin1


class Profile(ApiTest):
    endpoint = "/api/profile/"
    cases = [
        ApiTestCase(
            ["admin1"],
            "get",
            200,
            expected={"id": 1, "username": "admin1", "role": Role.ADMIN.value},
        ),
        ApiTestCase(
            ["auditor1"],
            "get",
            200,
            expected={"id": 3, "username": "auditor1", "role": Role.AUDITOR.value},
        ),
        ApiTestCase(
            ["reader1"],
            "get",
            200,
            expected={"id": 5, "username": "reader1", "role": Role.READER.value},
        ),
        ApiTestCase(
            ["admin2"],
            "put",
            200,
            new_profile,
            {
                "id": 2,
                "username": "admin2",
                "email": "admin2@rekono.com",
                "role": Role.ADMIN.value,
                **new_profile,
            },
        ),
        ApiTestCase(
            ["admin1"],
            "put",
            401,
            {"password": new_valid_password, "old_password": "invalid password"},
            endpoint="/api/profile/update-password/",
        ),
        ApiTestCase(
            ["admin1"],
            "put",
            400,
            {"password": invalid_password1, "old_password": "admin1"},
            endpoint="/api/profile/update-password/",
        ),
        ApiTestCase(
            ["admin1"],
            "put",
            200,
            {"password": new_valid_password, "old_password": "admin1"},
            endpoint="/api/profile/update-password/",
        ),
        ApiTestCase(["admin1"], "get", 401),
        ApiTestCase(
            [("admin1", new_valid_password)],
            "get",
            200,
            expected={"id": 1, "username": "admin1", "role": Role.ADMIN.value},
        ),
    ]

    def setUp(self) -> None:
        super().setUp()
        self.admin1_telegram_chat = TelegramChat.objects.create(user=cast(User, self.admin1), chat_id=1)

    def test_cases(self) -> None:
        self.assertEqual(
            self.admin1_telegram_chat.chat_id,
            cast(User, self.admin1).telegram_chat.chat_id,
        )
        super().test_cases()
        # Linked Telegram Chats are removed after a password change
        self.assertFalse(hasattr(User.objects.get(pk=cast(User, self.admin1).id), "telegram_chat"))

    def test_notification_scope(self) -> None:
        self._setup_tasks_and_executions()
        notification = SMTP()
        users_to_notify = list(notification._get_users_to_notify_execution(self.execution1))
        self.assertEqual(1, len(users_to_notify))
        self.assertEqual(self.admin1, users_to_notify[0])

        for user_not_executor in [self.auditor1, self.reader1]:
            user_not_executor.notification_scope = Notification.ALL_EXECUTIONS
            user_not_executor.save(update_fields=["notification_scope"])

        users_to_notify = list(notification._get_users_to_notify_execution(self.execution1))
        self.assertEqual(3, len(users_to_notify))
        self.assertEqual(self.admin1, users_to_notify[0])
        self.assertEqual(self.auditor1, users_to_notify[1])
        self.assertEqual(self.reader1, users_to_notify[2])

        self.admin1.notification_scope = Notification.DISABLED
        self.admin1.save(update_fields=["notification_scope"])
        users_to_notify = list(notification._get_users_to_notify_execution(self.execution1))
        self.assertEqual(2, len(users_to_notify))
        self.assertEqual(self.auditor1, users_to_notify[0])
        self.assertEqual(self.reader1, users_to_notify[1])

        notification.process_findings(self.execution1, [])


class ResetPasswordTest(ApiTest):
    endpoint = "/api/users/reset-password/"
    anonymous_allowed = None

    def test_reset_password(self) -> None:
        client = self._get_api_client()
        response = client.post(
            self.login,
            data={"username": self.admin1.username, "password": self.admin1.username},
        )
        self.assertEqual(200, response.status_code)
        authenticated_client = self._get_api_client(self._get_content(response.content)["access"])

        self.assertEqual(
            403,
            authenticated_client.post(self.endpoint, data={"email": self.admin1.email}).status_code,
        )

        self.assertEqual(
            200,
            client.post(self.endpoint, data={"email": "notfound@rekono.com"}).status_code,
        )

        self.assertEqual(
            200,
            client.post(self.endpoint, data={"email": self.admin1.email}).status_code,
        )
        otp = User.objects.setup_otp(User.objects.get(email=self.admin1.email))

        self.assertEqual(
            401,
            client.put(
                self.endpoint,
                data={"otp": "invalid OTP", "password": new_valid_password},
            ).status_code,
        )

        self.assertEqual(
            400,
            client.put(
                self.endpoint,
                data={"otp": otp, "password": invalid_password2},
            ).status_code,
        )

        self.assertEqual(
            403,
            authenticated_client.put(
                self.endpoint,
                data={"otp": otp, "password": new_valid_password},
            ).status_code,
        )

        self.assertEqual(
            200,
            client.put(
                self.endpoint,
                data={"otp": otp, "password": new_valid_password},
            ).status_code,
        )

        self.assertEqual(
            401,
            client.put(
                self.endpoint,
                data={"otp": otp, "password": new_valid_password},
            ).status_code,
        )

        response = self._get_api_client().post(
            self.login,
            data={"username": self.admin1.username, "password": new_valid_password},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            200,
            self._get_api_client(self._get_content(response.content)["access"]).get(self.profile).status_code,
        )
