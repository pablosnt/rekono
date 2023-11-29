import time
from datetime import datetime, timedelta
from typing import Any, Dict

from django.utils import timezone
from rest_framework.test import APIClient
from tests.framework import RekonoTest


class SecurityTest(RekonoTest):
    refresh = "/api/security/refresh-token/"
    logout = "/api/security/logout/"
    api_tokens = "/api/api-tokens/"

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
        response = authenticated_client.post(
            self.refresh, data={"refresh": "invalid refresh token"}
        )
        self.assertEqual(401, response.status_code)

        # Refresh tokens
        response = authenticated_client.post(
            self.refresh, data={"refresh": first_authentication["refresh"]}
        )
        self.assertEqual(200, response.status_code)
        second_authentication = self._get_content(response.content)
        self.assertNotEqual(
            first_authentication["access"], second_authentication["access"]
        )
        self.assertNotEqual(
            first_authentication["refresh"], second_authentication["refresh"]
        )
        authenticated_client = self._get_api_client(second_authentication["access"])

        # Get admin1's profile using the new access token
        response = authenticated_client.get(self.profile)
        self.assertEqual(200, response.status_code)
        content = self._get_content(response.content)
        self.assertEqual(self.admin1.id, content.get("id"))
        self.assertEqual(self.admin1.username, content.get("username"))

        # Logout
        response = authenticated_client.post(
            self.logout, {"refresh": second_authentication["refresh"]}
        )
        self.assertEqual(200, response.status_code)

        # Try to refresh tokens after logout
        response = authenticated_client.post(
            self.refresh, data={"refresh": second_authentication["refresh"]}
        )
        self.assertEqual(401, response.status_code)

    def test_api_authentication(self) -> None:
        # Login as admin1
        response = self._get_api_client().post(
            self.login,
            data={"username": self.admin1.username, "password": self.admin1.username},
        )
        self.assertEqual(200, response.status_code)
        access_client = self._get_api_client(
            self._get_content(response.content)["access"]
        )

        # Create API token
        response = access_client.post(
            self.api_tokens,
            data={
                "name": "test1",
                "expiration": (timezone.now() + timedelta(seconds=3)).isoformat(),
            },
        )
        self.assertEqual(201, response.status_code)
        content = self._get_content(response.content)
        api_client = self._get_api_client(token=content["key"])
        time.sleep(3)

        # Try to get admin1's profile using an expired token
        response = api_client.get(self.profile)
        self.assertEqual(401, response.status_code)

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

        # Remove API token
        response = api_client.delete(f"{self.api_tokens}{api_token_content['id']}/")
        self.assertEqual(204, response.status_code)

        # Try to get admin1's profile using the removed API token
        response = api_client.get(self.profile)
        self.assertEqual(401, response.status_code)
