import json
import time
from datetime import datetime, timedelta
from functools import cached_property
from typing import Any

import pyotp
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from rekono.settings import JWT_ACCESS_COOKIE, JWT_MFA_COOKIE, JWT_REFRESH_COOKIE
from security.validators.enums import Regex
from security.validators.input_validator import Validator
from security.validators.target_validator import TargetValidator
from tests.framework import ApiTest, ApiTestNoData
from tests.framework.cases import ApiTestCase, CustomApiTestCase
from users.models import User

# pytype: disable=wrong-arg-types,attribute-error


class SecurityTest(ApiTest, TestCase):
    data = []
    users_flag = True
    login = "/api/security/login/"
    refresh = "/api/security/refresh/"
    logout = "/api/security/logout/"
    api_tokens = "/api/api-tokens/"
    mfa_login = "/api/security/mfa/"
    mfa_user = "/api/profile/mfa/"
    profile = "/api/profile/"

    @cached_property
    def cases(self) -> list[ApiTestCase]:
        return [CustomApiTestCase(["members", "not_members"], endpoint=self.login, method="options")]

    def test_refresh_and_logout(self) -> None:
        client = APIClient()
        response = client.post(self.login, data={"username": self.admin1.username, "password": self.admin1.username})
        data = json.loads((response.content or "{}".encode()).decode())
        client = APIClient(HTTP_AUTHORIZATION=f"Bearer {data['access']}")

        # Get admin1's profile
        self.assertEqual(200, client.get(self.profile).status_code)

        # Refresh tokens
        self.assertEqual(401, client.post(self.refresh, data={"refresh": "invalid refresh token"}).status_code)
        response = client.post(self.refresh, data={"refresh": data["refresh"]})
        new_data = json.loads((response.content or "{}".encode()).decode())
        self.assertEqual(200, response.status_code)
        self.assertNotEqual(data["access"], new_data["access"])
        self.assertNotEqual(data["refresh"], new_data["refresh"])

        # Get admin1's profile with the new access token
        client = APIClient(HTTP_AUTHORIZATION=f"Bearer {new_data['access']}")
        self.assertEqual(200, client.get(self.profile).status_code)

        # Logout
        self.assertEqual(200, client.post(self.logout, {"refresh": new_data["refresh"]}).status_code)

        # Try to refresh tokens after logout
        self.assertEqual(401, client.post(self.refresh, data={"refresh": new_data["refresh"]}).status_code)

    def test_api_authentication(self) -> None:
        # Login as admin1
        client = APIClient()
        client.force_authenticate(self.admin1)

        # Create API token
        response = client.post(
            self.api_tokens, data={"name": "test1", "expiration": (timezone.now() + timedelta(seconds=3)).isoformat()}
        )
        self.assertEqual(201, response.status_code)
        data = json.loads((response.content or "{}".encode()).decode())
        api_client = APIClient(HTTP_AUTHORIZATION=f"Token {data['key']}")
        time.sleep(3)

        # Try to get admin1's profile using an expired token
        self.assertEqual(401, api_client.get(self.profile).status_code)

        # Create other API token
        response = client.post(
            self.api_tokens,
            data={"name": "test2", "expiration": (datetime.now() + timedelta(days=1)).isoformat() + "Z"},
        )
        self.assertEqual(201, response.status_code)
        data = json.loads((response.content or "{}".encode()).decode())
        api_client = APIClient(HTTP_AUTHORIZATION=f"Token {data['key']}")

        # Get admin1's profile
        self.assertEqual(200, api_client.get(self.profile).status_code)

        # MFA endpoints are not callable by using an API token
        for operation in ["register", "enable", "disable"]:
            self.assertEqual(401, api_client.post(f"{self.mfa_user}{operation}/").status_code)

    def test_mfa(self) -> None:
        # Login as admin1
        client = APIClient()
        client.force_authenticate(self.admin1)

        # Check current profile
        self.assertEqual(200, client.get(self.profile).status_code)

        # Before registering MFA, it can't be enabled
        self.assertEqual(400, client.post(f"{self.mfa_user}enable/", data={"mfa": "111111"}).status_code)

        # Register MFA app
        self.assertEqual(200, client.post(f"{self.mfa_user}register/").status_code)
        # Invalid MFA
        self.assertEqual(401, client.post(f"{self.mfa_user}enable/", data={"mfa": "1111111"}).status_code)
        # Valid MFA
        self.admin1 = User.objects.get(pk=self.admin1.id)
        mfa_otp = pyotp.TOTP(self.admin1.secret)
        response = client.post(f"{self.mfa_user}enable/", data={"mfa": mfa_otp.now()})
        self.assertEqual(200, response.status_code)
        self.assertTrue(json.loads((response.content or "{}".encode()).decode()).get("mfa"))

        # After enabling MFA, it can't be registered again
        self.assertEqual(400, client.post(f"{self.mfa_user}register/").status_code)

        # After enabling MFA, it can't be enabled again
        self.assertEqual(400, client.post(f"{self.mfa_user}enable/", data={"mfa": mfa_otp.now()}).status_code)

        # Login with MFA app
        response = APIClient().post(
            self.login, data={"username": self.admin1.username, "password": self.admin1.username}
        )
        self.assertEqual(200, response.status_code)
        content = json.loads((response.content or "{}".encode()).decode())
        self.assertIsNotNone(content.get("mfa"))
        self.assertIn(JWT_MFA_COOKIE, response.cookies)
        self.assertNotIn(JWT_ACCESS_COOKIE, response.cookies)
        self.assertNotIn(JWT_REFRESH_COOKIE, response.cookies)
        # Partial authenticated token is not valid to access API
        mfa_client = APIClient(HTTP_AUTHORIZATION=f"Bearer {content.get('mfa')}")
        self.assertEqual(401, mfa_client.get(self.profile).status_code)
        # Invalid token
        self.assertEqual(
            401, APIClient().post(self.mfa_login, data={"token": "invalid JWT", "mfa": mfa_otp.now()}).status_code
        )
        # Invalid MFA
        self.assertEqual(
            401, APIClient().post(self.mfa_login, data={"token": content.get("mfa"), "mfa": "1111111"}).status_code
        )
        # Valid token and MFA
        mfa_token = content.get("mfa")
        response = APIClient().post(self.mfa_login, data={"token": mfa_token, "mfa": mfa_otp.now()})
        self.assertEqual(200, response.status_code)
        content = json.loads((response.content or "{}".encode()).decode())
        self.assertIsNotNone(content.get("access"))
        self.assertIn(JWT_ACCESS_COOKIE, response.cookies)
        self.assertIn(JWT_REFRESH_COOKIE, response.cookies)
        client = APIClient(HTTP_AUTHORIZATION=f"Bearer {content.get('access')}")
        self.assertEqual(200, client.get(self.profile).status_code)
        # The MFA token is single-use: replaying it after a successful login is rejected
        self.assertEqual(
            401, APIClient().post(self.mfa_login, data={"token": mfa_token, "mfa": mfa_otp.now()}).status_code
        )

        # Login with MFA via cookies
        response = APIClient().post(
            self.login, data={"username": self.admin1.username, "password": self.admin1.username}
        )
        self.assertEqual(200, response.status_code)
        self.assertIn(JWT_MFA_COOKIE, response.cookies)
        mfa_client = APIClient()
        # Invalid token via cookie
        mfa_client.cookies[JWT_MFA_COOKIE] = "invalid JWT"
        self.assertEqual(401, mfa_client.post(self.mfa_login, data={"mfa": mfa_otp.now()}).status_code)
        mfa_client.cookies[JWT_MFA_COOKIE] = response.cookies[JWT_MFA_COOKIE].value
        response = mfa_client.post(self.mfa_login, data={"mfa": mfa_otp.now()})
        self.assertEqual(200, response.status_code)
        self.assertIn("access", json.loads(response.content.decode()))
        self.assertIn(JWT_ACCESS_COOKIE, response.cookies)
        self.assertIn(JWT_REFRESH_COOKIE, response.cookies)
        self.assertEqual("", response.cookies[JWT_MFA_COOKIE].value)

        # Login with email MFA
        response = APIClient().post(
            self.login, data={"username": self.admin1.username, "password": self.admin1.username}
        )
        self.assertEqual(200, response.status_code)
        content = json.loads((response.content or "{}".encode()).decode())
        self.assertIsNotNone(content.get("mfa"))
        # Partial authenticated token is not valid to access API
        self.assertEqual(
            401, APIClient(HTTP_AUTHORIZATION=f"Bearer {content.get('mfa')}").get(self.profile).status_code
        )
        # Request MFA via email
        self.assertEqual(400, APIClient().post(f"{self.mfa_login}email/").status_code)
        self.assertEqual(
            204,
            APIClient().post(f"{self.mfa_login}email/", data={"token": content.get("mfa")}).status_code,
        )
        plain_otp = User.objects.setup_otp(self.admin1)
        # Invalid token
        self.assertEqual(
            401, APIClient().post(self.mfa_login, data={"token": "invalid JWT", "mfa": plain_otp}).status_code
        )
        # Invalid MFA
        self.assertEqual(
            401, APIClient().post(self.mfa_login, data={"token": content.get("mfa"), "mfa": "1111111"}).status_code
        )
        # Valid token and MFA
        response = APIClient().post(self.mfa_login, data={"token": content.get("mfa"), "mfa": plain_otp})
        self.assertEqual(200, response.status_code)
        content = json.loads((response.content or "{}".encode()).decode())
        self.assertIsNotNone(content.get("access"))
        client = APIClient(HTTP_AUTHORIZATION=f"Bearer {content.get('access')}")
        self.assertEqual(200, client.get(self.profile).status_code)

        # After login with email MFA, disable MFA
        self.assertEqual(204, client.post(f"{self.mfa_login}email/").status_code)
        plain_otp = User.objects.setup_otp(self.admin1)
        # Invalid MFA
        self.assertEqual(401, client.post(f"{self.mfa_user}disable/", data={"mfa": "1111111"}).status_code)
        # Valid MFA
        response = client.post(f"{self.mfa_user}disable/", data={"mfa": plain_otp})
        self.assertEqual(200, response.status_code)
        self.assertFalse(json.loads((response.content or "{}".encode()).decode()).get("mfa"))

        # After disabling MFA, request MFA via email
        self.assertEqual(400, client.post(f"{self.mfa_login}email/").status_code)

        # After disabling MFA, it can't be disabled again
        self.assertEqual(
            400,
            client.post(f"{self.mfa_user}disable/", data={"mfa": plain_otp}).status_code,
        )

        # After disabling MFA, login again
        response = APIClient().post(
            self.login, data={"username": self.admin1.username, "password": self.admin1.username}
        )
        self.assertEqual(200, response.status_code)
        response = APIClient(HTTP_AUTHORIZATION=f"Bearer {content.get('access')}").get(self.profile)
        self.assertEqual(200, response.status_code)
        self.assertFalse(json.loads((response.content or "{}".encode()).decode()).get("mfa"))

    def test_access_token_via_cookie(self) -> None:
        # Login as admin1
        response = APIClient().post(
            self.login, data={"username": self.admin1.username, "password": self.admin1.username}
        )
        self.assertEqual(200, response.status_code)
        # Check cookies are set
        self.assertIn(JWT_ACCESS_COOKIE, response.cookies)
        self.assertIn(JWT_REFRESH_COOKIE, response.cookies)
        data = json.loads((response.content or "{}".encode()).decode())

        cookie_client = APIClient()
        # Invalid token via cookie
        cookie_client.cookies[JWT_ACCESS_COOKIE] = "invalid JWT"
        self.assertEqual(401, cookie_client.get(self.profile).status_code)

        # Authentication via cookie
        cookie_client.cookies[JWT_ACCESS_COOKIE] = data["access"]
        self.assertEqual(200, cookie_client.get(self.profile).status_code)

    def test_refresh_token_via_cookie(self) -> None:
        # Login as admin1
        response = APIClient().post(
            self.login, data={"username": self.admin1.username, "password": self.admin1.username}
        )
        data = json.loads((response.content or "{}".encode()).decode())

        # Authentication and refresh via cookie
        cookie_client = APIClient()
        cookie_client.cookies[JWT_ACCESS_COOKIE] = data["access"]

        # Invalid token via cookie
        cookie_client.cookies[JWT_REFRESH_COOKIE] = "invalid JWT"
        self.assertEqual(401, cookie_client.post(self.refresh).status_code)

        # Refresh tokens
        cookie_client.cookies[JWT_REFRESH_COOKIE] = data["refresh"]
        response = cookie_client.post(self.refresh)
        self.assertEqual(200, response.status_code)
        # New tokens are generated
        new_tokens = json.loads((response.content or "{}".encode()).decode())
        self.assertIn("access", new_tokens)
        self.assertIn("refresh", new_tokens)
        self.assertIn(JWT_ACCESS_COOKIE, response.cookies)
        self.assertIn(JWT_REFRESH_COOKIE, response.cookies)

    def test_logout_via_cookie(self) -> None:
        # Login as admin1
        login_response = APIClient().post(
            self.login, data={"username": self.admin1.username, "password": self.admin1.username}
        )
        data = json.loads(login_response.content.decode())
        cookie_client = APIClient()
        cookie_client.cookies[JWT_ACCESS_COOKIE] = data["access"]

        # Invalid token via cookie
        cookie_client.cookies[JWT_REFRESH_COOKIE] = "invalid JWT"
        self.assertEqual(401, cookie_client.post(self.logout).status_code)

        # Authentication and refresh via cookie
        cookie_client.cookies[JWT_REFRESH_COOKIE] = data["refresh"]
        response = cookie_client.post(self.logout)
        self.assertEqual(200, response.status_code)

        # The refresh token is no longer valid
        self.assertEqual(401, cookie_client.post(self.refresh, data={"refresh": data["refresh"]}).status_code)

        # No cookies available
        self.assertEqual("", response.cookies[JWT_ACCESS_COOKIE].value)
        self.assertEqual("", response.cookies[JWT_REFRESH_COOKIE].value)

    def test_input_validation_with_no_value(self) -> None:
        for validator in [Validator(Regex.CVE), TargetValidator(Regex.TARGET)]:
            exception = False
            try:
                validator(None)
            except ValidationError:
                exception = True
            self.assertTrue(exception)


