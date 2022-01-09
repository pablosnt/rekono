from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class RekonoTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.groups.first().name
        return token


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=500, required=True)

    def save(self, **kwargs):
        token = RefreshToken(self.validated_data.get('refresh_token'))
        token.blacklist()
