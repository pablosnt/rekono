"""Serializers of the users, their profile, and their account operations.

The user data is exposed by three serializers with growing detail, so the email
addresses only reach the roles that manage users. The rest of the serializers
implement the operations over an account: the invitation, the registration, the
password changes, the email verification, and the MFA.
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
    """Serializer with the minimum data needed to reference a user.

    Used by the other models that include their owner, and it's the base of the
    richer user serializers. Email is intentionally excluded to avoid exposing other
    users' addresses to roles that don't need them (phishing and social engineering
    prevention).

    Attributes:
        role: Role of the user, taken from the group they belong to.
    """

    role = SerializerMethodField()

    class Meta:
        """Serializer configuration for the user references."""

        model = User
        fields = ("id", "username", "role")

    def get_role(self, instance: User) -> str:
        """Get the role of the user, which is Reader when they have no group.

        Args:
            instance: User being serialized.

        Returns:
            The name of their role.
        """
        role = instance.groups.first()
        return role.name if role else Role.READER.value


class RestrictedUserSerializer(SimpleUserSerializer):
    """Serializer of a user without their email address.

    Used to list users for non-admin roles, exposing the data needed to
    identify and reference users without leaking their email addresses.
    """

    class Meta:
        """Serializer configuration for the users seen by the non-admin roles."""

        model = User
        fields = SimpleUserSerializer.Meta.fields + (
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
            "last_login",
        )


class UserSerializer(RestrictedUserSerializer):
    """Serializer of a user including their email address.

    Only exposed to the roles that are allowed to manage users, and to the users
    themselves in their own profile.
    """

    class Meta:
        """Serializer configuration for the users seen by the administrators."""

        model = User
        fields = RestrictedUserSerializer.Meta.fields + ("email",)


class InviteUserSerializer(ModelSerializer):
    """Serializer that invites a new user with a given role.

    Attributes:
        role: Role that the invited user will have.
    """

    role = ChoiceField(choices=Role.choices, required=True, write_only=True)

    class Meta:
        """Serializer configuration for the invitations."""

        model = User
        fields = ("email", "role")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Check that the invitation email can be sent.

        Args:
            attrs: Email address and role of the invitation.

        Returns:
            The same validated data, unchanged.

        Raises:
            ValidationError: If SMTP isn't configured, since the invited user would
              never receive the one-time password needed to register.
        """
        attrs = super().validate(attrs)
        if not SMTP().is_available():
            raise ValidationError("SMTP client is not available to send the invitation", code="smtp")
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        """Create the invited account and send its invitation email.

        Args:
            validated_data: Email address and role of the invitation.

        Returns:
            The invited user, who can't log in until they register.
        """
        return User.objects.invite_user(validated_data["email"], Role(validated_data["role"]))


class UpdateRoleSerializer(Serializer):
    """Serializer that changes the role of a user.

    Attributes:
        role: New role of the user.
    """

    role = ChoiceField(choices=Role.choices, required=True, write_only=True)

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        """Assign the new role to the user, replacing the previous one.

        Args:
            instance: User whose role is changed.
            validated_data: New role of the user.

        Returns:
            The user, belonging only to the group of the new role.
        """
        return User.objects.assign_role(instance, Role(validated_data["role"]))


class ProfileSerializer(UserSerializer):
    """Serializer that a user uses to read and update their own profile.

    The email address is writable but changes are not applied directly: a
    verification workflow updates the address only after the user confirms the new
    one, so the pending value is never exposed through the API.
    """

    class Meta:
        """Serializer configuration for the profile of the users."""

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
        """Check that a new email address can be verified.

        Args:
            attrs: Profile fields sent by the user, which may include a new email.

        Returns:
            The same validated data, unchanged.

        Raises:
            ValidationError: If the email changes while SMTP is unavailable, since
              the new address could never be confirmed.
        """
        attrs = super().validate(attrs)
        new_email = attrs.get("email")
        if self.instance and new_email and new_email != self.instance.email and not SMTP().is_available():
            raise ValidationError("SMTP client is not available to verify the new email", code="smtp")
        return attrs

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        """Update the profile, requesting a verification for a new email address.

        The email address is never written directly. When it differs from the current
        one, a verification workflow is started instead and the active email is kept
        until the user confirms the new address.

        Args:
            instance: User whose profile is updated.
            validated_data: Profile fields. The email is removed from it before the
              update runs, so it never reaches the account directly.

        Returns:
            The updated user, whose email address is still the previous one when a
            change was requested.
        """
        new_email = validated_data.pop("email", None)
        if new_email and new_email != instance.email:
            User.objects.request_email_change(instance, new_email)
        return super().update(instance, validated_data)


