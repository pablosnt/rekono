import os
from typing import Any, Dict

from resources.models import Wordlist
from security.file_upload import check_checksum
from testing.api.base import RekonoTestCase


class WordlistsTest(RekonoTestCase):
    '''Test cases for Wordlist entity from Resources module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        self.endpoint = '/api/resources/wordlists/'                             # Wordlists API endpoint
        super().setUp()
        # Wordlists paths
        self.resources = os.path.join(self.data_path, 'resources')
        self.passwords = os.path.join(self.resources, 'passwords_wordlist.txt')
        self.endpoints = os.path.join(self.resources, 'endpoints_wordlist.txt')
        self.invalid_size = os.path.join(self.resources, 'invalid_size.txt')
        self.invalid_extension = os.path.join(self.resources, 'invalid_extension.pdf')
        self.invalid_mime_type = os.path.join(self.resources, 'invalid_mime_type.txt')
        # Data for testing
        self.name = 'ZZZ'
        content = self.create_wordlist(self.name, self.passwords, 'Password')   # Create wordlist for testing
        self.wordlist = Wordlist.objects.get(pk=content["id"])
        self.models = {self.wordlist: self.name}                                # Models to test __str__ method

    def create_wordlist(self, name: str, path: str, type: str, status_code: int = 201) -> Dict[str, Any]:
        '''Create wordlist and check response.

        Args:
            name (str): Wordlist name
            path (str): Wordlist filepath
            type (str): Wordlist type
            status_code (int): Expected HTTP status code. Defaults to 201

        Returns:
            Dict[str, Any]: Created wordlist data
        '''
        with open(path, 'rb') as file:
            data = {'name': name, 'type': type, 'file': file}
            if status_code == 201:
                # Create wordlist and check response. Expected successfull request
                return self.api_test(
                    self.client.post, self.endpoint, status_code,
                    data=data, expected={'name': name, 'type': type, 'size': 3}, format='multipart'
                )
            else:
                # Try to create wordlist
                return self.api_test(self.client.post, self.endpoint, status_code, data=data, format='multipart')

    def test_create(self) -> None:
        '''Test wordlist creation feature.'''
        # Create new wordlist
        new_wordlist = self.create_wordlist(self.name + self.name, self.endpoints, 'Endpoint')
        content = self.api_test(self.client.get, f'{self.endpoint}?o=-name')    # Get all wordlists
        # Check that the first one is the new wordlist
        self.check_fields(['name', 'type', 'size', 'size', 'creator'], content['results'][0], new_wordlist)
        db_wordlist = Wordlist.objects.get(pk=new_wordlist['id'])
        self.assertTrue(check_checksum(self.endpoints, db_wordlist.checksum))   # Check Wordlist checksum

    def test_invalid_create(self) -> None:
        '''Test wordlist creation feature with invalid data.'''
        for name, file in [
            (self.name, self.passwords),                                        # Wordlist already exists
            ('Invalid size', self.invalid_size),                                # Invalid file size
            ('Invalid extension', self.invalid_extension),                      # Invalid file extension
            ('Invalid MIME type', self.invalid_mime_type),                      # Invalid MIME type
        ]:
            self.create_wordlist(name, file, 'Password', 400)

    def test_update(self) -> None:
        '''Test wordlist update feature.'''
        data = {'name': self.name, 'type': 'Endpoint'}
        # Update wordlist
        self.api_test(self.client.put, f'{self.endpoint}{self.wordlist.id}/', 200, data=data, expected=data)

    def test_invalid_update(self) -> None:
        '''Test wordlist update feature with invalid data.'''
        # Create new wordlist
        new_wordlist = self.create_wordlist(self.name + self.name, self.passwords, 'Password')
        with open(self.passwords, 'r') as wordlist:
            data = {'name': new_wordlist['name'], 'type': 'Password', 'file': wordlist}
            # Wordlist name already exists
            self.api_test(self.client.put, f'{self.endpoint}{self.wordlist.id}/', 400, data=data, format='multipart')

    def test_delete(self) -> None:
        '''Test wordlist deletion feature.'''
        before = self.api_test(self.client.get, f'{self.endpoint}?o=-name')     # Get wordlists
        # Delete testing wordlist
        self.api_test(self.client.delete, f'{self.endpoint}{self.wordlist.id}/', 204)
        self.api_test(self.client.get, f'{self.endpoint}?o=-name', expected={'count': before['count'] - 1})

    def test_unauthorized_delete(self) -> None:
        '''Test wordlist deletion feature without Admin or process creator.'''
        # Change user role to Auditor, because Admins can delete all wordlists
        data = {'role': 'Auditor'}
        self.api_test(self.client.put, f'/api/users/{self.other.id}/role/', data=data, expected=data)
        self.api_test(self.other_client.delete, f'{self.endpoint}{self.wordlist.id}/', 403)     # User is not authorized

    def test_like_dislike(self) -> None:
        '''Test like and dislike features for wordlists.'''
        count = self.api_test(self.client.get, f'{self.endpoint}?o=-name')['count']     # Get total count of wordlists
        # Like testing wordlist
        self.api_test(self.client.post, f'{self.endpoint}{self.wordlist.id}/like/', 201)
        self.api_test(self.client.get, f'{self.endpoint}{self.wordlist.id}/', expected={'liked': True, 'likes': 1})
        self.api_test(self.client.get, f'{self.endpoint}?liked=true', expected={'count': 1})
        self.api_test(self.client.get, f'{self.endpoint}?liked=false', expected={'count': count - 1})
        # Dislike testing wordlist
        self.api_test(self.client.post, f'{self.endpoint}{self.wordlist.id}/dislike/', 204)
        self.api_test(self.client.get, f'{self.endpoint}{self.wordlist.id}/', expected={'liked': False, 'likes': 0})
        self.api_test(self.client.get, f'{self.endpoint}?liked=true', expected={'count': 0})
        self.api_test(self.client.get, f'{self.endpoint}?liked=false', expected={'count': count})
