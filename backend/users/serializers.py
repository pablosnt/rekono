"""Serializers for user management with validation and security features.

Provides serialization for user models including account creation, profile
management, password operations, and MFA functionality with comprehensive
validation and security controls.
"""

import threading
from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import CharField, ChoiceField, EmailField, ModelSerializer, Serializer, URLField

from framework.logging import LoggingEntity
from platforms.email.notifications import SMTP
from platforms.telegram_app.notifications import Telegram
from security.authentication.serializers import MfaSerializer
from security.authorization.roles import Role
from users.enums import OtpScope
from users.models import User


class SimpleUserSerializer(ModelSerializer):
    """Simplified serializer for User model with minimal fields.

    Provides basic user information for references in other models and acts as
    the base for the richer user serializers. Email is intentionally excluded to
    avoid exposing other users' addresses to roles that don't need them (phishing
    and social engineering prevention).

    Attributes:
        role (SerializerMethodField): Computed role field from user groups
    """

    role = SerializerMethodField()

    class Meta:
        """Meta configuration for the SimpleUserSerializer.

        Attributes:
            model (Model): The User model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = User
        fields = ("id", "username", "role")

    def get_role(self, instance: User) -> str:
        """Get user's role from Django groups.

        Args:
            instance (User): User instance to get role for

        Returns:
            str: Role name or default READER role
        """
        role = instance.groups.first()
        return role.name if role else Role.READER.value


class RestrictedUserSerializer(SimpleUserSerializer):
    """Serializer for User model that hides the email address.

    Used to list users for non-admin roles, exposing the data needed to
    identify and reference users without leaking their email addresses.
    """

    class Meta:
        """Meta configuration for the RestrictedUserSerializer.

        Attributes:
            model (Model): The User model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = User
        fields = SimpleUserSerializer.Meta.fields + (
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
            "last_login",
        )


class UserSerializer(RestrictedUserSerializer):
    """Serializer for User model including the email address.

    Extends the restricted serializer with the email field, which is only
    exposed to roles allowed to manage users (admins and the user themselves).
    """

    class Meta:
        """Meta configuration for the UserSerializer.

        Attributes:
            model (Model): The User model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = User
        fields = RestrictedUserSerializer.Meta.fields + ("email",)


class InviteUserSerializer(ModelSerializer):
    """Serializer for user invitation operations.

    Handles user invitation with role assignment and SMTP validation.

    Attributes:
        role (ChoiceField): Role to assign to invited user
    """

    role = ChoiceField(choices=Role.choices, required=True, write_only=True)

    class Meta:
        """Meta configuration for the InviteUserSerializer.

        Attributes:
            model (Model): The User model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = User
        fields = ("email", "role")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate invitation data including SMTP availability.

        Args:
            attrs (dict[str, Any]): Serializer data to validate

        Returns:
            dict[str, Any]: Validated data

        Raises:
            ValidationError: If SMTP service is unavailable
        """
        attrs = super().validate(attrs)
        if not SMTP().is_available():
            raise ValidationError("SMTP client is not available to send the invitation", code="smtp")
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        """Create invited user account.

        Args:
            validated_data (dict[str, Any]): Validated invitation data

        Returns:
            User: Created user instance pending invitation acceptance
        """
        return User.objects.invite_user(validated_data["email"], Role(validated_data["role"]))


class UpdateRoleSerializer(Serializer):
    """Serializer for updating user role assignments.

    Handles role updates for existing user accounts.

    Attributes:
        role (ChoiceField): New role to assign to user
    """

    role = ChoiceField(choices=Role.choices, required=True, write_only=True)

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        """Update user's role assignment.

        Args:
            instance (User): User instance to update
            validated_data (dict[str, Any]): Validated role data

        Returns:
            User: Updated user instance with new role
        """
        return User.objects.assign_role(instance, Role(validated_data["role"]))


class ProfileSerializer(UserSerializer):
    """Serializer for user profile management.

    Handles user profile data including notification preferences with appropriate
    read-only fields for security. The email address is writable but changes are not
    applied directly: a verification workflow updates the address only after the user
    confirms the new one, so the pending value is never exposed through the API.
    """

    class Meta:
        """Meta configuration for the ProfileSerializer.

        Attributes:
            model (Model): The User model to serialize
            fields (tuple): Field names to include in serialization
            read_only_fields (tuple): Fields that cannot be modified
        """

        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "date_joined",
            "last_login",
            "mfa",
            "role",
            "telegram_chat",
            "notification_scope",
            "email_notifications",
            "telegram_notifications",
        )
        read_only_fields = ("username", "date_joined", "last_login", "mfa", "role", "telegram_chat")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate profile data, requiring SMTP availability for email changes.

        Args:
            attrs (dict[str, Any]): Serializer data to validate

        Returns:
            dict[str, Any]: Validated data

        Raises:
            ValidationError: If the email changes while SMTP is unavailable to verify it
        """
        attrs = super().validate(attrs)
        new_email = attrs.get("email")
        if self.instance and new_email and new_email != self.instance.email and not SMTP().is_available():
            raise ValidationError("SMTP client is not available to verify the new email", code="smtp")
        return attrs

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        """Update profile fields, routing email changes through OTP verification.

        The email address is never written directly. When it differs from the current
        one, a verification workflow is started instead and the active email is kept
        until the user confirms the new address.

        Args:
            instance (User): User instance to update
            validated_data (dict[str, Any]): Validated profile data

        Returns:
            User: Updated user instance
        """
        new_email = validated_data.pop("email", None)
        if new_email and new_email != instance.email:
            User.objects.request_email_change(instance, new_email)
        return super().update(instance, validated_data)


