from typing import Any

from platforms.telegram_app.models import TelegramChat
from tests.cases import ApiTestCase
from tests.framework import ApiTest
from users.models import User


class TelegramChatTest(ApiTest):
    endpoint = "/api/telegram/link/"
    expected_str = "admin1@rekono.com"
    cases = [
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected={"telegram_chat": None},
            endpoint="/api/profile/",
        ),
    ]

    def test_link(self) -> None:
        chat_id = 1
        users = [
            self.admin1,
            self.admin2,
            self.auditor1,
            self.auditor2,
            self.reader1,
            self.reader2,
        ]
        for user in users:
            otp = User.objects.generate_otp(TelegramChat)
            chat = TelegramChat.objects.create(
                otp=otp,
                otp_expiration=User.objects.get_otp_expiration_time(),
                chat_id=chat_id,
            )
            self.assertFalse(chat.is_auditor())
            ApiTestCase(
                [user.username], "post", 401, {"otp": "invalid token"}
            ).test_case(endpoint=self.endpoint)
            ApiTestCase(
                [user.username],
                "post",
                201,
                {"otp": otp},
                {"id": chat.id, "user": user.id},
            ).test_case(endpoint=self.endpoint)
            self.assertEqual(
                user in [self.admin1, self.admin2, self.auditor1, self.auditor2],
                TelegramChat.objects.get(pk=chat.id).is_auditor(),
            )
            ApiTestCase(
                [user.username],
                "get",
                200,
                expected={
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "telegram_chat": chat.id,
                },
            ).test_case(endpoint=self.profile)
            chat_id += 1
        for index, user in enumerate(users):
            for id in range(1, chat_id):
                if id != index + 1:
                    ApiTestCase(
                        [user.username], "delete", 403, endpoint=f"{{endpoint}}{id}/"
                    ).test_case(endpoint=self.endpoint)
        for index, user in enumerate(users):
            ApiTestCase(
                [user.username], "delete", 204, endpoint=f"{{endpoint}}{index + 1}/"
            ).test_case(endpoint=self.endpoint)
            ApiTestCase(
                [user.username],
                "get",
                200,
                expected={
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "telegram_chat": None,
                },
            ).test_case(endpoint=self.profile),

    def _get_object(self) -> Any:
        return TelegramChat.objects.create(user=self.admin1, chat_id=1)
