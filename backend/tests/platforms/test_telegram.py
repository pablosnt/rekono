from functools import cached_property
from unittest import mock

from django.test import TestCase
from telegram.error import TimedOut

from platforms.telegram_app.models import TelegramChat
from security.authorization.roles import Role
from security.cryptography import Crypto
from tests.framework import ApiTestNoData
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase, PutApiTestCase
from users.models import User

# pytype: disable=wrong-arg-types,attribute-error

token = {"token": "any_valid_telegram_token"}
invalid_token = {"token": "invalid;token"}
expected = {"id": 1, "bot": None, "is_available": False}


class TelegramSettingsTest(ApiTestNoData, TestCase):
    endpoint = "/api/telegram/settings/1/"
    cases = [
        ApiTestCase(["members", "not_members"], expected=expected),
        PutApiTestCase([Role.AUDITOR, Role.READER], 403, token),
        PutApiTestCase([Role.ADMIN], 400, invalid_token),
        PutApiTestCase([Role.ADMIN], data=token, expected=expected),
        ApiTestCase(["members", "not_members"], expected=expected),
    ]

    def test_settings_when_telegram_api_is_unreachable(self) -> None:
        def raise_timeout(coroutine: object) -> None:
            coroutine.close()  # Avoid "coroutine was never awaited" warnings from the mocked run
            raise TimedOut()

        with mock.patch("platforms.telegram_app.framework.asyncio.run", side_effect=raise_timeout):
            PutApiTestCase([Role.ADMIN], data=token, expected={"id": 1, "bot": None}).test_case(1, self, self.endpoint)
            ApiTestCase(["members"], expected={"id": 1, "bot": None}).test_case(1, self, self.endpoint)


class TelegramChatTest(ApiTestNoData, TestCase):
    endpoint = "/api/telegram/link/"
    expected_string = "admin1@rekono.com - 1"
    cases = [ApiTestCase(["members", "not_members"], expected={"telegram_chat": None}, endpoint="/api/profile/")]

    def test_link(self) -> None:
        chat_id = 1
        for role, users in self.users.items():
            for user in users:
                otp = User.objects.generate_otp(TelegramChat)
                chat = TelegramChat.objects.create(
                    otp=Crypto.hash(otp), otp_expiration=User.objects.get_otp_expiration_time(), chat_id=chat_id
                )
                self.assertFalse(chat.is_auditor())
                PostApiTestCase([user.username], status_code=401, data={"otp": "invalid token"}).test_case(
                    1, self, self.endpoint
                )
                PostApiTestCase(
                    [user.username], data={"otp": otp}, expected={"id": chat.id, "user": user.id}
                ).test_case(1, self, self.endpoint)
                self.assertEqual(role in [Role.ADMIN, Role.AUDITOR], TelegramChat.objects.get(pk=chat.id).is_auditor())
                ApiTestCase(
                    [user.username],
                    expected={"id": user.id, "username": user.username, "email": user.email, "telegram_chat": chat.id},
                ).test_case(1, self, "/api/profile/")
                chat_id += 1
        for _user in self.members + self.not_members:
            user = User.objects.get(pk=_user.id)
            for _chat_id in range(1, chat_id):
                if _chat_id != user.telegram_chat.id:
                    DeleteApiTestCase([user.username], status_code=403, endpoint=str(_chat_id)).test_case(
                        1, self, self.endpoint
                    )
        for _user in self.members + self.not_members:
            user = User.objects.get(pk=_user.id)
            DeleteApiTestCase([user.username], endpoint=str(user.telegram_chat.id)).test_case(1, self, self.endpoint)
            ApiTestCase(
                [user.username],
                expected={"id": user.id, "username": user.username, "email": user.email, "telegram_chat": None},
            ).test_case(1, self, "/api/profile/")

    def test_link_rejected_when_already_linked(self) -> None:
        user = self.admin1
        first_otp = User.objects.generate_otp(TelegramChat)
        TelegramChat.objects.create(
            otp=Crypto.hash(first_otp), otp_expiration=User.objects.get_otp_expiration_time(), chat_id=500
        )
        PostApiTestCase([user.username], data={"otp": first_otp}).test_case(1, self, self.endpoint)

        # Second link attempt by an already-linked user
        second_otp = User.objects.generate_otp(TelegramChat)
        TelegramChat.objects.create(
            otp=Crypto.hash(second_otp), otp_expiration=User.objects.get_otp_expiration_time(), chat_id=501
        )
        PostApiTestCase([user.username], status_code=400, data={"otp": second_otp}).test_case(1, self, self.endpoint)

    @cached_property
    def object(self) -> TelegramChat:
        return TelegramChat.objects.create(user=self.admin1, chat_id=1)
