import json
from typing import Any, Callable, Dict

from django.http import HttpResponse
from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User


class RekonoTestCase(TestCase):
    '''Base test case.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        self.username = 'rekono'                                                # Username for test authentication
        self.email = 'rekono@rekono.rekono'                                     # Email for test authentication
        self.password = 'rekono'                                                # Password for test authentication
        # Create user for test authentication
        self.admin = User.objects.create_superuser(self.username, self.email, self.password)
        data = {'username': self.username, 'password': self.password}           # Login data
        content = self.api_test(APIClient().post, '/api/token/', 200, data, {})     # Login request
        self.rekono = APIClient(HTTP_AUTHORIZATION=f'Bearer {content.get("access")}')   # Configure Rekono API client
        super().setUp()

    def get_content(self, response: HttpResponse) -> Dict[Any, Any]:
        '''Get content from HTTP response.

        Args:
            response (HttpResponse): HTTP response

        Returns:
            Dict[Any, Any]: Response content
        '''
        return json.loads(response.content.decode('utf-8')) if response.content else {}

    def api_test(
        self,
        request: Callable,
        endpoint: str,
        expected_status: int,
        data: Dict[str, Any] = {},
        expected: Dict[str, Any] = {}
    ) -> Dict[Any, Any]:
        '''Test Rekono API.

        Args:
            request (Callable): Method to make Rekono API request
            endpoint (str): Rekono API endpoint
            expected_status (int): Expected HTTP status code
            data (Dict[str, Any], optional): Request body. Defaults to {}.
            expected (Dict[str, Any], optional): Expected response content. Defaults to {}.

        Returns:
            Dict[Any, Any]: Response content
        '''
        if data:                                                                # HTTP body
            response = request(endpoint, data=data, format='json')              # Make Rekono API request
        else:                                                                   # No HTTP body
            response = request(endpoint)                                        # Make Rekono API request
        self.assertEqual(response.status_code, expected_status)                 # Check HTTP status code
        content = self.get_content(response)                                    # Get content from HTTP response
        if expected:                                                            # Expected response content
            for field, value in expected.items():                               # For each expected data
                self.assertEqual(content[field], value)                         # Check expected value for field
        return content
