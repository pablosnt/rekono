from tests.cases import ApiTestCase
from tests.framework import ApiTest

token = {"token": "any_valid_telegram_token"}
invalid_token = {"token": "invalid;token"}
expected = {"id": 1, "bot": None, "is_available": False}


class TelegramSettingsTest(ApiTest):
    endpoint = "/api/telegram/settings/1/"
    cases = [
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected=expected,
        ),
        ApiTestCase(["auditor1", "auditor2", "reader1", "reader2"], "put", 403, token),
        ApiTestCase(["admin1", "admin2"], "put", 400, invalid_token),
        ApiTestCase(["admin1", "admin2"], "put", 200, token, expected),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected=expected,
        ),
    ]
