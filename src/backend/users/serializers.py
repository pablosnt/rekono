import logging
from typing import Any, Dict

from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import (
    CharField,
    ChoiceField,
    ModelSerializer,
    Serializer,
)
from security.authorization.roles import Role
from users.models import User

logger = logging.getLogger()  # Rekono logger


class UserSerializer(ModelSerializer):
    """Serializer to get the users data via API."""

    role = SerializerMethodField(method_name="get_role")

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "date_joined",
            "last_login",
            "role",
        )

    def get_role(self, instance: User) -> str:
        """Get user role name from the user groups.

        Args:
            instance (User): User to get role name

        Returns:
            str: Role name assigned to the user
        """
        role = instance.groups.first()
        return role.name if role else None


class SimpleUserSerializer(UserSerializer):
    """Simple serializer to include user main data in other serializers."""

    class Meta:
        model = User
        fields = ("id", "username", "email", "role")


class InviteUserSerializer(ModelSerializer):
    """Serializer to invite a new user via API."""

    role = ChoiceField(choices=Role.choices, required=True, write_only=True)

    class Meta:
        model = User
        fields = ("email", "role")

    def create(self, validated_data: Dict[str, Any]) -> User:
        """Create instance from validated data.

        Args:
            validated_data (Dict[str, Any]): Validated data

        Returns:
            User: Created instance
        """
        return User.objects.invite_user(
            validated_data["email"], Role(validated_data["role"])
        )


class UpdateRoleSerializer(Serializer):
    """Serializer to change user role via API."""

    role = ChoiceField(choices=Role.choices, required=True, write_only=True)

    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        """Update instance from validated data.

        Args:
            instance (User): Instance to update
            validated_data (Dict[str, Any]): Validated data

        Returns:
            User: Updated instance
        """
        return User.objects.assign_role(instance, Role(validated_data["role"]))


class ProfileSerializer(UserSerializer):
    """Serializer to manage user profile via API."""

    # Field that indicates if the user has configured Telegram bot yet or not
    # telegram_configured = SerializerMethodField(method_name="get_telegram_configured")

    # TODO: Telegram link

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "date_joined",
            "last_login",
            "role",
            # "telegram_configured",
            "notification_scope",
            "email_notifications",
            "telegram_notifications",
        )
        # Read only fields
        read_only_fields = (
            "username",
            "email",
            "date_joined",
            "last_login",
            "role",
            # "telegram_configured",
        )

    # def get_telegram_configured(self, instance: User) -> bool:
    #     """Check if user has configured Telegam bot yet or not.

    #     Args:
    #         instance (User): User to check Telegram bot configuration

    #     Returns:
    #         bool: Indicate if Telegram bot has been configured
    #     """
    #     return hasattr(instance, "telegram_chat") and instance.telegram_chat is not None


class PasswordSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ("password",)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        attrs = super().validate(attrs)
        validate_password(attrs.get("password"))
        return attrs


class OTPSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ("otp",)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Search inactive user by otp and check expiration datetime
            user = User.objects.get(
                otp=attrs.get("otp"), otp_expiration__gt=timezone.now()
            )
        except User.DoesNotExist:  # Invalid otp
            raise AuthenticationFailed(
                "Invalid OTP value", code=status.HTTP_401_UNAUTHORIZED
            )
        attrs = super().validate(attrs)
        attrs["user"] = user
        return attrs


