from datetime import datetime

from django.contrib.sites.shortcuts import get_current_site
from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed
from security.authorization.roles import Role
from telegram_bot.models import TelegramChat
from users.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email', 'is_active',
            'date_joined', 'last_login', 'groups', 'notification_preference'
        )
        read_only_fields = ('username', 'email', 'is_active', 'date_joined', 'last_login', 'groups')


class InviteUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    role = serializers.ChoiceField(choices=Role.choices, required=True)

    def create(self, validated_data):
        request = self.context.get('request', None)
        user = User.objects.create_user(
            validated_data.get('email'),
            Role(validated_data.get('role')),
            get_current_site(request).domain
        )
        return user


class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(max_length=150, required=True)
    otp = serializers.CharField(max_length=200, required=True)

    def create(self, validated_data):
        pk = self.context.get('pk', None)
        user = User.objects.get(pk=pk, is_active=False, otp=validated_data.get('otp'))
        user.username = validated_data.get('username')
        user.first_name = validated_data.get('first_name')
        user.last_name = validated_data.get('last_name')
        user.set_password(validated_data.get('password'))
        user.is_active = True
        user.otp = None
        user.save()
        return user


class EnableUserSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=Role.choices, required=True)

    def update(self, instance, validated_data):
        role = Role(validated_data.get('role'))
        request = self.context.get('request', None)
        user = User.objects.enable_user(instance, role, get_current_site(request).domain)
        return user


class ChangeUserRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=Role.choices, required=True)

    def update(self, instance, validated_data):
        role = Role(validated_data.get('role'))
        instance = User.objects.change_user_role(instance, role)
        return instance


class ChangeUserPasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ('password', 'old_password')
        extra_kwargs = {
            'password': {'write_only': True},
            'old_password': {'write_only': True},
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = self.instance
        if not user.check_password(attrs.get('old_password')):
            raise AuthenticationFailed('Invalid password', code=status.HTTP_401_UNAUTHORIZED)
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data.get('password'))
        instance.save()
        return instance


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=150, required=True)

    def save(self, **kwargs):
        user = User.objects.get(email=self.validated_data.get('email'), is_active=True)
        request = self.context.get('request', None)
        user = User.objects.request_password_reset(user, get_current_site(request))
        return user


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    otp = serializers.CharField(max_length=200, required=True)

    def save(self, **kwargs):
        user = User.objects.get(otp=self.validated_data.get('otp'), is_active=True)
        user.set_password(self.validated_data.get('password'))
        user.otp = None
        user.save()
        return user


class TelegramTokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=200, required=True)

    def update(self, instance, validated_data):
        try:
            telegram_chat = TelegramChat.objects.get(
                start_token=self.validated_data.get('token'),
                expiration__gt=datetime.now()
            )
        except TelegramChat.DoesNotExist:
            raise AuthenticationFailed('Invalid Telegram token', code=status.HTTP_401_UNAUTHORIZED)
        if User.objects.filter(telegram_id=telegram_chat.chat_id).exists():
            raise AuthenticationFailed('Invalid Telegram token', code=status.HTTP_401_UNAUTHORIZED)
        instance.telegram_id = telegram_chat.chat_id
        instance.save()
        return instance
