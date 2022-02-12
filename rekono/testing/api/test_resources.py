import os

from testing.api.base import RekonoTestCase


class ResourcesTest(RekonoTestCase):
    '''Test cases for Resources module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        self.passwords = os.path.join(self.current_path, 'data', 'resources', 'passwords.txt')      # Password wordlists
        self.endpoints = os.path.join(self.current_path, 'data', 'resources', 'endpoints.txt')      # Endpoint wordlists
        with open(self.passwords, 'r') as wordlist:
            self.wordlist = self.api_test(                                      # Create wordlist for testing
                self.rekono.post, '/api/resources/wordlists/', 201,
                {'name': 'ZZZ', 'type': 'Password', 'file': wordlist},
                {'name': 'ZZZ', 'type': 'Password', 'size': 3},
                'multipart'
            )

    def test_create_wordlist(self) -> None:
        '''Test wordlist creation feature.'''
        content = self.api_test(self.rekono.get, '/api/resources/wordlists/?o=-name', 200)          # Get all wordlists
        self.check_fields(['name', 'type', 'size', 'size', 'creator'], content['results'][0], self.wordlist)
        with open(self.endpoints, 'r') as wordlist:
            data = {'name': 'ZZZZZZ', 'type': 'Endpoint', 'file': wordlist}
            new_wordlist = self.api_test(                                       # Create new wordlist
                self.rekono.post, '/api/resources/wordlists/', 201,
                data, {'name': 'ZZZZZZ', 'type': 'Endpoint', 'size': 3}, 'multipart'
            )
            # Wordlist name already exists
            self.api_test(self.rekono.post, '/api/resources/wordlists/', 400, data, {}, 'multipart')
        content = self.api_test(self.rekono.get, '/api/resources/wordlists/?o=-name', 200)          # Get all wordlists
        # Check that the first one is the new wordlist
        self.check_fields(['name', 'type', 'size', 'size', 'creator'], content['results'][0], new_wordlist)

    def test_update_wordlist(self) -> None:
        '''Test wordlist update feature.'''
        with open(self.passwords, 'r') as wordlist:
            data = {'name': 'ZZZ updated', 'type': 'Password', 'file': wordlist}
            updated = self.api_test(                                            # Update testing wordlist
                self.rekono.put, f'/api/resources/wordlists/{self.wordlist["id"]}/', 200,
                data, {'name': 'ZZZ updated', 'type': 'Password', 'size': 3}, 'multipart'
            )
            # Wordlist name already exists
            self.api_test(
                self.rekono.put, f'/api/resources/wordlists/{self.wordlist["id"]}/', 400,
                data, {}, 'multipart'
            )
        # Check the updated wordlist data
        self.api_test(self.rekono.get, f'/api/resources/wordlists/{self.wordlist["id"]}/', 200, {}, updated)

    def test_delete_wordlist(self) -> None:
        '''Test wordlist deletion feature.'''
        before = self.api_test(self.rekono.get, '/api/resources/wordlists/?o=-name', 200)           # Get wordlists
        # Delete testing wordlist
        self.api_test(self.rekono.delete, f'/api/resources/wordlists/{self.wordlist["id"]}/', 204, {})
        # Check the wordlist deletion
        self.api_test(self.rekono.get, '/api/resources/wordlists/?o=-name', 200, {}, {'count': before['count'] - 1})

    def test_like_dislike_wordlist(self) -> None:
        '''Test like and dislike features for wordlists.'''
        # Like testing wordlist
        self.api_test(self.rekono.post, f'/api/resources/wordlists/{self.wordlist["id"]}/like/', 201)
        self.api_test(                                                          # Check that the wordlist is liked
            self.rekono.get, f'/api/resources/wordlists/{self.wordlist["id"]}/',
            200, {}, {'liked': True, 'likes': 1}
        )
        # Dislike testing wordlist
        self.api_test(self.rekono.post, f'/api/resources/wordlists/{self.wordlist["id"]}/dislike/', 204)
        self.api_test(                                                          # Check that the wordlist is not liked
            self.rekono.get, f'/api/resources/wordlists/{self.wordlist["id"]}/',
            200, {}, {'liked': False, 'likes': 0}
        )
