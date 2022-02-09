from rest_framework.test import APIClient
from security.otp import generate
from telegram_bot.models import TelegramChat
from testing.unit.base import RekonoTestCase
from users.models import User


class UsersTest(RekonoTestCase):
    '''Test cases for Users module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        # Create user for testing
        self.user = User.objects.create(username='reader', email='reader@reader.reader', password='reader')

    def test_invite_create(self) -> None:
        '''Test invitation and creation features.'''
        self.api_test(self.rekono.get, '/api/users/', 200, {}, {'count': 2})    # Get all users
        invite = {'email': 'newrekono@rekono.rekono', 'role': 'Auditor'}
        expected = {'email': invite['email'], 'role': invite['role'], 'is_active': False}
        self.api_test(self.rekono.post, '/api/users/invite/', 201, invite, expected)    # Invite new user
        self.api_test(self.rekono.post, '/api/users/invite/', 400, invite)      # Email already exists
        self.api_test(self.rekono.get, '/api/users/', 200, {}, {'count': 3})    # Get all users. New user found
        create = {
            'username': self.username,
            'password': 'newrekono',
            'first_name': 'new',
            'last_name': 'rekono',
            'otp': 'invalid'
        }
        self.api_test(APIClient().post, '/api/users/create/', 401, create)      # Invalid OTP
        new_user = User.objects.get(email=invite['email'])
        create['otp'] = new_user.otp
        self.api_test(APIClient().post, '/api/users/create/', 400, create)      # Invalid password
        create['password'] = 'VERYcomplexP4$W0RD'
        self.api_test(APIClient().post, '/api/users/create/', 400, create)      # Username already exists
        create['username'] = 'newrekono'
        self.api_test(APIClient().post, '/api/users/create/', 201, create)      # Create new user
        self.api_test(APIClient().post, '/api/users/create/', 401, create)      # Expired OTP
        self.api_test(self.rekono.delete, f'/api/users/{new_user.id}/', 204)    # Disable new user

    def test_filters(self) -> None:
        '''Test filter feature.'''
        content = self.api_test(self.rekono.get, '/api/users/?role=Admin', 200, {}, {'count': 1})   # Get Admin users
        self.assertEqual(content['results'][0]['username'], self.admin.username)    # Check authenticated user
        data = {'name': 'Test', 'description': 'Test', 'tags': ['test']}
        project = self.api_test(self.rekono.post, '/api/projects/', 201, data, data)      # Create project
        # Get users that belong to created project
        content = self.api_test(self.rekono.get, f'/api/users/?project={project["id"]}&o=-username', 200, {}, {'count': 1})     # noqa: E501
        self.assertEqual(content['results'][0]['username'], self.admin.username)    # Check authenticated user (owner)
        # Get users that belong to unexisting project
        self.api_test(self.rekono.get, '/api/users/?project=-1&o=-username', 200, {}, {'count': 0})
        # Get users that don't belong to created project
        content = self.api_test(self.rekono.get, f'/api/users/?project__ne={project["id"]}&o=-username', 200, {}, {'count': 1})     # noqa: E501
        self.assertEqual(content['results'][0]['username'], self.user.username)     # Check testing user
        # Get users that don't belong to unexisting project
        self.api_test(self.rekono.get, '/api/users/?project__ne=-1&o=-username', 200, {}, {'count': 2})

    def test_change_role(self) -> None:
        '''Test change role feature.'''
        data = {'role': 'Auditor'}
        # Change testing user role to Auditor
        self.api_test(self.rekono.put, f'/api/users/{self.user.id}/role/', 200, data, data)
        self.api_test(self.rekono.get, f'/api/users/{self.user.id}/', 200, {}, data)
        data = {'role': 'Invalid'}
        # Change testing user role to invalid role
        self.api_test(self.rekono.put, f'/api/users/{self.user.id}/role/', 400, data)
        data = {'role': 'Reader'}
        # Change testing user role to Reader
        self.api_test(self.rekono.put, f'/api/users/{self.user.id}/role/', 200, data, data)
        self.api_test(self.rekono.get, f'/api/users/{self.user.id}/', 200, {}, data)

    def test_enable_disable(self) -> None:
        '''Test enable and disable features.'''
        self.api_test(self.rekono.delete, f'/api/users/{self.user.id}/', 204)   # Disable testing user
        self.api_test(self.rekono.get, f'/api/users/{self.user.id}/', 200, {}, {'is_active': False})
        # Enable testing user as Admin
        self.api_test(self.rekono.post, f'/api/users/{self.user.id}/enable/', 200, {'role': 'Admin'})
        self.api_test(self.rekono.get, f'/api/users/{self.user.id}/', 200, {}, {'role': 'Admin'})
        # Enable testing user with invalid role
        self.api_test(self.rekono.post, f'/api/users/{self.user.id}/enable/', 400, {'role': 'Invalid'})
        # Enable testing user as Reader
        self.api_test(self.rekono.post, f'/api/users/{self.user.id}/enable/', 200, {'role': 'Reader'})
        self.api_test(self.rekono.get, f'/api/users/{self.user.id}/', 200, {}, {'role': 'Reader'})

    def test_profile(self) -> None:
        '''Test profile features.'''
        expected = {'email': self.email, 'username': self.username}
        self.api_test(self.rekono.get, '/api/profile/', 200, {}, expected)      # Get user profile
        data = {
            'first_name': 'rekono',
            'last_name': 'rekono',
            'notification_scope': 'All executions',
            'email_notification': False
        }
        self.api_test(self.rekono.put, '/api/profile/', 200, data, data)        # Update user profile
        data['notification_scope'] = 'Invalid'
        self.api_test(self.rekono.put, '/api/profile/', 400, data)              # Invalid notification scope

    def test_change_password(self) -> None:
        '''Test change password feature.'''
        data = {'old_password': 'invalid', 'password': 'newrekono'}
        self.api_test(self.rekono.put, '/api/profile/change-password/', 401, data)      # Invalid old password
        data['old_password'] = self.password
        self.api_test(self.rekono.put, '/api/profile/change-password/', 400, data)      # Invalid new password
        data['password'] = 'VERYcomplexP4$W0RD'
        self.api_test(self.rekono.put, '/api/profile/change-password/', 200, data)      # Change password
        data = {'username': self.username, 'password': data['password']}
        self.api_test(APIClient().post, '/api/token/', 200, data)               # Test login with new password
        self.admin.set_password(self.password)                                  # Restore original password
        self.admin.save(update_fields=['password'])

    def test_reset_password(self) -> None:
        '''Test reset password features.'''
        self.api_test(self.rekono.post, '/api/reset-password/', 400)            # Email is required
        # Request password reset for unexisting email. Returns 200 to prevent user enumeration vulnerabilities
        self.api_test(self.rekono.post, '/api/reset-password/', 200, {'email': 'notfound@notfound.notfound'})
        self.api_test(self.rekono.post, '/api/reset-password/', 200, {'email': self.email})     # Request password reset
        data = {'otp': 'invalid', 'password': 'newrekono'}
        self.api_test(self.rekono.put, '/api/reset-password/', 401, data)       # Invalid OTP
        current_user = User.objects.get(email=self.email)
        data['otp'] = current_user.otp
        self.api_test(self.rekono.put, '/api/reset-password/', 400, data)       # Invalid password
        data['password'] = 'VERYcomplexP4$W0RD'
        self.api_test(self.rekono.put, '/api/reset-password/', 200, data)       # Reset password
        data = {'username': self.username, 'password': data['password']}
        self.api_test(APIClient().post, '/api/token/', 200, data)               # Test login with new password
        self.admin.set_password(self.password)                                  # Restore original password
        self.admin.save(update_fields=['password'])

    def test_telegram_bot(self) -> None:
        '''Test Telegram bot feature.'''
        self.api_test(self.rekono.post, '/api/profile/telegram-token/', 400)    # OTP is required
        self.api_test(self.rekono.post, '/api/profile/telegram-token/', 401, {'otp': 'invalid'})    # Invalid OTP
        telegram_chat = TelegramChat.objects.create(chat_id=1, user=self.admin, otp=generate())
        # Link account to Telegram bot
        self.api_test(self.rekono.post, '/api/profile/telegram-token/', 200, {'otp': telegram_chat.otp})
