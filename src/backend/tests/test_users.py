from typing import Any

from security.authorization.roles import Role
from security.cryptography.hashing import hash
from tests.cases import ApiTestCase
from tests.framework import ApiTest
from users.enums import Notification
from users.models import User

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
new_invalid_password = "new password"

user1 = {
    "username": "test1",
    "first_name": "test",
    "last_name": "test",
    "password": new_valid_password,
}
invalid_user1 = {**user1, "username": "test;1"}
invalid_user2 = {**user1, "password": new_invalid_password}
invalid_user3 = {**user1, "first_name": "test;1"}


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
        ApiTestCase(["admin2"], "get", 200, endpoint="{endpoint}?no_project=1"),
        ApiTestCase(
            ["auditor1", "auditor2", "reader1", "reader2"], "post", 403, invitation1
        ),
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
        ApiTestCase(
            ["auditor1", "auditor2", "reader1"], "get", 403, endpoint="{endpoint}2/"
        ),
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

    def test_invite_and_create(self) -> None:
        client = self._get_api_client()
        response = client.post(
            self.login,
            data={"username": self.admin1.username, "password": self.admin1.username},
        )
        self.assertEqual(200, response.status_code)
        authenticated_client = self._get_api_client(
            self._get_content(response.content)["access"]
        )

        response = authenticated_client.post(self.endpoint, data=invitation1)
        self.assertEqual(201, response.status_code)
        new_user = User.objects.get(email=invitation1["email"])
        otp = User.objects.generate_otp()
        new_user.otp = hash(otp)
        new_user.save(update_fields=["otp"])

        response = authenticated_client.post(
            f"{self.endpoint}create/", data={"otp": otp, **user1}
        )
        self.assertEqual(403, response.status_code)

        response = client.post(
            f"{self.endpoint}create/", data={"otp": "invalid otp", **user1}
        )
        self.assertEqual(401, response.status_code)

        for invalid_user in [invalid_user1, invalid_user2, invalid_user3]:
            response = client.post(
                f"{self.endpoint}create/", data={"otp": otp, **invalid_user}
            )
            self.assertEqual(400, response.status_code)

        new_user.is_active = True
        new_user.save(update_fields=["is_active"])
        response = client.post(f"{self.endpoint}create/", data={"otp": otp, **user1})
        self.assertEqual(401, response.status_code)

        new_user.is_active = None
        new_user.save(update_fields=["is_active"])
        response = client.post(f"{self.endpoint}create/", data={"otp": otp, **user1})
        self.assertEqual(201, response.status_code)
        content = self._get_content(response.content)
        self.assertEqual(7, content["id"])
        self.assertTrue(content["is_active"])

        response = client.post(
            f"{self.endpoint}create/",
            data={"otp": otp, **user1, "username": "unique new test"},
        )
        self.assertEqual(401, response.status_code)

        response = client.post(
            self.login,
            data={"username": user1["username"], "password": new_valid_password},
        )
        self.assertEqual(200, response.status_code)
        authenticated_client = self._get_api_client(
            self._get_content(response.content)["access"]
        )

        response = authenticated_client.get(self.profile)
        self.assertEqual(200, response.status_code)

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
            endpoint="/api/security/update-password/",
        ),
        ApiTestCase(
            ["admin1"],
            "put",
            400,
            {"password": new_invalid_password, "old_password": "admin1"},
            endpoint="/api/security/update-password/",
        ),
        ApiTestCase(
            ["admin1"],
            "put",
            200,
            {"password": new_valid_password, "old_password": "admin1"},
            endpoint="/api/security/update-password/",
        ),
        ApiTestCase(["admin1"], "get", 401),
        ApiTestCase(
            [("admin1", new_valid_password)],
            "get",
            200,
            expected={"id": 1, "username": "admin1", "role": Role.ADMIN.value},
        ),
    ]


class ResetPasswordTest(ApiTest):
    endpoint = "/api/security/reset-password/"
    anonymous_allowed = None

    def test_reset_password(self) -> None:
        response = self._get_api_client().post(
            self.login,
            data={"username": self.admin1.username, "password": self.admin1.username},
        )
        self.assertEqual(200, response.status_code)
        authenticated_client = self._get_api_client(
            self._get_content(response.content)["access"]
        )

        response = authenticated_client.post(
            self.endpoint, data={"email": self.admin1.email}
        )
        self.assertEqual(403, response.status_code)

        client = self._get_api_client()
        response = client.post(self.endpoint, data={"email": self.admin1.email})
        self.assertEqual(200, response.status_code)
        user = User.objects.get(email=self.admin1.email)
        otp = User.objects.generate_otp()
        user.otp = hash(otp)
        user.save(update_fields=["otp"])

        response = client.put(
            self.endpoint, data={"otp": "invalid OTP", "password": new_valid_password}
        )
        self.assertEqual(401, response.status_code)

        response = client.put(
            self.endpoint,
            data={"otp": otp, "password": new_invalid_password},
        )
        self.assertEqual(400, response.status_code)

        response = authenticated_client.put(
            self.endpoint,
            data={"otp": otp, "password": new_valid_password},
        )
        self.assertEqual(403, response.status_code)

        response = client.put(
            self.endpoint,
            data={"otp": otp, "password": new_valid_password},
        )
        self.assertEqual(200, response.status_code)

        response = client.put(
            self.endpoint,
            data={"otp": otp, "password": new_valid_password},
        )
        self.assertEqual(401, response.status_code)

        response = self._get_api_client().post(
            self.login,
            data={"username": self.admin1.username, "password": new_valid_password},
        )
        self.assertEqual(200, response.status_code)
        authenticated_client = self._get_api_client(
            self._get_content(response.content)["access"]
        )
        response = authenticated_client.get(self.profile)
        self.assertEqual(200, response.status_code)
