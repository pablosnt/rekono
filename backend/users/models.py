"""Model of the Rekono users and the manager that implements their lifecycle.

The manager covers the whole life of an account, from the invitation to the
deactivation, including the one-time passwords used to verify the email addresses
and the TOTP secrets used as second authentication factor.
"""

from datetime import datetime, timedelta
from typing import Any

import pyotp
from django.contrib.auth.models import AbstractUser, Group, UserManager
from django.db import models
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from framework.logging import LoggingEntity
from framework.models import BaseEncrypted
from platforms.email.notifications import SMTP
from rekono.settings import CONFIG
from security.authentication.api import ApiToken
from security.authorization.roles import Role
from security.cryptography import Crypto
from security.validators.input_validator import FutureDatetimeValidator, Regex, Validator
from users.enums import Notification, OtpScope


class OtpManagerMixin:
    """Mixin that manages the one-time passwords sent to the users by email.

    Each one-time password is bound to the operation that it was issued for, so it
    can't be replayed against a different one.
    """

    def generate_otp(self, model: Any = None) -> str:
        """Generate a one-time password that isn't assigned to any other user.

        Args:
            model: Model where the collisions are checked, the users by default.

        Returns:
            The plain one-time password, since only its hash is ever stored.
        """
        otp = Crypto.hash(Crypto.random(3000))
        if (model or User).objects.filter(otp=Crypto.hash(otp)).exists():  # pragma: no cover
            return self.generate_otp(model)
        return otp

    def get_otp_expiration_time(self, time: dict[str, int] = {"hours": CONFIG.otp_expiration_hours}) -> datetime:
        """Get the moment when a one-time password created now will expire.

        Args:
            time: Lifetime of the one-time password, as timedelta arguments.

        Returns:
            The expiration moment, which is what gets stored with the user.
        """
        return timezone.now() + timedelta(**time)

    def setup_otp(self, user: Any, scope: OtpScope, time: dict[str, int] | None = None) -> str:
        """Assign a new one-time password to a user.

        Args:
            user: User that will receive the one-time password.
            scope: Operation that the OTP is issued for. It's the only operation
              that will accept it during verification.
            time: Lifetime of the OTP, or None to use the configured one.

        Returns:
            The plain one-time password to be sent to the user, since only its hash
            is assigned to the user.
        """
        plain_otp = self.generate_otp()
        user.otp = Crypto.hash(plain_otp)
        user.otp_scope = scope
        user.otp_expiration = self.get_otp_expiration_time(time) if time is not None else self.get_otp_expiration_time()
        user.save(update_fields=["otp", "otp_scope", "otp_expiration"])
        return plain_otp

    def remove_otp(self, user: Any) -> Any:
        """Remove the one-time password of a user, so it can't be used anymore.

        Args:
            user: User whose one-time password is cleared.

        Returns:
            The user, without the one-time password and its expiration.
        """
        user.otp = user.otp_scope = user.otp_expiration = None
        user.save(update_fields=["otp", "otp_scope", "otp_expiration"])
        return user

    def verify_otp(self, otp: str, scope: OtpScope, user: Any | None = None) -> Any | None:
        """Get the user that a valid one-time password belongs to.

        Args:
            otp: Plain one-time password to be verified.
            scope: Operation that the OTP must have been issued for.
            user: User that must own the OTP, or None to search all of them, which
              is what the operations performed by anonymous users need.

        Returns:
            The user that owns the OTP, or None if it's expired, was issued for
            another operation, or simply doesn't exist.
        """
        filter = {"otp": Crypto.hash(otp), "otp_scope": scope, "otp_expiration__gt": timezone.now()}
        if user:
            filter["id"] = user.id
        return User.objects.filter(**filter).first()


