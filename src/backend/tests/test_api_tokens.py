from datetime import datetime, timedelta
from functools import cached_property

from api_tokens.models import ApiToken
from security.authorization.roles import Role
from tests.framework import ApiTest
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase

# pytype: disable=wrong-arg-types

expiration = (datetime.now() + timedelta(days=365)).isoformat() + "Z"
valid_api_token = {"name": "test1", "expiration": expiration}
invalid_api_token = {"name": "test;1", "expiration": expiration}


class ApiTokenTest(ApiTest):
    endpoint = "/api/api-tokens/"
    expected_string = f"admin1@rekono.com - {valid_api_token['name']}"
    cases = [
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 404, endpoint="1"),
        PostApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 400, invalid_api_token),
        PostApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], data=valid_api_token, expected=valid_api_token),
        PostApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], 400, valid_api_token),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER], expected=[valid_api_token]),
        ApiTestCase(["admin1"], expected=valid_api_token, endpoint="1"),
        ApiTestCase(["admin2", Role.AUDITOR, Role.READER], 404, endpoint="1"),
        ApiTestCase(["auditor1"], expected=valid_api_token, endpoint="3"),
        ApiTestCase(["reader1"], expected=valid_api_token, endpoint="5"),
        DeleteApiTestCase(["admin2", Role.AUDITOR, Role.READER], 404, endpoint="1"),
        DeleteApiTestCase(["admin1"], endpoint="1"),
        DeleteApiTestCase(["admin2"], endpoint="2"),
        DeleteApiTestCase(["auditor1"], endpoint="3"),
        DeleteApiTestCase(["auditor2"], endpoint="4"),
        DeleteApiTestCase(["reader1"], endpoint="5"),
        DeleteApiTestCase(["reader2"], endpoint="6"),
        ApiTestCase([Role.ADMIN, Role.AUDITOR, Role.READER]),
    ]

    @cached_property
    def object(self) -> ApiToken:
        return ApiToken(**{"user": self.admin1, **valid_api_token})