class PasswordSerializer(UserSerializer):
    """Base serializer of the operations that set a new password."""

    class Meta:
        """Serializer configuration for the passwords."""

        model = User
        fields = ("password",)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Check that the new password satisfies the password policy.

        Args:
            attrs: Validated data including the new password.

        Returns:
            The same validated data, unchanged.

        Raises:
            ValidationError: If the password is rejected by any of the configured
              Django password validators.
        """
        attrs = super().validate(attrs)
        validate_password(attrs.get("password"))
        return attrs


class OTPSerializer(UserSerializer):
    """Base serializer of the operations verified with a one-time password.

    Each subclass declares the scope its OTPs are issued for, so an OTP sent for one
    operation is never accepted by another one.

    Attributes:
        otp_scope: Operation that the received OTP must have been issued for.
    """

    otp_scope = OtpScope.INVITATION

    class Meta:
        """Serializer configuration for the one-time passwords."""

        model = User
        fields = ("otp",)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Get the user that the one-time password belongs to.

        Args:
            attrs: Validated data including the one-time password.

        Returns:
            The validated data with the resolved user added as ``user``, since the
            request only carries the OTP and not the account it belongs to.

        Raises:
            AuthenticationFailed: If the OTP is invalid, expired, or was issued for
              another operation.
        """
        attrs = super().validate(attrs)
        user = User.objects.verify_otp(attrs.get("otp"), self.otp_scope)
        if not user:
            raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        attrs["user"] = user
        return attrs


class VerifyEmailSerializer(OTPSerializer):
    """Serializer that confirms a pending email address change.

    Attributes:
        otp_scope: Only OTPs sent to verify an email address are accepted.
    """

    otp_scope = OtpScope.EMAIL_VERIFICATION

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Check that the user still has an email change waiting for confirmation.

        Args:
            attrs: Validated data including the one-time password.

        Returns:
            The validated data with the resolved user added as ``user``.

        Raises:
            AuthenticationFailed: If the OTP is invalid or the change was already
              applied or discarded.
        """
        attrs = super().validate(attrs)
        if not attrs["user"].pending_email:
            raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        return attrs

    def save(self, **kwargs: Any) -> User:
        """Apply the verified email address change.

        Args:
            **kwargs: Standard serializer arguments, unused because the user comes
              from the validated one-time password.

        Returns:
            The user, whose email address is now the confirmed one.
        """
        return User.objects.update_email(self.validated_data.get("user"))


class CreateUserSerializer(OTPSerializer, PasswordSerializer):
    """Serializer that completes the registration of an invited user.

    Attributes:
        otp_scope: Only OTPs sent with an invitation are accepted.
    """

    otp_scope = OtpScope.INVITATION

    class Meta:
        """Serializer configuration for the registration of the invited users."""

        model = User
        fields = ("username", "first_name", "last_name", "password", "otp")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Check that the account is still waiting for its registration.

        Args:
            attrs: Account details and the one-time password of the invitation.

        Returns:
            The validated data with the resolved user added as ``user``.

        Raises:
            AuthenticationFailed: If the account was already created or disabled.
        """
        attrs = super().validate(attrs)
        if attrs["user"].is_active is not None:
            raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        """Create the account of the invited user, which becomes active.

        Args:
            validated_data: Account details, plus the user that the validate method
              resolves from the one-time password, since the request carries the
              password and not the account that it belongs to.

        Returns:
            The registered user, now active and able to log in.
        """
        return User.objects.create_user(
            validated_data.get("user"),
            validated_data.get("username"),
            validated_data.get("first_name"),
            validated_data.get("last_name"),
            validated_data.get("password"),
        )


