import logging
from typing import Any, Dict

from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils import timezone
from platforms.telegram_app.notifications.notifications import Telegram
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import (
    CharField,
    ChoiceField,
    EmailField,
    ModelSerializer,
    Serializer,
)
from security.authorization.roles import Role
from security.cryptography.hashing import hash
from users.models import User

logger = logging.getLogger()


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
            "telegram_chat",
            "notification_scope",
            "email_notifications",
            "telegram_notifications",
        )
        read_only_fields = (
            "username",
            "email",
            "date_joined",
            "last_login",
            "role",
            "telegram_chat",
        )


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
                otp=hash(attrs.get("otp")), otp_expiration__gt=timezone.now()
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
        if hasattr(user, "telegram_chat"):
            Telegram().logout_after_password_change_message(user.telegram_chat)
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


class RequestPasswordResetSerializer(Serializer):
    """Serializer to request the user password reset via API."""

    email = EmailField(max_length=150, required=True)

    @transaction.atomic()
    def save(self, **kwargs: Any) -> User:
        """Save changes in instance.

        Returns:
            User: Instance after apply changes
        """
        user = User.objects.filter(
            email=self.validated_data.get("email"), is_active=True
        )
        return (
            User.objects.request_password_reset(user.first()) if user.exists() else None
        )
