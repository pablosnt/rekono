import time
from datetime import datetime, timedelta

import pyotp
from django.utils import timezone
from tests.cases import ApiTestCase
from tests.framework import ApiTest
from users.models import User


class SecurityTest(ApiTest):
    refresh = "/api/security/refresh/"
    logout = "/api/security/logout/"
    api_tokens = "/api/api-tokens/"
    mfa_login = "/api/security/mfa/"
    mfa_user = "/api/profile/mfa/"
    profile = "/api/profile/"
    cases = [
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2", "reader1", "reader2"],
            "options",
            200,
            endpoint=ApiTest.login,
        )
    ]
    admin1: User

    def test_refresh_and_logout(self) -> None:
        # Login as admin1
        response = self._get_api_client().post(
            self.login,
            data={"username": self.admin1.username, "password": self.admin1.username},
        )
        self.assertEqual(200, response.status_code)
        first_authentication = self._get_content(response.content)
        authenticated_client = self._get_api_client(first_authentication["access"])

        # Get admin1's profile
        response = authenticated_client.get(self.profile)
        self.assertEqual(200, response.status_code)
        content = self._get_content(response.content)
        self.assertEqual(self.admin1.id, content.get("id"))
        self.assertEqual(self.admin1.username, content.get("username"))

        # Try to refresh tokens using an invalid refresh token
        self.assertEqual(
            401,
            authenticated_client.post(self.refresh, data={"refresh": "invalid refresh token"}).status_code,
        )

        # Refresh tokens
        response = authenticated_client.post(self.refresh, data={"refresh": first_authentication["refresh"]})
        self.assertEqual(200, response.status_code)
        second_authentication = self._get_content(response.content)
        self.assertNotEqual(first_authentication["access"], second_authentication["access"])
        self.assertNotEqual(first_authentication["refresh"], second_authentication["refresh"])
        authenticated_client = self._get_api_client(second_authentication["access"])

        # Get admin1's profile using the new access token
        response = authenticated_client.get(self.profile)
        self.assertEqual(200, response.status_code)
        content = self._get_content(response.content)
        self.assertEqual(self.admin1.id, content.get("id"))
        self.assertEqual(self.admin1.username, content.get("username"))

        # Logout
        self.assertEqual(
            200,
            authenticated_client.post(self.logout, {"refresh": second_authentication["refresh"]}).status_code,
        )

        # Try to refresh tokens after logout
        self.assertEqual(
            401,
            authenticated_client.post(self.refresh, data={"refresh": second_authentication["refresh"]}).status_code,
        )

    def test_api_authentication(self) -> None:
        # Login as admin1
        response = self._get_api_client().post(
            self.login,
            data={"username": self.admin1.username, "password": self.admin1.username},
        )
        self.assertEqual(200, response.status_code)
        access_client = self._get_api_client(self._get_content(response.content)["access"])

        # Create API token
        response = access_client.post(
            self.api_tokens,
            data={
                "name": "test1",
                "expiration": (timezone.now() + timedelta(seconds=3)).isoformat(),
            },
        )
        self.assertEqual(201, response.status_code)
        api_client = self._get_api_client(token=self._get_content(response.content)["key"])
        time.sleep(3)

        # Try to get admin1's profile using an expired token
        self.assertEqual(401, api_client.get(self.profile).status_code)

        # Create other API token
        response = access_client.post(
            self.api_tokens,
            data={
                "name": "test2",
                "expiration": (datetime.now() + timedelta(days=1)).isoformat() + "Z",
            },
        )
        self.assertEqual(201, response.status_code)
        api_token_content = self._get_content(response.content)
        api_client = self._get_api_client(token=api_token_content["key"])

        # Get admin1's profile
        response = api_client.get(self.profile)
        self.assertEqual(200, response.status_code)
        content = self._get_content(response.content)
        self.assertEqual(self.admin1.id, content.get("id"))
        self.assertEqual(self.admin1.username, content.get("username"))

        # MFA endpoints are not callable by using an API token
        for mfa_endpoint in ["register", "enable", "disable"]:
            self.assertEqual(401, api_client.post(f"{self.mfa_user}{mfa_endpoint}/").status_code)

        # Remove API token
        self.assertEqual(
            204,
            api_client.delete(f"{self.api_tokens}{api_token_content['id']}/").status_code,
        )

        # Try to get admin1's profile using the removed API token
        self.assertEqual(401, api_client.get(self.profile).status_code)

    def test_mfa(self) -> None:
        anonymous_client = self._get_api_client()
        # Login as admin1
        response = anonymous_client.post(
            self.login,
            data={"username": self.admin1.username, "password": self.admin1.username},
        )
        self.assertEqual(200, response.status_code)
        access_client = self._get_api_client(self._get_content(response.content)["access"])

        # Check current profile
        response = access_client.get(self.profile)
        self.assertEqual(200, response.status_code)
        self.assertFalse(self._get_content(response.content).get("mfa"))

        # Before registering MFA, it can't be enabled
        self.assertEqual(
            400,
            access_client.post(f"{self.mfa_user}enable/", data={"mfa": "111111"}).status_code,
        )

        # Register MFA app
        self.assertEqual(200, access_client.post(f"{self.mfa_user}register/").status_code)
        # Invalid MFA
        self.assertEqual(
            401,
            access_client.post(f"{self.mfa_user}enable/", data={"mfa": "1111111"}).status_code,
        )
        # Valid MFA
        self.admin1 = User.objects.get(pk=self.admin1.id)
        mfa_otp = pyotp.TOTP(self.admin1.secret)
        response = access_client.post(f"{self.mfa_user}enable/", data={"mfa": mfa_otp.now()})
        self.assertEqual(200, response.status_code)
        self.assertTrue(self._get_content(response.content).get("mfa"))

        # After enabling MFA, it can't be registered again
        self.assertEqual(400, access_client.post(f"{self.mfa_user}register/").status_code)

        # After enabling MFA, it can't be enabled again
        self.assertEqual(
            400,
            access_client.post(f"{self.mfa_user}enable/", data={"mfa": mfa_otp.now()}).status_code,
        )

        # Login with MFA app
        response = anonymous_client.post(
            self.login,
            data={"username": self.admin1.username, "password": self.admin1.username},
        )
        self.assertEqual(200, response.status_code)
        content = self._get_content(response.content)
        self.assertIsNotNone(content.get("mfa"))
        # Partial authenticated token is not valid to access API
        self.assertEqual(401, self._get_api_client(content.get("mfa")).get(self.profile).status_code)
        # Invalid token
        self.assertEqual(
            401,
            anonymous_client.post(self.mfa_login, data={"token": "invalid JWT", "mfa": mfa_otp.now()}).status_code,
        )
        # Invalid MFA
        self.assertEqual(
            401,
            anonymous_client.post(self.mfa_login, data={"token": content.get("mfa"), "mfa": "1111111"}).status_code,
        )
        # Valid token and MFA
        response = anonymous_client.post(self.mfa_login, data={"token": content.get("mfa"), "mfa": mfa_otp.now()})
        self.assertEqual(200, response.status_code)
        content = self._get_content(response.content)
        self.assertIsNotNone(content.get("access"))
        access_client = self._get_api_client(content.get("access"))
        self.assertEqual(200, access_client.get(self.profile).status_code)

        # Login with email MFA
        response = anonymous_client.post(
            self.login,
            data={"username": self.admin1.username, "password": self.admin1.username},
        )
        self.assertEqual(200, response.status_code)
        content = self._get_content(response.content)
        self.assertIsNotNone(content.get("mfa"))
        # Partial authenticated token is not valid to access API
        self.assertEqual(401, self._get_api_client(content.get("mfa")).get(self.profile).status_code)
        # Request MFA via email
        self.assertEqual(400, anonymous_client.post(f"{self.mfa_login}email/").status_code)
        self.assertEqual(
            204,
            anonymous_client.post(f"{self.mfa_login}email/", data={"token": content.get("mfa")}).status_code,
        )
        plain_otp = User.objects.setup_otp(self.admin1)
        # Invalid token
        self.assertEqual(
            401,
            anonymous_client.post(self.mfa_login, data={"token": "invalid JWT", "mfa": plain_otp}).status_code,
        )
        # Invalid MFA
        self.assertEqual(
            401,
            anonymous_client.post(self.mfa_login, data={"token": content.get("mfa"), "mfa": "1111111"}).status_code,
        )
        # Valid token and MFA
        response = anonymous_client.post(self.mfa_login, data={"token": content.get("mfa"), "mfa": plain_otp})
        self.assertEqual(200, response.status_code)
        content = self._get_content(response.content)
        self.assertIsNotNone(content.get("access"))
        access_client = self._get_api_client(content.get("access"))
        self.assertEqual(200, access_client.get(self.profile).status_code)

        # After login with email MFA, disable MFA
        self.assertEqual(204, access_client.post(f"{self.mfa_login}email/").status_code)
        plain_otp = User.objects.setup_otp(self.admin1)
        # Invalid MFA
        self.assertEqual(
            401,
            access_client.post(f"{self.mfa_user}disable/", data={"mfa": "1111111"}).status_code,
        )
        # Valid MFA
        response = access_client.post(f"{self.mfa_user}disable/", data={"mfa": plain_otp})
        self.assertEqual(200, response.status_code)
        self.assertFalse(self._get_content(response.content).get("mfa"))

        # After disabling MFA, request MFA via email
        self.assertEqual(400, access_client.post(f"{self.mfa_login}email/").status_code)

        # After disabling MFA, it can't be disabled again
        self.assertEqual(
            400,
            access_client.post(f"{self.mfa_user}disable/", data={"mfa": plain_otp}).status_code,
        )

        # After disabling MFA, login again
        response = anonymous_client.post(
            self.login,
            data={"username": self.admin1.username, "password": self.admin1.username},
        )
        self.assertEqual(200, response.status_code)
        response = self._get_api_client(self._get_content(response.content)["access"]).get(self.profile)
        self.assertEqual(200, response.status_code)
        self.assertFalse(self._get_content(response.content).get("mfa"))
