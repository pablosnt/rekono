from datetime import datetime, timedelta
from typing import Any

from api_tokens.models import ApiToken
from tests.cases import ApiTestCase
from tests.framework import ApiTest

api_token1 = {
    "name": "test1",
    "expiration": (datetime.now() + timedelta(days=365)).isoformat() + "Z",
}
invalid_api_token = {
    "name": "test;1",
    "expiration": (datetime.now() - timedelta(days=365)).isoformat() + "Z",
}


class ApiTokenTest(ApiTest):
    endpoint = "/api/api-tokens/"
    expected_str = f"admin1@rekono.com - {api_token1['name']}"
    cases = [
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected=[],
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            404,
            endpoint=f"{endpoint}1/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "post",
            400,
            invalid_api_token,
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "post",
            201,
            api_token1,
            api_token1,
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "post",
            400,
            api_token1
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected=[api_token1],
        ),
        ApiTestCase(
            ["admin1"], "get", 200, expected=api_token1, endpoint=f"{endpoint}1/"
        ),
        ApiTestCase(
            ["admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            404,
            endpoint=f"{endpoint}1/",
        ),
        ApiTestCase(
            ["auditor1"], "get", 200, expected=api_token1, endpoint=f"{endpoint}3/"
        ),
        ApiTestCase(
            ["reader1"], "get", 200, expected=api_token1, endpoint=f"{endpoint}5/"
        ),
        ApiTestCase(
            ["admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "delete",
            404,
            endpoint=f"{endpoint}1/",
        ),
        ApiTestCase(["admin1"], "delete", 204, endpoint=f"{endpoint}1/"),
        ApiTestCase(["admin2"], "delete", 204, endpoint=f"{endpoint}2/"),
        ApiTestCase(["auditor1"], "delete", 204, endpoint=f"{endpoint}3/"),
        ApiTestCase(["auditor2"], "delete", 204, endpoint=f"{endpoint}4/"),
        ApiTestCase(["reader1"], "delete", 204, endpoint=f"{endpoint}5/"),
        ApiTestCase(["reader2"], "delete", 204, endpoint=f"{endpoint}6/"),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "get",
            200,
            expected=[],
        ),
    ]

    def _get_object(self) -> Any:
        return ApiToken(**{"user": self.admin1, **api_token1})
