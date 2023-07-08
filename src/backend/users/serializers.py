import logging
from typing import Any, Dict

from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.forms import ValidationError
from django.utils import timezone
from email_notifications.sender import user_telegram_linked_notification
from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.fields import SerializerMethodField
from security.authorization.roles import Role
from telegram_bot import sender as telegram_sender
from telegram_bot.messages.basic import LINKED
from telegram_bot.models import TelegramChat
from users.models import User

logger = logging.getLogger()                                                    # Rekono logger


class UserSerializer(serializers.ModelSerializer):
    '''Serializer to get the users data via API.'''

    # Field that indicates the user role name
    role = SerializerMethodField(method_name='get_role')

    class Meta:
        '''Serializer metadata.'''

        model = User
        fields = (                                                              # Target port fields exposed via API
            'id', 'username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined', 'last_login', 'role'
        )

    def get_role(self, instance: User) -> str:
        '''Get user role name from the user groups.

        Args:
            instance (User): User to get role name

        Returns:
            str: Role name assigned to the user
        '''
        role = instance.groups.first()                                          # Get user group
        return role.name if role else None                                      # Return group name


class SimplyUserSerializer(serializers.ModelSerializer):
    '''Simply serializer to include user main data in other serializers.'''

    class Meta:
        '''Serializer metadata.'''

        model = User
        fields = ('id', 'username')                                             # User fields exposed via API


class InviteUserSerializer(serializers.Serializer):
    '''Serializer to invite a new user via API.'''

    email = serializers.EmailField(required=True)                               # New user email
    role = serializers.ChoiceField(choices=Role.choices, required=True)         # New user role

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        '''Validate the provided data before use it.

        Args:
            attrs (Dict[str, Any]): Provided data

        Raises:
            ValidationError: Raised if provided data is invalid

        Returns:
            Dict[str, Any]: Data after validation process
        '''
        attrs = super().validate(attrs)
        if User.objects.filter(email=attrs['email']):
            raise ValidationError({'email': 'This email already exists'})
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> User:
        '''Create instance from validated data.

        Args:
            validated_data (Dict[str, Any]): Validated data

        Returns:
            User: Created instance
        '''
        return User.objects.create_user(validated_data['email'], Role(validated_data['role']))


class ChangeUserRoleSerializer(serializers.Serializer):
    '''Serializer to change user role via API.'''

    role = serializers.ChoiceField(choices=Role.choices, required=True)         # New role for the user

    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        '''Update instance from validated data.

        Args:
            instance (User): Instance to update
            validated_data (Dict[str, Any]): Validated data

        Returns:
            User: Updated instance
        '''
        return User.objects.change_user_role(instance, Role(validated_data['role']))


class UserProfileSerializer(serializers.ModelSerializer):
    '''Serializer to manage user profile via API.'''

    # Field that indicates the user role name
    role = SerializerMethodField(method_name='get_role')
    # Field that indicates if the user has configured Telegram bot yet or not
    telegram_configured = SerializerMethodField(method_name='get_telegram_configured')

    class Meta:
        '''Serializer metadata.'''

        model = User
        fields = (                                                              # User fields exposed via API
            'id', 'username', 'first_name', 'last_name', 'email', 'date_joined', 'last_login',
            'role', 'telegram_configured', 'notification_scope', 'email_notification', 'telegram_notification'
        )
        # Read only fields
        read_only_fields = ('username', 'email', 'date_joined', 'last_login', 'role', 'telegram_configured')

    def get_role(self, instance: User) -> str:
        '''Get user role name from the user groups.

        Args:
            instance (User): User to get role name

        Returns:
            str: Role name assigned to the user
        '''
        role = instance.groups.first()                                          # Get user group
        return role.name if role else None                                      # Return group name

    def get_telegram_configured(self, instance: User) -> bool:
        '''Check if user has configured Telegam bot yet or not.

        Args:
            instance (User): User to check Telegram bot configuration

        Returns:
            bool: Indicate if Telegram bot has been configured
        '''
        return hasattr(instance, 'telegram_chat') and instance.telegram_chat is not None


