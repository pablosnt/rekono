from typing import Dict

from rest_framework.test import APIClient
from security.otp import generate
from telegram_bot.models import TelegramChat
from testing.api.base import RekonoTestCase
from users.models import User


class UsersTest(RekonoTestCase):
    '''Test cases for Users module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        self.endpoint = '/api/users/'                                           # Users API endpoints
        self.profile = '/api/profile/'
        self.reset_password = '/api/reset-password/'
        self.valid_password = 'VERYcomplexP4$W0RD'                              # Data for testing
        self.invite_data = {'email': 'newrekono@rekono.rekono', 'role': 'Auditor'}
        self.create_data = {
            'username': 'newrekono',
            'password': self.valid_password,
            'first_name': 'new',
            'last_name': 'rekono',
            'otp': 'invalid'
        }
        self.profile_data = {
            'first_name': 'rekono',
            'last_name': 'rekono',
            'notification_scope': 'All executions',
            'email_notification': False
        }
        self.password_data = {'old_password': self.password, 'password': self.valid_password}
        # Create user for testing
        self.user = User.objects.create(username='reader', email='reader@reader.reader', password='reader')

    def invite(self, data: Dict[str, str], status_code: int = 201) -> None:
        '''Invite user and check response.

        Args:
            data (Dict[str, str]): User data
            status_code (int, optional): Expected HTTP status code. Defaults to 201.
        '''
        expected = {'email': data['email'], 'role': data['role'], 'is_active': False}
        if status_code == 201:
            # Invite new user. Expected successfull request
            self.api_test(self.rekono.post, f'{self.endpoint}invite/', status_code, data, expected)
        else:
            self.api_test(self.rekono.post, f'{self.endpoint}invite/', status_code, data)           # Try to invite user

    def test_invite(self) -> None:
        '''Test invitation feature.'''
        self.api_test(self.rekono.get, self.endpoint, 200, {}, {'count': 2})    # Get all users
        self.invite(self.invite_data)                                           # Invite new user
        self.api_test(self.rekono.get, self.endpoint, 200, {}, {'count': 3})    # Get all users. New user found

    def test_invalid_invite(self) -> None:
        '''Test invitation feature with invalid data.'''
        self.invite({'email': self.email, 'role': 'Reader'}, 400)               # Email already exists

    def test_create(self) -> None:
        '''Test creation feature.'''
        self.invite(self.invite_data)                                           # Invite new user
        new_user = User.objects.get(email=self.invite_data['email'])
        self.create_data['otp'] = new_user.otp                                  # Use OTP
        self.api_test(APIClient().post, f'{self.endpoint}create/', 201, self.create_data)           # Create new user
        expected = {
            'email': self.invite_data['email'],
            'role': self.invite_data['role'],
            'username': self.create_data['username'],
            'first_name': self.create_data['first_name'],
            'last_name': self.create_data['last_name'],
            'is_active': True
        }
        self.api_test(self.rekono.get, f'{self.endpoint}{new_user.id}/', 200, {}, expected)         # Check created user
        self.api_test(APIClient().post, f'{self.endpoint}create/', 401, self.create_data)           # Expired OTP
        self.api_test(self.rekono.delete, f'{self.endpoint}{new_user.id}/', 204)    # Disable new user

    def test_invalid_create(self) -> None:
        '''Test creation feature with invalid data.'''
        self.invite(self.invite_data)                                           # Invite new user
        new_user = User.objects.get(email=self.invite_data['email'])
        self.create_data['otp'] = new_user.otp                                  # Use OTP
        self.create_data['username'] = self.username
        self.api_test(APIClient().post, f'{self.endpoint}create/', 400, self.create_data)   # Username already exists
        self.create_data['password'] = 'invalid'
        self.api_test(APIClient().post, f'{self.endpoint}create/', 400, self.create_data)   # Invalid password

    def test_unauthorized_create(self) -> None:
        '''Test creation feature with invalid OTP.'''
        self.api_test(APIClient().post, f'{self.endpoint}create/', 401, self.create_data)   # Invalid OTP

    def test_filter_by_role(self) -> None:
        '''Test filter feature by role.'''
        # Get Admin users
        content = self.api_test(self.rekono.get, f'{self.endpoint}?role=Admin', 200, {}, {'count': 1})
        self.assertEqual(content['results'][0]['username'], self.admin.username)    # Check authenticated user

    def test_filter_by_project(self) -> None:
        '''Test filter feature by project.'''
        data = {'name': 'Test', 'description': 'Test', 'tags': ['test']}
        project = self.api_test(self.rekono.post, '/api/projects/', 201, data, data)                # Create project
        # Get users that belong to created project
        content = self.api_test(self.rekono.get, f'{self.endpoint}?project={project["id"]}&o=-username', 200, {}, {'count': 1})     # noqa: E501
        self.assertEqual(content['results'][0]['username'], self.admin.username)    # Check authenticated user (owner)
        # Get users that don't belong to created project
        content = self.api_test(self.rekono.get, f'{self.endpoint}?project__ne={project["id"]}&o=-username', 200, {}, {'count': 1})     # noqa: E501
        self.assertEqual(content['results'][0]['username'], self.user.username)     # Check testing user

    def test_filter_by_project_not_found(self) -> None:
        '''Test filter feature by not found project.'''
        # Get users that belong to unexisting project: No users
        self.api_test(self.rekono.get, f'{self.endpoint}?project=-1&o=-username', 200, {}, {'count': 0})
        # Get users that don't belong to unexisting project: All users
        self.api_test(self.rekono.get, f'{self.endpoint}?project__ne=-1&o=-username', 200, {}, {'count': 2})

    def test_change_role(self) -> None:
        '''Test change role feature.'''
        data = {'role': 'Auditor'}
        # Change testing user role to Auditor
        self.api_test(self.rekono.put, f'{self.endpoint}{self.user.id}/role/', 200, data, data)
        self.api_test(self.rekono.get, f'{self.endpoint}{self.user.id}/', 200, {}, data)            # Check user role

    def test_invalid_change_role(self) -> None:
        '''Test change role feature with invalid data.'''
        data = {'role': 'Invalid'}
        # Change testing user role to invalid role
        self.api_test(self.rekono.put, f'{self.endpoint}{self.user.id}/role/', 400, data)

    def test_enable_disable(self) -> None:
        '''Test enable and disable features.'''
        self.api_test(self.rekono.delete, f'{self.endpoint}{self.user.id}/', 204)   # Disable testing user
        self.api_test(self.rekono.get, f'{self.endpoint}{self.user.id}/', 200, {}, {'is_active': False})
        # Enable testing user as Admin
        self.api_test(self.rekono.post, f'{self.endpoint}{self.user.id}/enable/', 200, {'role': 'Admin'})
        # Inactive because password should be established
        expected = {'role': 'Admin', 'is_active': False}
        self.api_test(self.rekono.get, f'{self.endpoint}{self.user.id}/', 200, {}, expected)

    def test_invalid_enable(self) -> None:
        '''Test enable feature with invalid data.'''
        # Enable testing user with invalid role
        self.api_test(self.rekono.post, f'{self.endpoint}{self.user.id}/enable/', 400, {'role': 'Invalid'})

    def test_profile(self) -> None:
        '''Test get profile feature.'''
        # Get user profile
        self.api_test(self.rekono.get, self.profile, 200, {}, {'email': self.email, 'username': self.username})

    def test_update_profile(self) -> None:
        '''Test update profile feature.'''
        self.api_test(self.rekono.put, self.profile, 200, self.profile_data, self.profile_data)     # Update profile

    def test_invalid_update_profile(self) -> None:
        '''Test update profile feature with invalid data.'''
        self.profile_data['notification_scope'] = 'Invalid'                     # Invalid notification scope
        self.api_test(self.rekono.put, self.profile, 400, self.profile_data)

    def test_change_password(self) -> None:
        '''Test change password feature.'''
        self.api_test(self.rekono.put, f'{self.profile}change-password/', 200, self.password_data)  # Change password
        data = {'username': self.username, 'password': self.valid_password}
        self.api_test(APIClient().post, self.login, 200, data)               # Test login with new password

    def test_unauthorized_change_password(self) -> None:
        '''Test change password feature with invalid old password.'''
        self.password_data['old_password'] = 'invalid'                          # Invalid old password
        self.api_test(self.rekono.put, f'{self.profile}change-password/', 401, self.password_data)

    def test_invalid_change_password(self) -> None:
        '''Test change password feature with invalid data.'''
        self.password_data['password'] = 'invalid'                              # Invalid new password
        self.api_test(self.rekono.put, f'{self.profile}change-password/', 400, self.password_data)

    def test_reset_password(self) -> None:
        '''Test reset password features.'''
        self.api_test(self.rekono.post, self.reset_password, 200, {'email': self.email})    # Request password reset
        current_user = User.objects.get(email=self.email)
        data = {'otp': current_user.otp, 'password': self.valid_password}       # Use OTP
        self.api_test(self.rekono.put, self.reset_password, 200, data)          # Reset password
        data = {'username': self.username, 'password': data['password']}
        self.api_test(APIClient().post, self.login, 200, data)                  # Test login with new password

    def test_unauthorized_reset_password(self) -> None:
        '''Test reset password feature with invalid OTP.'''
        # Invalid OTP
        self.api_test(self.rekono.put, self.reset_password, 401, {'otp': 'invalid', 'password': self.valid_password})

    def test_invalid_reset_password(self) -> None:
        '''Test reset password feature with invalid data.'''
        self.api_test(self.rekono.post, self.reset_password, 200, {'email': self.email})    # Request password reset
        current_user = User.objects.get(email=self.email)
        data = {'otp': current_user.otp, 'password': 'invalid'}
        self.api_test(self.rekono.put, self.reset_password, 400, data)          # Invalid password

    def test_invalid_reset_password_request(self) -> None:
        '''Test request password reset feature with invalid data.'''
        self.api_test(self.rekono.post, self.reset_password, 400)               # Email is required

    def test_not_found_reset_password_request(self) -> None:
        '''Test request password reset feature with unexisting email.'''
        # Request password reset for unexisting email. Returns 200 to prevent user enumeration vulnerabilities
        self.api_test(self.rekono.post, self.reset_password, 200, {'email': 'notfound@notfound.notfound'})

    def test_telegram_bot(self) -> None:
        '''Test Telegram bot feature.'''
        telegram_chat = TelegramChat.objects.create(chat_id=1, user=self.admin, otp=generate())
        # Link account to Telegram bot
        self.api_test(self.rekono.post, f'{self.profile}telegram-token/', 200, {'otp': telegram_chat.otp})

    def test_invalid_telegram_bot(self) -> None:
        '''Test Telegram bot feature with invalid data.'''
        self.api_test(self.rekono.post, f'{self.profile}telegram-token/', 400)  # OTP is required

    def test_unauthorized_telegram_bot(self) -> None:
        '''Test Telegram bot feature with invalid OTP.'''
        self.api_test(self.rekono.post, f'{self.profile}telegram-token/', 401, {'otp': 'invalid'})  # Invalid OTP