class PasswordSerializer(UserSerializer):
    """Serializer for password operations with validation.

    Provides password validation using Django's password validators.
    """

    class Meta:
        """Meta configuration for the PasswordSerializer.

        Attributes:
            model (Model): The User model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = User
        fields = ("password",)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate password against Django's password policies.

        Args:
            attrs (dict[str, Any]): Serializer data to validate

        Returns:
            dict[str, Any]: Validated data

        Raises:
            ValidationError: If password doesn't meet requirements
        """
        attrs = super().validate(attrs)
        validate_password(attrs.get("password"))
        return attrs


class OTPSerializer(UserSerializer):
    """Serializer for OTP verification operations.

    Handles one-time password verification with user lookup. Each subclass declares the
    scope its OTPs are issued for, so an OTP sent for one operation is never accepted by
    another one.

    Attributes:
        otp_scope (OtpScope): Scope the submitted OTP must have been issued for
    """

    otp_scope = OtpScope.INVITATION

    class Meta:
        """Meta configuration for the OTPSerializer.

        Attributes:
            model (Model): The User model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = User
        fields = ("otp",)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate OTP and retrieve associated user.

        Args:
            attrs (dict[str, Any]): Serializer data to validate

        Returns:
            dict[str, Any]: Validated data with user instance

        Raises:
            AuthenticationFailed: If OTP is invalid, expired or issued for another scope
        """
        attrs = super().validate(attrs)
        user = User.objects.verify_otp(attrs.get("otp"), self.otp_scope)
        if not user:
            raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        attrs["user"] = user
        return attrs


class VerifyEmailSerializer(OTPSerializer):
    """Serializer for confirming a pending email address change.

    Verifies the OTP sent to the new address and ensures the associated user actually
    has a pending email change awaiting confirmation.

    Attributes:
        otp_scope (OtpScope): Only OTPs sent to verify an email address are accepted
    """

    otp_scope = OtpScope.EMAIL_VERIFICATION

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate the OTP and ensure a pending email change exists.

        Args:
            attrs (dict[str, Any]): Serializer data to validate

        Returns:
            dict[str, Any]: Validated data with the associated user

        Raises:
            AuthenticationFailed: If the OTP is invalid or there is no pending email change
        """
        attrs = super().validate(attrs)
        if not attrs["user"].pending_email:
            raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        return attrs

    def save(self, **kwargs: Any) -> User:
        """Apply the verified email address change.

        Returns:
            User: Updated user instance with the new email address applied
        """
        return User.objects.update_email(self.validated_data.get("user"))


class CreateUserSerializer(OTPSerializer, PasswordSerializer):
    """Serializer for user account creation after invitation.

    Combines OTP verification and password validation for secure
    account activation after invitation.

    Attributes:
        otp_scope (OtpScope): Only OTPs sent with an invitation are accepted
    """

    otp_scope = OtpScope.INVITATION

    class Meta:
        """Meta configuration for the CreateUserSerializer.

        Attributes:
            model (Model): The User model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = User
        fields = ("username", "first_name", "last_name", "password", "otp")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate account creation data and user status.

        Args:
            attrs (dict[str, Any]): Serializer data to validate

        Returns:
            dict[str, Any]: Validated data

        Raises:
            AuthenticationFailed: If the account is no longer pending invitation
                (already created or disabled)
        """
        attrs = super().validate(attrs)
        if attrs["user"].is_active is not None:
            raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        """Create active user account from invitation.

        Args:
            validated_data (dict[str, Any]): Validated account creation data

        Returns:
            User: Activated user instance
        """
        return User.objects.create_user(
            validated_data.get("user"),
            validated_data.get("username"),
            validated_data.get("first_name"),
            validated_data.get("last_name"),
            validated_data.get("password"),
        )


class UpdatePasswordSerializer(PasswordSerializer):
    """Serializer for password update operations.

    Handles password changes with old password verification.

    Attributes:
        old_password (CharField): Current password for verification
    """

    old_password = CharField(max_length=150, required=True, write_only=True)

    class Meta:
        """Meta configuration for the UpdatePasswordSerializer.

        Attributes:
            model (Model): The User model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = User
        fields = ("password", "old_password")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate password change with old password check.

        Args:
            attrs (dict[str, Any]): Serializer data to validate

        Returns:
            dict[str, Any]: Validated data

        Raises:
            AuthenticationFailed: If old password is incorrect
        """
        if not self.instance.check_password(attrs.get("old_password")):
            raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        return super().validate(attrs)

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        """Update user password with security cleanup.

        Args:
            instance (User): User instance to update
            validated_data (dict[str, Any]): Validated password data

        Returns:
            User: Updated user instance
        """
        Telegram().logout_after_password_change_message(instance)
        return User.objects.update_password(instance, validated_data.get("password"))


class ResetPasswordSerializer(PasswordSerializer, OTPSerializer):
    """Serializer for password reset operations.

    Combines OTP verification and password validation for secure
    password reset workflow.

    Attributes:
        otp_scope (OtpScope): Only OTPs sent to reset a password or to enable an
            account are accepted
    """

    otp_scope = OtpScope.PASSWORD_RESET

    class Meta:
        """Meta configuration for the ResetPasswordSerializer.

        Attributes:
            model (Model): The User model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = User
        fields = ("otp", "password")

    def save(self, **kwargs: Any) -> User:
        """Apply the verified password reset.

        Returns:
            User: Updated user instance with the new password applied
        """
        return User.objects.reset_password(self.validated_data.get("user"), self.validated_data.get("password"))