class MfaManagerMixin:
    """Mixin that manages the TOTP secrets used as second authentication factor."""

    def register_mfa(self, user: Any) -> str:
        """Generate the TOTP secret of a user and save it encrypted.

        Args:
            user: User that is enabling the multi-factor authentication.

        Returns:
            The provisioning URI that the user scans with their authenticator app,
            which is the only time the secret leaves the backend.
        """
        user.secret = pyotp.random_base32()
        user.save(update_fields=["_mfa_key"])
        return pyotp.totp.TOTP(user.secret).provisioning_uri(user.email, issuer_name="Rekono")

    def verify_mfa(self, otp: str, user: Any) -> bool:
        """Check if a code matches the TOTP secret of a user at this moment.

        Args:
            otp: Code provided by the user.
            user: User whose TOTP secret the code is checked against.

        Returns:
            Whether the code is the valid one right now.
        """
        return pyotp.TOTP(user.secret).verify(otp)


class RekonoUserManager(UserManager, LoggingEntity, OtpManagerMixin, MfaManagerMixin):
    """Manager that implements the lifecycle of the Rekono accounts."""

    def assign_role(self, user: Any, role: Role) -> Any:
        """Assign a role to a user, replacing the one they had.

        Args:
            user: User whose role is replaced.
            role: New role of the user.

        Returns:
            The user, belonging only to the group of the new role.
        """
        group = Group.objects.get(name=role.value)
        user.groups.clear()  # Users have exactly one role, so prior group membership must be replaced, not extended
        user.groups.set([group])
        self.logger.info(f"[User] Role {role} has been assigned to user {user.id}")
        return user

    def send_invitation(self, user: Any) -> None:
        """Send the invitation email that lets a user create their account.

        Args:
            user: Invited user, who gets a new one-time password bound to the
              invitation scope.
        """
        plain_otp = self.generate_otp()
        user.otp = Crypto.hash(plain_otp)
        user.otp_scope = OtpScope.INVITATION
        user.otp_expiration = self.get_otp_expiration_time()
        user.save(update_fields=["otp", "otp_scope", "otp_expiration"])
        SMTP().invite_user(user, plain_otp)

    def invite_user(self, email: str, role: Role) -> Any:
        """Invite a new user, creating their account in the invited state.

        Args:
            email: Address where the invitation is sent.
            role: Role assigned to the new user.

        Returns:
            The invited user, which can't log in until they complete the
            registration with the one-time password sent by email.
        """
        # is_active=None marks the account as invited but not yet activated
        user = User.objects.create(email=email, is_active=None)
        self.assign_role(user, role)
        self.send_invitation(user)
        self.logger.info(f"[User] User {user.id} has been invited with role {role}")
        return user

    def create_user(self, user: Any, username: str, first_name: str, last_name: str, password: str) -> Any:
        """Complete the registration of an invited user and activate their account.

        Args:
            user: Invited user, already verified with their invitation OTP.
            username: Username chosen by the user.
            first_name: First name of the user.
            last_name: Last name of the user.
            password: Password chosen by the user.

        Returns:
            The registered user, now active and able to log in.
        """
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        # nosemgrep: python.django.security.audit.unvalidated-password.unvalidated-password
        user.set_password(password)
        user.is_active = True
        user.otp = None
        user.otp_scope = None
        user.otp_expiration = None
        user.save(
            update_fields=[
                "username",
                "first_name",
                "last_name",
                "password",
                "is_active",
                "otp",
                "otp_scope",
                "otp_expiration",
            ]
        )
        self.logger.info(f"[User] User {user.id} has been created", extra={"user": user.id})
        return user

    def create_superuser(self, username: str, email: str, password: str, **extra_fields: Any) -> Any:
        """Create an active account with the Admin role, without any invitation.

        It's the entry point of the createsuperuser command, which is how the first
        administrator of a new deployment is created.

        Args:
            username: Username of the new administrator.
            email: Email address of the new administrator.
            password: Password of the new administrator.
            **extra_fields: Extra model fields, whose is_active is always forced to
              True so the account can be used right away.

        Returns:
            The new administrator, active and able to log in.
        """
        extra_fields["is_active"] = True
        user = super().create_superuser(username, email, password, **extra_fields)
        self.assign_role(user, Role.ADMIN)
        self.logger.info(f"[User] Superuser {user.id} has been created")
        return user

    def enable_user(self, user: Any) -> Any:
        """Enable a disabled account and let the user set a new password.

        Args:
            user: Disabled user to be enabled again.

        Returns:
            The enabled user, who still has to set a password before logging in.
        """
        plain_otp = self.generate_otp()
        user.otp = Crypto.hash(plain_otp)
        # The enable account email links to the password reset page, since disabled accounts have an unusable password
        user.otp_scope = OtpScope.PASSWORD_RESET
        user.otp_expiration = self.get_otp_expiration_time()
        user.is_active = True
        user.save(update_fields=["otp", "otp_scope", "otp_expiration", "is_active"])
        SMTP().enable_user_account(user, plain_otp)
        self.logger.info(f"[User] User {user.id} has been enabled")
        return user

    def disable_user(self, user: Any) -> Any:
        """Disable an account and revoke everything that could still authenticate it.

        The password becomes unusable, the MFA secret and the pending OTP are
        removed, the API tokens are deleted, and the user leaves all their projects.

        Args:
            user: User whose account is disabled.

        Returns:
            The disabled user, who can no longer authenticate by any means.
        """
        user.is_active = False
        user.set_unusable_password()
        user.otp = None
        user.otp_scope = None
        user.otp_expiration = None
        user.mfa = False
        user._mfa_key = None
        user.projects.clear()
        user.save(update_fields=["password", "otp", "otp_scope", "otp_expiration", "is_active", "mfa", "_mfa_key"])
        ApiToken.objects.filter(user=user).delete()
        self.logger.info(f"[User] User {user.id} has been disabled")
        return user

    def update_password(self, user: Any, password: str) -> Any:
        """Change the password of a user and close their open sessions.

        The Telegram chat is also disconnected, since it authenticates the user by
        the chat itself and not by their new credentials.

        Args:
            user: User whose password is changed.
            password: New plain password, already validated by the serializers.

        Returns:
            The user, with the new password and no open session left.
        """
        # nosemgrep: python.django.security.audit.unvalidated-password.unvalidated-password
        user.set_password(password)
        user.save(update_fields=["password"])
        self.logger.info(f"[Security] User {user.id} changed his password", extra={"user": user.id})
        if hasattr(user, "telegram_chat"):
            user.telegram_chat.delete()
        self.invalidate_all_tokens(user)
        return user

    def reset_password(self, user: Any, password: str) -> Any:
        """Change the password of a user and consume the one-time password used.

        Args:
            user: User whose password is reset.
            password: New plain password, already validated by the serializers.

        Returns:
            The user, with the new password and the one-time password consumed.
        """
        user = self.update_password(user, password)
        user.otp = None
        user.otp_scope = None
        user.otp_expiration = None
        user.save(update_fields=["otp", "otp_scope", "otp_expiration"])
        return user

    def request_email_change(self, user: Any, new_email: str) -> Any:
        """Start the verification workflow for an email address change.

        The new address is stored in the pending_email field, and the active email
        is only updated once the user confirms it, so an unverified or malicious
        change can never lock the account out. The current address is notified too,
        so the user knows about a change that they didn't request.

        The OTP sent to the new address is bound to the email verification scope, so it
        only confirms the address and can't be replayed to reset the account password or
        to pass the MFA second factor.

        Args:
            user: User that requested the change.
            new_email: Address to verify, which doesn't replace the current one yet.

        Returns:
            The user, with the new address kept as pending until it is confirmed.
        """
        user.pending_email = new_email
        user.save(update_fields=["pending_email"])
        plain_otp = self.setup_otp(user, OtpScope.EMAIL_VERIFICATION)
        SMTP().verify_email(user, plain_otp)
        SMTP().email_change_notification(user)
        self.logger.info(f"[User] User {user.id} requested an email change", extra={"user": user.id})
        return user

    def update_email(self, user: Any) -> Any:
        """Apply a pending email change, once the new address has been verified.

        Args:
            user: User whose pending address has just been confirmed.

        Returns:
            The user, whose email address is now the confirmed one.
        """
        user.email = user.pending_email
        user.pending_email = None
        user.otp = None
        user.otp_scope = None
        user.otp_expiration = None
        user.save(update_fields=["email", "pending_email", "otp", "otp_scope", "otp_expiration"])
        self.logger.info(f"[User] User {user.id} verified its new email address", extra={"user": user.id})
        return user

    def invalidate_all_tokens(self, user: Any) -> Any:
        """Blacklist all the JWT tokens of a user, closing their open sessions.

        Args:
            user: User whose outstanding tokens are blacklisted.

        Returns:
            The user, with none of their previous tokens still valid.
        """
        for token in OutstandingToken.objects.filter(user=user).exclude(
            id__in=BlacklistedToken.objects.filter(token__user=user).values_list("token_id", flat=True)
        ):
            BlacklistedToken.objects.create(token=token)
        return user

    def verify_mfa_or_otp(self, otp: str, user: Any) -> bool:
        """Verify a TOTP code, with an email OTP fallback for MFA-enabled accounts.

        Always checks the code against the user's TOTP secret first. If that
        check fails and the user has MFA enabled, the code is checked again
        as an email OTP, so accounts are not locked out when the
        authenticator app is unavailable. Only OTPs issued for the MFA scope
        are accepted as that fallback, so OTPs sent for other operations, like
        email verification, can't be used as a second factor. Users without MFA
        enabled get no such fallback.

        Args:
            otp: Code provided by the user, either the TOTP one or the one received
              by email.
            user: User that is completing their second authentication factor.

        Returns:
            Whether the code is valid for that user.
        """
        mfa_verification = self.verify_mfa(otp, user)
        if mfa_verification or not user.mfa:
            return mfa_verification
        return self.verify_otp(otp, OtpScope.MFA, user) is not None