class TelegramBotSerializer(serializers.Serializer):
    '''Serializer to configure Telegram Bot via API.'''

    # One Time Password used to link account to the Telegram Bot
    otp = serializers.CharField(max_length=200, required=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        '''Validate the provided data before use it.

        Args:
            attrs (Dict[str, Any]): Provided data

        Raises:
            ValidationError: Raised if provided data is invalid
            AuthenticationFailed: Raised if Telegram OTP is invalid

        Returns:
            Dict[str, Any]: Data after validation process
        '''
        attrs = super().validate(attrs)
        try:
            # Search Telegram chat by otp
            attrs['telegram_chat'] = TelegramChat.objects.get(otp=attrs.get('otp'), otp_expiration__gt=timezone.now())
        except TelegramChat.DoesNotExist:                                       # Invalid otp
            raise AuthenticationFailed('Invalid Telegram OTP', code=status.HTTP_401_UNAUTHORIZED)
        return attrs

    @transaction.atomic()
    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        '''Update instance from validated data.

        Args:
            instance (User): Instance to update
            validated_data (Dict[str, Any]): Validated data

        Returns:
            User: Updated instance
        '''
        validated_data['telegram_chat'].otp = None                              # Set otp to null
        validated_data['telegram_chat'].otp_expiration = None                   # Set otp expiration to null
        validated_data['telegram_chat'].user = instance                         # Link Telegram chat Id to the user
        validated_data['telegram_chat'].save(update_fields=['otp', 'otp_expiration', 'user'])
        user_telegram_linked_notification(instance)                             # Send email notification to the user
        # Send Telegram notification to the user
        telegram_sender.send_message(validated_data['telegram_chat'].chat_id, LINKED)
        logger.info(f'[Security] User {instance.id} has logged in the Telegram bot', extra={'user': instance.id})
        return instance


class UserPasswordSerializer(serializers.Serializer):
    '''Common serializer for all user password operations.'''

    password = serializers.CharField(max_length=150, required=True)             # User password

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        '''Validate the provided data before use it.

        Args:
            attrs (Dict[str, Any]): Provided data

        Raises:
            ValidationError: Raised if provided data is invalid

        Returns:
            Dict[str, Any]: Data after validation process
        '''
        attrs = super().validate(attrs)
        validate_password(attrs.get('password'))                                # Check password policy
        return attrs


class CreateUserSerializer(UserPasswordSerializer):
    '''Serializer to create an user via API after email invitation.'''

    username = serializers.CharField(max_length=150, required=True)             # New user username
    first_name = serializers.CharField(max_length=150, required=True)           # New user first name
    last_name = serializers.CharField(max_length=150, required=True)            # New user last name
    otp = serializers.CharField(max_length=200, required=True)                  # OTP included in the email invitation

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        '''Validate the provided data before use it.

        Args:
            attrs (Dict[str, Any]): Provided data

        Raises:
            ValidationError: Raised if provided data is invalid
             AuthenticationFailed: Raised if OTP is invalid

        Returns:
            Dict[str, Any]: Data after validation process
        '''
        try:
            # Search inactive user by otp and check expiration datetime
            user = User.objects.get(is_active=None, otp=attrs.get('otp'), otp_expiration__gt=timezone.now())
        except User.DoesNotExist:                                               # Invalid otp
            raise AuthenticationFailed('Invalid OTP value', code=status.HTTP_401_UNAUTHORIZED)
        attrs = super().validate(attrs)
        if User.objects.filter(username=attrs['username']):
            raise ValidationError({'username': 'This username already exists'})
        attrs['user'] = user
        return attrs

    @transaction.atomic()
    def create(self, validated_data: Dict[str, Any]) -> User:
        '''Create instance from validated data.

        Args:
            validated_data (Dict[str, Any]): Validated data

        Returns:
            User: Created instance
        '''
        # Get invited user
        validated_data['user'].username = validated_data.get('username')        # Set username
        validated_data['user'].first_name = validated_data.get('first_name')    # Set first name
        validated_data['user'].last_name = validated_data.get('last_name')      # Set last name
        # nosemgrep: python.django.security.audit.unvalidated-password.unvalidated-password
        validated_data['user'].set_password(validated_data.get('password'))     # Set password
        validated_data['user'].is_active = True                                 # Enable user
        validated_data['user'].otp = None                                       # Clear OTP
        validated_data['user'].otp_expiration = None                            # Clear OTP expiration
        validated_data['user'].save(update_fields=[
            'username', 'first_name', 'last_name', 'password', 'is_active', 'otp', 'otp_expiration'
        ])
        logger.info(
            f'[User] User {validated_data["user"].id} has been created',
            extra={'user': validated_data["user"].id}
        )
        return validated_data['user']


class ChangeUserPasswordSerializer(UserPasswordSerializer):
    '''Serializer to change user password via API.'''

    # Original user password to validate his identity
    old_password = serializers.CharField(max_length=150, required=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        '''Validate the provided data before use it.

        Args:
            attrs (Dict[str, Any]): Provided data

        Raises:
            ValidationError: Raised if provided data is invalid
            AuthenticationFailed: Raised if old password is invalid

        Returns:
            Dict[str, Any]: Data after validation process
        '''
        if not self.instance.check_password(attrs.get('old_password')):
            raise AuthenticationFailed('Invalid password', code=status.HTTP_401_UNAUTHORIZED)
        return super().validate(attrs)

    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        '''Update instance from validated data.

        Args:
            instance (User): Instance to update
            validated_data (Dict[str, Any]): Validated data

        Returns:
            User: Updated instance
        '''
        # nosemgrep: python.django.security.audit.unvalidated-password.unvalidated-password
        instance.set_password(validated_data.get('password'))                   # Update password
        instance.save(update_fields=['password'])
        logger.info(f'[Security] User {self.instance.id} changed his password', extra={'user': self.instance.id})
        return instance


class ResetPasswordSerializer(UserPasswordSerializer):
    '''Serializer to reset user password via API.'''

    otp = serializers.CharField(max_length=200, required=True)                  # OTP included in the email message

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        '''Validate the provided data before use it.

        Args:
            attrs (Dict[str, Any]): Provided data

        Raises:
            ValidationError: Raised if provided data is invalid
            AuthenticationFailed: Raised if OTP is invalid

        Returns:
            Dict[str, Any]: Data after validation process
        '''
        try:
            # Search active user by otp and check expiration datetime
            user = User.objects.get(otp=attrs['otp'], otp_expiration__gt=timezone.now())
        except User.DoesNotExist:                                               # Invalid otp
            raise AuthenticationFailed('Invalid OTP value', code=status.HTTP_401_UNAUTHORIZED)
        attrs = super().validate(attrs)
        attrs['user'] = user
        return attrs

    @transaction.atomic()
    def save(self, **kwargs: Any) -> User:
        '''Save changes in instance.

        Returns:
            User: Instance after apply changes
        '''
        # Get user that requested the password reset
        # nosemgrep: python.django.security.audit.unvalidated-password.unvalidated-password
        self.validated_data['user'].set_password(self.validated_data.get('password'))   # Set password
        self.validated_data['user'].otp = None                                  # Clear OTP
        self.validated_data['user'].is_active = True                            # Active user
        self.validated_data['user'].save(update_fields=['password', 'otp', 'is_active'])
        logger.info(
            f'[Security] User {self.validated_data["user"].id} changed his password',
            extra={'user': self.validated_data["user"].id}
        )
        return self.validated_data['user']


class RequestPasswordResetSerializer(serializers.Serializer):
    '''Serializer to request the user password reset via API.'''

    # User email of the user that requests the password reset
    email = serializers.EmailField(max_length=150, required=True)

    @transaction.atomic()
    def save(self, **kwargs: Any) -> User:
        '''Save changes in instance.

        Returns:
            User: Instance after apply changes
        '''
        # Get user that requests the password reset
        user = User.objects.get(email=self.validated_data.get('email'), is_active=True)
        user = User.objects.request_password_reset(user)                        # Request password reset
        return user