BLOCKED = "https://evil.com/script.js"
ORIGIN = "https://rekono.com/projects/"
DIRECTIVE = "script-src"
INJECTED_BLOCKED = "https://evil.com/script.js\r\nWARNING forged log entry injected by attacker"


class CspReportTest(ApiTestNoData):
    endpoint = ""
    valid = {}
    no_origin = {}
    invalid = {}
    malicious = {}
    anonymous_access_allowed = None

    def _post(self, payload: dict[str, Any]) -> int:
        return APIClient().post(self.endpoint, data=payload, content_type="application/json").status_code

    def test_valid(self) -> None:
        self.assertEqual(204, self._post(self.valid))

    def test_no_origin(self) -> None:
        self.assertEqual(204, self._post(self.no_origin))

    def test_invalid(self) -> None:
        self.assertEqual(204, self._post(self.invalid))

    def test_log_injection(self) -> None:
        self.assertEqual(204, self._post(self.malicious))


class CspReportToTest(CspReportTest, TestCase):
    endpoint = "/api/csp-report-to/"
    valid = [
        {
            "type": "csp-violation",
            "url": ORIGIN,
            "body": {"blockedURL": BLOCKED, "documentUrl": ORIGIN, "effectiveDirective": DIRECTIVE},
        }
    ]
    no_origin = [{"type": "csp-violation", "body": {"blockedURL": BLOCKED, "effectiveDirective": DIRECTIVE}}]
    invalid = [
        {
            "type": "csp-violation",
            "url": ORIGIN,
            "body": {"documentUrl": ORIGIN, "effectiveDirective": DIRECTIVE},
        }
    ]
    malicious = [
        {
            "type": "csp-violation",
            "url": ORIGIN,
            "body": {"blockedURL": INJECTED_BLOCKED, "documentUrl": ORIGIN, "effectiveDirective": DIRECTIVE},
        }
    ]


class CspReportUriTest(CspReportTest, TestCase):
    endpoint = "/api/csp-report-uri/"
    valid = {"csp-report": {"blocked-uri": BLOCKED, "document-uri": ORIGIN, "effective-directive": DIRECTIVE}}
    no_origin = {"csp-report": {"blocked-uri": BLOCKED, "effective-directive": DIRECTIVE}}
    invalid = {"csp-report": {"blocked-uri": BLOCKED, "document-uri": ORIGIN}}
    malicious = {
        "csp-report": {"blocked-uri": INJECTED_BLOCKED, "document-uri": ORIGIN, "effective-directive": DIRECTIVE}
    }
