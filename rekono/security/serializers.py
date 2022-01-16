from typing import Any, Dict

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User


class RekonoTokenObtainPairSerializer(TokenObtainPairSerializer):
    '''Serializer to user authentication and access token refresh via API.'''

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