class UpdatePasswordSerializer(PasswordSerializer):
    """Serializer that a user uses to change their own password.

    Attributes:
        old_password: Current password, required to prove that the session belongs
          to the owner of the account.
    """

    old_password = CharField(max_length=150, required=True, write_only=True)

    class Meta:
        """Serializer configuration for the password changes."""

        model = User
        fields = ("password", "old_password")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Check the current password before validating the new one.

        Args:
            attrs: Current and new passwords sent by the user.

        Returns:
            The same validated data, unchanged.

        Raises:
            AuthenticationFailed: If the current password isn't correct.
        """
        if not self.instance.check_password(attrs.get("old_password")):
            raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        return super().validate(attrs)

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        """Change the password, warning the user that their sessions are closed.

        Args:
            instance: User whose password is changed.
            validated_data: Current and new passwords, already validated.

        Returns:
            The user, with the new password and no open session left.
        """
        Telegram().logout_after_password_change_message(instance)
        return User.objects.update_password(instance, validated_data.get("password"))


class ResetPasswordSerializer(PasswordSerializer, OTPSerializer):
    """Serializer that sets a new password using a one-time password.

    Attributes:
        otp_scope: Only OTPs sent to reset a password or to enable an account are
          accepted.
    """

    otp_scope = OtpScope.PASSWORD_RESET

    class Meta:
        """Serializer configuration for the password resets."""

        model = User
        fields = ("otp", "password")

    def save(self, **kwargs: Any) -> User:
        """Apply the verified password reset.

        Args:
            **kwargs: Standard serializer arguments, unused because the user comes
              from the validated one-time password.

        Returns:
            The user, with the new password and the one-time password consumed.
        """
        return User.objects.reset_password(self.validated_data.get("user"), self.validated_data.get("password"))


class RequestPasswordResetSerializer(Serializer, LoggingEntity):
    """Serializer that sends the email with the code needed to reset a password.

    Attributes:
        email: Address of the account whose password is being reset.
    """

    email = EmailField(max_length=150, required=True)

    def _save_in_thread(self, email: str) -> None:
        """Send the password reset email, if the address belongs to an active user.

        Args:
            email: Address received in the request, which may belong to nobody.
        """
        user = User.objects.filter(email=email, is_active=True).first()
        if email and user:  # pragma: no cover
            otp = User.objects.setup_otp(user, OtpScope.PASSWORD_RESET)
            SMTP().reset_password(user, otp)
            self.logger.info(f"[User] User {user.id} requested a password reset", extra={"user": user.id})

    def save(self, **kwargs: Any) -> None:
        """Start the password reset in a thread, so the response is always the same.

        Nothing is returned and nothing is awaited, so the response time doesn't
        reveal whether the email address belongs to a Rekono user.

        Args:
            **kwargs: Standard serializer arguments, unused because the address
              comes from the validated data.
        """
        threading.Thread(target=self._save_in_thread, args=(self.validated_data.get("email"),)).start()


class EnableMfaSerializer(MfaSerializer):
    """Serializer that enables the multi-factor authentication of a user.

    Attributes:
        validator: TOTP verification, replacing the fallback to the email OTPs of
          the base serializer. MFA is not enabled yet at this point, so that
          fallback would accept a code without confirming that the authenticator
          app actually works.
    """

    validator = User.objects.verify_mfa

    def save(self, **kwargs: Any) -> User:
        """Enable the multi-factor authentication of the user.

        Args:
            **kwargs: Standard serializer arguments, unused because the user comes
              from the authenticated request.

        Returns:
            The user, who now needs a second factor to log in.
        """
        self.context.get("request").user.mfa = True
        self.context.get("request").user.save(update_fields=["mfa"])
        return self.context.get("request").user


class DisableMfaSerializer(MfaSerializer):
    """Serializer that disables the multi-factor authentication of a user."""

    def save(self, **kwargs: Any) -> User:
        """Disable the multi-factor authentication of the user.

        Args:
            **kwargs: Standard serializer arguments, unused because the user comes
              from the authenticated request.

        Returns:
            The user, who logs in with their password alone from now on.
        """
        self.context.get("request").user.mfa = False
        self.context.get("request").user.save(update_fields=["mfa"])
        return self.context.get("request").user


class RegisterMfaSerializer(Serializer):
    """Serializer of the response returned when the MFA is registered.

    Attributes:
        url: Provisioning URI that the user scans with their authenticator app.
    """

    url = URLField(max_length=200, read_only=True)