class User(AbstractUser, BaseEncrypted):
    """Account of a person that uses Rekono.

    Attributes:
        username: Username chosen during the registration, still empty while the
          user is only invited.
        first_name: First name of the user.
        last_name: Last name of the user.
        email: Email address where the user receives the notifications.
        pending_email: New email address awaiting verification.
        is_active: None while the user is invited, True once their account is
          created, and False when it's disabled.
        otp: Hash of the one-time password currently assigned to the user.
        otp_scope: Operation that the one-time password was issued for.
        otp_expiration: Moment when the one-time password stops being valid.
        mfa: Whether the user enabled the multi-factor authentication.
        notification_scope: Executions that the user wants to be notified about.
        email_notifications: Whether the user receives notifications by email.
        telegram_notifications: Whether the user receives notifications by Telegram.
        USERNAME_FIELD: Field that Django authenticates the users by.
        EMAIL_FIELD: Field that Django sends the account emails to.
        REQUIRED_FIELDS: Fields that the createsuperuser command asks for, besides
          the username and the password.
        objects: Manager that also creates the users and their one-time passwords.
    """

    username = models.TextField(
        max_length=100, unique=True, blank=True, null=True, validators=[Validator(Regex.NAME, code="username")]
    )
    first_name = models.TextField(
        max_length=100, blank=True, null=True, validators=[Validator(Regex.NAME, code="first_name")]
    )
    last_name = models.TextField(
        max_length=100, blank=True, null=True, validators=[Validator(Regex.NAME, code="last_name")]
    )
    email = models.EmailField(max_length=150, unique=True)
    pending_email = models.EmailField(max_length=150, blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True, default=None)

    otp = models.TextField(max_length=200, blank=True, null=True)
    otp_scope = models.IntegerField(choices=OtpScope.choices, blank=True, null=True)
    otp_expiration = models.DateTimeField(
        blank=True, null=True, validators=[FutureDatetimeValidator(code="otp_expiration")]
    )

    _mfa_key = models.TextField(max_length=40, blank=True, null=True, db_column="mfa_key")
    mfa = models.BooleanField(default=False)

    notification_scope = models.TextField(
        max_length=18, choices=Notification.choices, default=Notification.MY_EXECUTIONS
    )
    email_notifications = models.BooleanField(default=True)
    telegram_notifications = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

    objects = RekonoUserManager()
    _encrypted_field = "_mfa_key"

    def __str__(self) -> str:
        """Return the email address of the user."""
        return self.email
