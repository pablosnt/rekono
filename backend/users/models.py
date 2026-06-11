"""User models for Rekono's authentication and account management.

Provides comprehensive user account models including custom user manager with
authentication operations, OTP management, MFA support, and role assignment
capabilities for secure user lifecycle management.
"""

from datetime import datetime, timedelta
from typing import Any, cast

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
from users.enums import Notification


class OtpManagerMixin:
    """Mixin providing One-Time Password (OTP) management functionality.

    Provides methods for generating, validating, and managing one-time passwords
    used for secure operations like account invitation, password resets, and
    account activation. Includes collision detection and expiration handling.
    """

    def generate_otp(self, model: Any = None) -> str:
        """Generate a unique OTP with collision detection.

        Creates a cryptographically secure random OTP and ensures uniqueness
        by checking against existing OTPs in the database.

        Args:
            model (Any, optional): Model class to check for collisions. Defaults to User.

        Returns:
            str: A unique OTP string.
        """
        otp = Crypto.hash(Crypto.random(3000))
        if (model or User).objects.filter(otp=Crypto.hash(otp)).exists():  # pragma: no cover
            return self.generate_otp(model)
        return otp

    def get_otp_expiration_time(self, time: dict[str, int] = {"hours": CONFIG.otp_expiration_hours}) -> datetime:
        """Calculate OTP expiration timestamp.

        Determines when an OTP should expire based on the configured
        expiration time or custom time delta.

        Args:
            time (dict[str, int], optional): Time delta parameters.
                Defaults to configured OTP expiration hours.

        Returns:
            datetime: The expiration timestamp.
        """
        return timezone.now() + timedelta(**time)

    def setup_otp(self, user: Any, time: dict[str, int] | None = None) -> str:
        """Set up OTP for a user account.

        Generates a new OTP, hashes it for storage, and sets the expiration
        time on the user account. Used for secure operations requiring
        email verification.

        Args:
            user (Any): User instance to set up OTP for.
            time (dict[str, int] | None, optional): Custom expiration time.
                Defaults to system configuration.

        Returns:
            str: The plain text OTP to send to the user.
        """
        plain_otp = self.generate_otp()
        user.otp = Crypto.hash(plain_otp)
        user.otp_expiration = self.get_otp_expiration_time(time) if time is not None else self.get_otp_expiration_time()
        user.save(update_fields=["otp", "otp_expiration"])
        return plain_otp

    def remove_otp(self, user: Any) -> Any:
        """Remove OTP from user account.

        Clears the OTP and expiration timestamp from the user account,
        effectively invalidating any pending OTP verification.

        Args:
            user (Any): User instance to clear OTP from.

        Returns:
            Any: The updated user instance.
        """
        user.otp = user.otp_expiration = None
        user.save(update_fields=["otp", "otp_expiration"])
        return user

    def verify_otp(self, otp: str, user: Any | None = None) -> Any | None:
        """Verify OTP against stored hash and expiration.

        Validates a plain text OTP by comparing its hash against stored
        values and checking expiration time. Optionally filters by user.

        Args:
            otp (str): Plain text OTP to verify.
            user (Any | None, optional): Specific user to verify against.
                If None, searches all users.

        Returns:
            Any | None: User instance if OTP is valid, None otherwise.
        """
        filter = {"otp": Crypto.hash(otp), "otp_expiration__gt": timezone.now()}
        if user:
            filter["id"] = user.id
        return User.objects.filter(**filter).first()


class MfaManagerMixin:
    """Mixin providing Multi-Factor Authentication (MFA) management functionality.

    Handles TOTP-based multi-factor authentication using authenticator apps.
    Provides secret generation, QR code provisioning URIs, and OTP verification
    for enhanced account security.
    """

    def register_mfa(self, user: Any) -> str:
        """Register MFA for a user account.

        Generates a new MFA secret key and creates a provisioning URI
        for QR code generation. The secret is encrypted before storage.

        Args:
            user (Any): User instance to register MFA for.

        Returns:
            str: Provisioning URI for authenticator app setup.
        """
        user.secret = pyotp.random_base32()
        user.save(update_fields=["_mfa_key"])
        return pyotp.totp.TOTP(user.secret).provisioning_uri(user.email, issuer_name="Rekono")

    def verify_mfa(self, otp: str, user: Any) -> bool:
        """Verify MFA OTP code.

        Validates a time-based OTP code against the user's MFA secret
        using TOTP algorithm with time window validation.

        Args:
            otp (str): Six-digit OTP code from authenticator app.
            user (Any): User instance with registered MFA.

        Returns:
            bool: True if OTP is valid, False otherwise.
        """
        return pyotp.TOTP(user.secret).verify(otp)