class CreateUserSerializer(PasswordSerializer, OTPSerializer):
    """Serializer to create an user via API after email invitation."""

    # username = CharField(max_length=150, required=True)  # New user username
    # first_name = CharField(max_length=150, required=True)  # New user first name
    # last_name = CharField(max_length=150, required=True)  # New user last name
    # otp = CharField(
    #     max_length=200, required=True
    # )  # OTP included in the email invitation

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "password",
            "otp",
        )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the provided data before use it.

        Args:
            attrs (Dict[str, Any]): Provided data

        Raises:
            ValidationError: Raised if provided data is invalid
             AuthenticationFailed: Raised if OTP is invalid

        Returns:
            Dict[str, Any]: Data after validation process
        """
        attrs = super().validate(attrs)
        if attrs["user"].is_active is not None:
            raise AuthenticationFailed(
                "Invalid OTP value", code=status.HTTP_401_UNAUTHORIZED
            )
        return attrs

    @transaction.atomic()
    def create(self, validated_data: Dict[str, Any]) -> User:
        """Create instance from validated data.

        Args:
            validated_data (Dict[str, Any]): Validated data

        Returns:
            User: Created instance
        """
        return User.objects.create_user(
            validated_data.get("user"),
            validated_data.get("username"),
            validated_data.get("first_name"),
            validated_data.get("last_name"),
            validated_data.get("password"),
        )


class UpdatePasswordSerializer(PasswordSerializer):
    """Serializer to change user password via API."""

    old_password = CharField(max_length=150, required=True, write_only=True)

    class Meta:
        model = User
        fields = (
            "password",
            "old_password",
        )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the provided data before use it.

        Args:
            attrs (Dict[str, Any]): Provided data

        Raises:
            ValidationError: Raised if provided data is invalid
            AuthenticationFailed: Raised if old password is invalid

        Returns:
            Dict[str, Any]: Data after validation process
        """
        if not self.instance.check_password(attrs.get("old_password")):
            raise AuthenticationFailed(
                "Invalid password", code=status.HTTP_401_UNAUTHORIZED
            )
        return super().validate(attrs)

    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        """Update instance from validated data.

        Args:
            instance (User): Instance to update
            validated_data (Dict[str, Any]): Validated data

        Returns:
            User: Updated instance
        """
        return User.objects.update_password(instance, validated_data.get("password"))


class ResetPasswordSerializer(PasswordSerializer, OTPSerializer):
    """Serializer to reset user password via API."""

    class Meta:
        model = User
        fields = ("otp", "password")

    @transaction.atomic()
    def save(self, **kwargs: Any) -> User:
        """Save changes in instance.

        Returns:
            User: Instance after apply changes
        """
        return User.objects.reset_password(
            self.validated_data.get("user"), self.validated_data.get("password")
        )


class RequestPasswordResetSerializer(UserSerializer):
    """Serializer to request the user password reset via API."""

    class Meta:
        model = User
        fields = ("email",)

    @transaction.atomic()
    def save(self, **kwargs: Any) -> User:
        """Save changes in instance.

        Returns:
            User: Instance after apply changes
        """
        try:
            # Get user that requests the password reset
            user = User.objects.get(
                email=self.validated_data.get("email"), is_active=True
            )
            user = User.objects.request_password_reset(user)  # Request password reset
            return user
        except User.DoesNotExist:
            return None


# TODO: Telegram link

# class TelegramBotSerializer(Serializer):
#     """Serializer to configure Telegram Bot via API."""

#     # One Time Password used to link account to the Telegram Bot
#     otp = CharField(max_length=200, required=True)

#     def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
#         """Validate the provided data before use it.

#         Args:
#             attrs (Dict[str, Any]): Provided data

#         Raises:
#             ValidationError: Raised if provided data is invalid
#             AuthenticationFailed: Raised if Telegram OTP is invalid

#         Returns:
#             Dict[str, Any]: Data after validation process
#         """
#         attrs = super().validate(attrs)
#         try:
#             # Search Telegram chat by otp
#             attrs["telegram_chat"] = TelegramChat.objects.get(
#                 otp=attrs.get("otp"), otp_expiration__gt=timezone.now()
#             )
#         except TelegramChat.DoesNotExist:  # Invalid otp
#             raise AuthenticationFailed(
#                 "Invalid Telegram OTP", code=status.HTTP_401_UNAUTHORIZED
#             )
#         return attrs

#     @transaction.atomic()
#     def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
#         """Update instance from validated data.

#         Args:
#             instance (User): Instance to update
#             validated_data (Dict[str, Any]): Validated data

#         Returns:
#             User: Updated instance
#         """
#         validated_data["telegram_chat"].otp = None  # Set otp to null
#         validated_data[
#             "telegram_chat"
#         ].otp_expiration = None  # Set otp expiration to null
#         validated_data[
#             "telegram_chat"
#         ].user = instance  # Link Telegram chat Id to the user
#         validated_data["telegram_chat"].save(
#             update_fields=["otp", "otp_expiration", "user"]
#         )
#         user_telegram_linked_notification(
#             instance
#         )  # Send email notification to the user
#         # Send Telegram notification to the user
#         telegram_sender.send_message(validated_data["telegram_chat"].chat_id, LINKED)
#         logger.info(
#             f"[Security] User {instance.id} has logged in the Telegram bot",
#             extra={"user": instance.id},
#         )
#         return instance
