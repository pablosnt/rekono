import os
from typing import Any, Dict

from resources.models import Wordlist
from rest_framework.test import APIClient
from security.file_upload import check_checksum
from testing.test_base import RekonoTestCase
from users.models import User


class WordlistsTest(RekonoTestCase):
    '''Test cases for Wordlist entity from Resources module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        self.endpoint = '/api/resources/wordlists/'                             # Wordlists API endpoint
        # Wordlists paths
        self.resources = os.path.join(self.data_path, 'resources')
        self.passwords = os.path.join(self.resources, 'passwords_wordlist.txt')
        self.endpoints = os.path.join(self.resources, 'endpoints_wordlist.txt')
        self.invalid_size = os.path.join(self.resources, 'invalid_size.txt')
        self.invalid_extension = os.path.join(self.resources, 'invalid_extension.pdf')
        self.invalid_mime_type = os.path.join(self.resources, 'invalid_mime_type.txt')
        # Data for testing
        self.name = 'ZZZ'
        self.fields = ['name', 'type', 'size', 'size', 'creator']               # Fields to check
        self.wordlist = self.create_passwords_wordlist(self.name)               # Create wordlist for testing

    def create_wordlist(self, name: str, path: str, type: str, status_code: int) -> Dict[str, Any]:
        '''Create wordlist and check response.

        Args:
            name (str): Wordlist name
            path (str): Wordlist filepath
            type (str): Wordlist type
            status_code (int): Expected HTTP status code

        Returns:
            Dict[str, Any]: Created wordlist data
        '''
        with open(path, 'rb') as file:
            data = {'name': name, 'type': type, 'file': file}
            if status_code == 201:
                expected = {'name': name, 'type': type, 'size': 3}
                # Create wordlist and check response. Expected successfull request
                return self.api_test(self.rekono.post, self.endpoint, status_code, data, expected, 'multipart')
            else:
                # Try to create wordlist
                return self.api_test(self.rekono.post, self.endpoint, status_code, data, {}, 'multipart')

    def create_passwords_wordlist(self, name: str, status_code: int = 201) -> Dict[str, Any]:
        '''Create wordlist of type Password.

        Args:
            name (str): Wordlist name
            status_code (int, optional): Expected HTTP status code. Defaults to 201.

        Returns:
            Dict[str, Any]: Created wordlist data
        '''
        return self.create_wordlist(name, self.passwords, 'Password', status_code)

    def create_endpoints_wordlist(self, name: str, status_code: int = 201) -> Dict[str, Any]:
        '''Create wordlist of type Endpoint.

        Args:
            name (str): Wordlist name
            status_code (int, optional): Expected HTTP status code. Defaults to 201.

        Returns:
            Dict[str, Any]: Created wordlist data
        '''
        return self.create_wordlist(name, self.endpoints, 'Endpoint', status_code)

    def test_create(self) -> None:
        '''Test wordlist creation feature.'''
        new_wordlist = self.create_endpoints_wordlist(self.name + self.name)    # Create new wordlist
        content = self.api_test(self.rekono.get, f'{self.endpoint}?o=-name', 200)   # Get all wordlists
        # Check that the first one is the new wordlist
        self.check_fields(self.fields, content['results'][0], new_wordlist)
        db_wordlist = Wordlist.objects.get(pk=new_wordlist['id'])
        self.assertTrue(check_checksum(self.endpoints, db_wordlist.checksum))   # Check Wordlist checksum

    def test_invalid_create(self) -> None:
        '''Test wordlist creation feature with invalid data.'''
        self.create_endpoints_wordlist(self.name, 400)                          # Wordlist already exists

    def test_create_with_too_big_file(self) -> None:
        '''Test wordlist creation feature using file with invalid size.'''
        self.create_wordlist('Invalid size', self.invalid_size, 'Password', 400)

    def test_create_with_invalid_extension(self) -> None:
        '''Test wordlist creation feature using file with invalid extension.'''
        self.create_wordlist('Invalid extension', self.invalid_extension, 'Password', 400)

    def test_create_with_invalid_mime_type(self) -> None:
        '''Test wordlist creation feature using file with invalid MIME type.'''
        self.create_wordlist('Invalid MIME type', self.invalid_mime_type, 'Password', 400)

    def test_update(self) -> None:
        '''Test wordlist update feature.'''
        with open(self.endpoints, 'r') as wordlist:
            data = {'name': self.name, 'type': 'Endpoint', 'file': wordlist}
            expected = {'name': data['name'], 'type': data['type'], 'size': 3}
            updated = self.api_test(                                            # Update wordlist
                self.rekono.put, f'{self.endpoint}{self.wordlist["id"]}/', 200,
                data, expected, 'multipart'
            )
        # Check the updated wordlist data
        self.api_test(self.rekono.get, f'{self.endpoint}{self.wordlist["id"]}/', 200, {}, updated)

    def test_invalid_update(self) -> None:
        '''Test wordlist update feature with invalid data.'''
        new_wordlist = self.create_passwords_wordlist(self.name + self.name)    # Create new wordlist
        with open(self.passwords, 'r') as wordlist:
            data = {'name': new_wordlist['name'], 'type': 'Password', 'file': wordlist}
            # Wordlist name already exists
            self.api_test(self.rekono.put, f'{self.endpoint}{self.wordlist["id"]}/', 400, data, {}, 'multipart')

    def test_delete(self) -> None:
        '''Test wordlist deletion feature.'''
        before = self.api_test(self.rekono.get, f'{self.endpoint}?o=-name', 200)                    # Get wordlists
        # Delete testing wordlist
        self.api_test(self.rekono.delete, f'{self.endpoint}{self.wordlist["id"]}/', 204, {})
        self.api_test(self.rekono.get, f'{self.endpoint}?o=-name', 200, {}, {'count': before['count'] - 1})

    def test_unauthorized_delete(self) -> None:
        '''Test wordlist deletion feature without Admin or process creator.'''
        credential = 'other'
        user = User.objects.create_superuser(credential, 'other@other.other', credential)           # Create other user
        data = {'username': credential, 'password': credential}                 # Login data
        content = self.api_test(APIClient().post, self.login, 200, data, {})    # Login request
        unauth = APIClient(HTTP_AUTHORIZATION=f'Bearer {content.get("access")}')            # Configure API client
        data = {'role': 'Auditor'}
        # Change user role to Auditor, because Admins can delete all wordlists
        self.api_test(self.rekono.put, f'/api/users/{user.id}/role/', 200, data, data)
        self.api_test(unauth.delete, f'{self.endpoint}{self.wordlist["id"]}/', 403)         # User is not authorized

    def test_like_dislike(self) -> None:
        '''Test like and dislike features for wordlists.'''
        # Like testing wordlist
        self.api_test(self.rekono.post, f'{self.endpoint}{self.wordlist["id"]}/like/', 201)
        self.api_test(self.rekono.get, f'{self.endpoint}{self.wordlist["id"]}/', 200, {}, {'liked': True, 'likes': 1})
        # Dislike testing wordlist
        self.api_test(self.rekono.post, f'{self.endpoint}{self.wordlist["id"]}/dislike/', 204)
        self.api_test(self.rekono.get, f'{self.endpoint}{self.wordlist["id"]}/', 200, {}, {'liked': False, 'likes': 0})