class RekonoUserManager(UserManager, LoggingEntity, OtpManagerMixin, MfaManagerMixin):
    """Custom user manager for Rekono with enhanced authentication features.

    Extends Django's UserManager with comprehensive user lifecycle management
    including invitation workflows, role assignment, OTP/MFA operations,
    and security-focused account management.

    Security Features:
        - Secure invitation workflow with email verification
        - Role-based access control with automatic group assignment
        - Password security with validation and token invalidation
        - Account enabling/disabling with cleanup operations
        - Comprehensive audit logging for security events
    """

    def assign_role(self, user: Any, role: Role) -> Any:
        """Assign role to user account.

        Sets the user's role by managing Django group membership.
        Clears existing groups and assigns the new role group.

        Args:
            user (Any): User instance to assign role to.
            role (Role): Role enum value to assign.

        Returns:
            Any: Updated user instance with new role.
        """
        group = Group.objects.get(name=role.value)  # Get user group related to the role
        user.groups.clear()  # Clean user groups
        user.groups.set([group])  # Set user group
        self.logger.info(f"[User] Role {role} has been assigned to user {user.id}")
        return user

    def send_invitation(self, user: Any) -> None:
        """Send invitation email to user.

        Generates OTP and sends invitation email with account creation
        instructions and verification code.

        Args:
            user (Any): User instance to send invitation to.
        """
        plain_otp = self.generate_otp()
        user.otp = Crypto.hash(plain_otp)
        user.otp_expiration = self.get_otp_expiration_time()
        user.save(update_fields=["otp", "otp_expiration"])
        SMTP().invite_user(user, plain_otp)

    def invite_user(self, email: str, role: Role) -> Any:
        """Create and invite new user account.

        Creates inactive user account with specified email and role,
        then sends invitation email for account activation.

        Args:
            email (str): Email address for the new user.
            role (Role): Role to assign to the user.

        Returns:
            Any: Created user instance in inactive state.
        """
        # Create new user including an OTP. The user will be inactive while invitation is not accepted
        user = User.objects.create(email=email, is_active=None)
        self.assign_role(user, role)
        self.send_invitation(user)
        self.logger.info(f"[User] User {user.id} has been invited with role {role}")
        return user

    def create_user(self, user: Any, username: str, first_name: str, last_name: str, password: str) -> Any:
        """Complete user account creation after invitation.

        Activates user account by setting personal information, password,
        and clearing invitation OTP. Called after successful OTP verification.

        Args:
            user (Any): Inactive user instance from invitation.
            username (str): Chosen username for the account.
            first_name (str): User's first name.
            last_name (str): User's last name.
            password (str): Chosen password for the account.

        Returns:
            Any: Activated user instance.
        """
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        # nosemgrep: python.django.security.audit.unvalidated-password.unvalidated-password
        user.set_password(password)
        user.is_active = True
        user.otp = None
        user.otp_expiration = None
        user.save(
            update_fields=["username", "first_name", "last_name", "password", "is_active", "otp", "otp_expiration"]
        )
        self.logger.info(f"[User] User {user.id} has been created", extra={"user": user.id})
        return user

    def create_superuser(self, username: str, email: str, password: str, **extra_fields: Any) -> Any:
        """Create superuser account with admin role.

        Creates active superuser account with admin privileges.
        Used for initial system setup and administrative access.

        Args:
            username (str): Username for the superuser.
            email (str): Email address for the superuser.
            password (str): Password for the superuser.
            **extra_fields (Any): Additional user fields.

        Returns:
            Any: Created superuser instance with admin role.
        """
        extra_fields["is_active"] = True
        user = super().create_superuser(username, email, password, **extra_fields)
        self.assign_role(user, cast(Role, Role.ADMIN))
        self.logger.info(f"[User] Superuser {user.id} has been created")
        return user

    def enable_user(self, user: Any) -> Any:
        """Enable disabled user account.

        Reactivates a disabled user account and sends email notification
        with new OTP for account access.

        Args:
            user (Any): Disabled user instance to enable.

        Returns:
            Any: Enabled user instance.
        """
        plain_otp = self.generate_otp()
        user.otp = Crypto.hash(plain_otp)
        user.otp_expiration = self.get_otp_expiration_time()
        user.is_active = True
        user.save(update_fields=["otp", "otp_expiration", "is_active"])
        SMTP().enable_user_account(user, plain_otp)
        self.logger.info(f"[User] User {user.id} has been enabled")
        return user

    def disable_user(self, user: Any) -> Any:
        """Disable user account and cleanup resources.

        Deactivates user account, makes password unusable, clears OTP,
        disables MFA, removes project memberships, and deletes API tokens for security.

        Args:
            user (Any): User instance to disable.

        Returns:
            Any: Disabled user instance.
        """
        user.is_active = False  # Disable user
        user.set_unusable_password()  # Make its password unusable
        user.otp = None  # Remove its OTP
        user.otp_expiration = None
        user.mfa = False  # Disable MFA
        user._mfa_key = None  # Remove MFA secret key
        user.projects.clear()  # Clear its projects
        user.save(update_fields=["password", "otp", "otp_expiration", "is_active", "mfa", "_mfa_key"])
        ApiToken.objects.filter(user=user).delete()
        self.logger.info(f"[User] User {user.id} has been disabled")
        return user

    def update_password(self, user: Any, password: str) -> Any:
        """Update user password with security cleanup.

        Updates user password and performs security cleanup including
        JWT token invalidation and Telegram chat disconnection.

        Args:
            user (Any): User instance to update password for.
            password (str): New password to set.

        Returns:
            Any: Updated user instance.
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
        """Reset user password after OTP verification.

        Resets password, clears OTP, and activates account. Used for
        password reset workflow after email verification.

        Args:
            user (Any): User instance to reset password for.
            password (str): New password to set.

        Returns:
            Any: Updated user instance with reset password.
        """
        user = self.update_password(user, password)
        user.otp = None
        user.otp_expiration = None
        user.is_active = True
        user.save(update_fields=["otp", "otp_expiration", "is_active"])
        return user

    def invalidate_all_tokens(self, user: Any) -> Any:
        """Invalidate all JWT tokens for user.

        Blacklists all outstanding JWT tokens for the user to force
        re-authentication. Used for security events like password changes.

        Args:
            user (Any): User instance to invalidate tokens for.

        Returns:
            Any: User instance with invalidated tokens.
        """
        for token in OutstandingToken.objects.filter(user=user).exclude(
            id__in=BlacklistedToken.objects.filter(token__user=user).values_list("token_id", flat=True)
        ):
            BlacklistedToken.objects.create(token=token)
        return user

    def verify_mfa_or_otp(self, otp: str, user: Any) -> bool:
        """Verify either MFA or OTP code depending on user settings.

        Performs verification based on user's MFA status. If MFA is enabled,
        verifies against TOTP. Otherwise, verifies against email OTP.

        Args:
            otp (str): OTP code to verify.
            user (Any): User instance to verify against.

        Returns:
            bool: True if verification succeeds, False otherwise.
        """
        mfa_verification = self.verify_mfa(otp, user)
        return self.verify_otp(otp, user) is not None if not mfa_verification and user.mfa else mfa_verification


class User(AbstractUser, BaseEncrypted):
    """Custom user model for Rekono with enhanced security features.

    Extends Django's AbstractUser with comprehensive security and authentication
    features including OTP support, MFA capabilities, notification preferences,
    and encrypted field storage for sensitive data.

    Account States:
        - is_active=None: User invited but account not created
        - is_active=True: Active user account
        - is_active=False: Disabled user account

    Attributes:
        username (TextField): Unique username with validation (optional, max 100 chars)
        first_name (TextField): User's first name (optional, max 100 chars)
        last_name (TextField): User's last name (optional, max 100 chars)
        email (EmailField): Unique email address (required, max 150 chars)
        is_active (BooleanField): Account status (None/True/False for invitation/active/disabled)
        otp (TextField): Hashed one-time password for secure operations (max 200 chars)
        otp_expiration (DateTimeField): OTP expiration timestamp with future validation
        _mfa_key (TextField): Encrypted MFA secret key (stored as 'mfa_key', max 40 chars)
        mfa (BooleanField): Whether MFA is enabled for this account
        notification_scope (TextField): Notification preference level (from Notification enum)
        email_notifications (BooleanField): Whether to send email notifications
        telegram_notifications (BooleanField): Whether to send Telegram notifications

    Example:
        Create a new user invitation:

        ```python
        user = User.objects.invite_user(
            email="user@example.com",
            role=Role.READER
        )
        ```
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
    is_active = models.BooleanField(blank=True, null=True, default=None)

    # One Time Password used to invite and enable users or reset passwords and MFA via email
    otp = models.TextField(max_length=200, blank=True, null=True)
    otp_expiration = models.DateTimeField(
        blank=True, null=True, validators=[FutureDatetimeValidator(code="otp_expiration")]
    )

    # Key for Multi Factor Authetication via authenticator app
    _mfa_key = models.TextField(max_length=40, blank=True, null=True, db_column="mfa_key")
    mfa = models.BooleanField(default=False)

    # User notification preferences
    notification_scope = models.TextField(
        max_length=18, choices=Notification.choices, default=Notification.MY_EXECUTIONS
    )
    email_notifications = models.BooleanField(default=True)
    telegram_notifications = models.BooleanField(default=False)

    # Generic user configuration
    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

    # Custom model manager
    objects = RekonoUserManager()
    _encrypted_field = "_mfa_key"

    @property
    def secret(self) -> str | None:
        """Get decrypted MFA secret.

        Returns:
            str | None: Decrypted MFA secret or None if not set.
        """
        return self._mfa_key

    @secret.setter
    def secret(self, value: str) -> None:
        """Set MFA secret with encryption.

        Args:
            value (str): Plain text MFA secret to encrypt and store.
        """
        self._mfa_key = value

    def __str__(self) -> str:
        """Return string representation of the user.

        Returns:
            str: User's email address.
        """
        return self.email
