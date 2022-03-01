import logging
from typing import Any, Dict

from email_notifications.sender import user_login_notification
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User

logger = logging.getLogger()                                                    # Rekono logger


class RekonoTokenObtainPairSerializer(TokenObtainPairSerializer):
    '''Serializer to user authentication and access token refresh via API.'''

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        '''Validate the provided data before use it.

        Args:
            attrs (Dict[str, Any]): Provided data

        Raises:
            ValidationError: Raised if provided data is invalid

        Returns:
            Dict[str, Any]: Data after validation process
        '''
        attrs = super().validate(attrs)                                         # User login
        user_login_notification(self.user)                                      # Send email notification to the user
        logger.info(f'[Security] User {self.user.id} has logged in', extra={'user': self.user.id})
        return attrs

    @classmethod
    def get_token(cls, user: User) -> Dict[str, Any]:
        '''Get claims to include in the access token.

        Args:
            user (User): Authenticated user

        Returns:
            Dict[str, Any]: Claims for this user
        '''
        token = super().get_token(user)                                         # Get standard claims
        token['role'] = user.groups.first().name                                # Include user role name
        return token


class LogoutSerializer(serializers.Serializer):
    '''Serializer to user logout via API.'''

    refresh_token = serializers.CharField(max_length=500, required=True)        # Refresh token to logout

    def save(self, **kwargs: Any) -> None:
        '''Perform the logout operation, including the refresh token in the blacklist.'''
        token = RefreshToken(self.validated_data.get('refresh_token'))
        token.blacklist()                                                       # Add refresh token to the blacklist