class RequestPasswordResetSerializer(Serializer, LoggingEntity):
    """Serializer for password reset requests.

    Handles password reset email sending with user enumeration protection.

    Attributes:
        email (EmailField): Email address for password reset
    """

    email = EmailField(max_length=150, required=True)

    def _save_in_thread(self, email: str) -> None:
        """Send password reset email in background thread.

        Prevents user enumeration by executing database queries and email
        sending in a separate thread with consistent response time.

        Args:
            email (str): Email address to send reset instructions to
        """
        # Even though the reset-password email is sent in another thread, the
        # database query and the OTP setup is executed in a different one to
        # prevent user enumeration by analyzing the Rekono execution time
        # during the password reset request
        user = User.objects.filter(email=email, is_active=True).first()
        if email and user:  # pragma: no cover
            otp = User.objects.setup_otp(user, OtpScope.PASSWORD_RESET)
            SMTP().reset_password(user, otp)
            self.logger.info(f"[User] User {user.id} requested a password reset", extra={"user": user.id})

    def save(self, **kwargs: Any) -> None:
        """Initiate password reset process in background thread.

        Returns:
            None: Always returns None to prevent user enumeration
        """
        threading.Thread(target=self._save_in_thread, args=(self.validated_data.get("email"),)).start()


class EnableMfaSerializer(MfaSerializer):
    """Serializer for enabling MFA on user accounts.

    Extends the base MFA serializer to activate MFA once the submitted code is
    verified. Overrides the default validator to require a TOTP code specifically:
    MFA is not enabled yet at this point, so the base validator would otherwise fall
    back to email OTP instead of confirming that the authenticator app actually works.

    Attributes:
        validator (callable): TOTP-only verification, overriding the base MFA-or-OTP fallback
    """

    validator = User.objects.verify_mfa

    def save(self, **kwargs: Any) -> User:
        """Enable MFA for the current user.

        Returns:
            User: Updated user instance with MFA enabled
        """
        self.context.get("request").user.mfa = True
        self.context.get("request").user.save(update_fields=["mfa"])
        return self.context.get("request").user


class DisableMfaSerializer(MfaSerializer):
    """Serializer for disabling MFA on user accounts.

    Handles MFA disabling with proper verification.
    """

    def save(self, **kwargs: Any) -> User:
        """Disable MFA for the current user.

        Returns:
            User: Updated user instance with MFA disabled
        """
        self.context.get("request").user.mfa = False
        self.context.get("request").user.save(update_fields=["mfa"])
        return self.context.get("request").user


class RegisterMfaSerializer(Serializer):
    """Serializer for MFA registration responses.

    Provides QR code URL for authenticator app setup.

    Attributes:
        url (URLField): QR code provisioning URL for MFA setup
    """

    url = URLField(max_length=200, read_only=True)
