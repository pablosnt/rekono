import logging
from datetime import datetime, timedelta
from typing import Any, cast

import pyotp
from django.contrib.auth.models import AbstractUser, Group, UserManager
from django.db import models
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

from framework.models import BaseEncrypted
from platforms.mail.notifications import SMTP
from rekono.settings import CONFIG
from security.authentication.api import ApiToken
from security.authorization.roles import Role
from security.cryptography.hashing import hash
from security.cryptography.random import generate_random_value
from security.validators.input_validator import (
    FutureDatetimeValidator,
    Regex,
    Validator,
)
from users.enums import Notification

# Create your models here.

logger = logging.getLogger()


class RekonoUserManager(UserManager):
    """Manager for the User model."""

    def generate_otp(self, model: Any = None) -> str:
        otp = hash(generate_random_value(3000))
        if (model or User).objects.filter(otp=hash(otp)).exists():  # pragma: no cover
            return self.generate_otp(model)
        return otp

    # pytype: disable=attribute-error
    def get_otp_expiration_time(self, time: dict[str, int] = {"hours": CONFIG.otp_expiration_hours}) -> datetime:
        # pytype: enable=attribute-error
        return timezone.now() + timedelta(**time)

    def assign_role(self, user: Any, role: Role) -> Any:
        """Initialize user, assigning it a role and creating its API token.

        Args:
            user (any): User to initialize
            role (Role): Role to assign
        """
        group = Group.objects.get(name=role.value)  # Get user group related to the role
        user.groups.clear()  # Clean user groups
        user.groups.set([group])  # Set user group
        logger.info(f"[User] Role {role} has been assigned to user {user.id}")
        return user

    def send_invitation(self, user: Any) -> None:
        plain_otp = self.generate_otp()
        user.otp = hash(plain_otp)
        user.otp_expiration = self.get_otp_expiration_time()
        user.save(update_fields=["otp", "otp_expiration"])
        SMTP().invite_user(user, plain_otp)

    def invite_user(self, email: str, role: Role) -> Any:
        """Create a new user.

        Args:
            email (str): New user email
            role (Role): New user role

        Returns:
            Any: Created user
        """
        # Create new user including an OTP. The user will be inactive while invitation is not accepted
        user = User.objects.create(email=email, is_active=None)
        self.assign_role(user, role)
        self.send_invitation(user)
        logger.info(f"[User] User {user.id} has been invited with role {role}")
        return user

    def create_user(self, user: Any, username: str, first_name: str, last_name: str, password: str) -> Any:
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        # nosemgrep: python.django.security.audit.unvalidated-password.unvalidated-password
        user.set_password(password)
        user.is_active = True
        user.otp = None
        user.otp_expiration = None
        user.save(
            update_fields=[
                "username",
                "first_name",
                "last_name",
                "password",
                "is_active",
                "otp",
                "otp_expiration",
            ]
        )
        logger.info(
            f"[User] User {user.id} has been created",
            extra={"user": user.id},
        )
        return user

    def create_superuser(self, username: str, email: str, password: str, **extra_fields: Any) -> Any:
        """Create a new superuser (Admin role, platform administrator and staff).

        Args:
            username (str): New superuser username
            email (str): New superuser email
            password (str): New superuser plain password

        Returns:
            Any: Created superuser
        """
        extra_fields["is_active"] = True
        user = super().create_superuser(username, email, password, **extra_fields)
        self.assign_role(user, cast(Role, Role.ADMIN))
        logger.info(f"[User] Superuser {user.id} has been created")
        return user

    def enable_user(self, user: Any) -> Any:
        """Enable disabled user, assigning it a new role.

        Args:
            user (any): User to enable

        Returns:
            Any: Enabled user
        """
        plain_otp = self.generate_otp()
        user.otp = hash(plain_otp)
        user.otp_expiration = self.get_otp_expiration_time()  # Set OTP expiration
        user.is_active = True
        user.save(update_fields=["otp", "otp_expiration", "is_active"])
        SMTP().enable_user_account(user, plain_otp)
        logger.info(f"[User] User {user.id} has been enabled")
        return user

    def disable_user(self, user: Any) -> Any:
        """Disable user.

        Args:
            user (any): User to disable

        Returns:
            Any: Disabled user
        """
        user.is_active = False  # Disable user
        user.set_unusable_password()  # Make its password unusable
        user.otp = None  # Remove its OTP
        user.otp_expiration = None
        user.projects.clear()  # Clear its projects
        user.save(update_fields=["otp", "otp_expiration", "is_active"])
        ApiToken.objects.filter(user=user).delete()
        logger.info(f"[User] User {user.id} has been disabled")
        return user

    def _update_otp(
        self,
        user: Any,
        otp: str | None = None,
        otp_expiration: datetime | None = None,
    ) -> Any:
        user.otp = otp
        user.otp_expiration = otp_expiration
        user.save(update_fields=["otp", "otp_expiration"])
        return user

    def setup_otp(self, user: Any, time: dict[str, int] | None = None) -> str:
        plain_otp = self.generate_otp()
        user = self._update_otp(
            user,
            hash(plain_otp),
            (self.get_otp_expiration_time(time) if time is not None else self.get_otp_expiration_time()),
        )
        return plain_otp

    def remove_otp(self, user: Any) -> Any:
        return self._update_otp(user)

    def verify_otp(self, otp: str, user: Any | None = None) -> bool:
        filter = {"otp": hash(otp), "otp_expiration__gt": timezone.now()}
        if user:
            filter["id"] = user.id
        return User.objects.filter(**filter).first()

    def update_password(self, user: Any, password: str) -> Any:
        # nosemgrep: python.django.security.audit.unvalidated-password.unvalidated-password
        user.set_password(password)
        user.save(update_fields=["password"])
        logger.info(
            f"[Security] User {user.id} changed his password",
            extra={"user": user.id},
        )
        if hasattr(user, "telegram_chat"):
            user.telegram_chat.delete()
        self.invalidate_all_tokens(user)
        return user

    def reset_password(self, user: Any, password: str) -> Any:
        user = self.update_password(user, password)
        user.otp = None
        user.otp_expiration = None
        user.is_active = True
        user.save(update_fields=["otp", "otp_expiration", "is_active"])
        return user

    def invalidate_all_tokens(self, user: Any) -> Any:
        for token in OutstandingToken.objects.filter(user=user).exclude(
            id__in=BlacklistedToken.objects.filter(token__user=user).values_list("token_id", flat=True)
        ):
            BlacklistedToken.objects.create(token=token)
        return user

    def register_mfa(self, user: Any) -> str:
        user.secret = pyotp.random_base32()
        user.save(update_fields=["_mfa_key"])
        return pyotp.totp.TOTP(user.secret).provisioning_uri(user.email, issuer_name="Rekono")

    def verify_mfa(self, otp: str, user: Any) -> bool:
        return pyotp.TOTP(user.secret).verify(otp)

    def verify_mfa_or_otp(self, otp: str, user: Any) -> bool:
        mfa_verification = self.verify_mfa(otp, user)
        if not mfa_verification and user.mfa:
            return self.verify_otp(otp, user) is not None
        return mfa_verification


class User(AbstractUser, BaseEncrypted):
    """User model."""

    # Main user data
    username = models.TextField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        validators=[Validator(Regex.NAME.value, code="username")],
    )
    first_name = models.TextField(
        max_length=100,
        blank=True,
        null=True,
        validators=[Validator(Regex.NAME.value, code="first_name")],
    )
    last_name = models.TextField(
        max_length=100,
        blank=True,
        null=True,
        validators=[Validator(Regex.NAME.value, code="last_name")],
    )
    email = models.EmailField(max_length=150, unique=True)
    is_active = models.BooleanField(blank=True, null=True, default=None)

    # One Time Password used to invite and enable users or reset passwords and MFA via email
    otp = models.TextField(max_length=200, blank=True, null=True)
    otp_expiration = models.DateTimeField(
        blank=True,
        null=True,
        validators=[FutureDatetimeValidator(code="otp_expiration")],
    )

    _mfa_key = models.TextField(max_length=40, blank=True, null=True, db_column="mfa_key")
    mfa = models.BooleanField(default=False)

    notification_scope = models.TextField(  # User notification preferences
        max_length=18, choices=Notification.choices, default=Notification.MY_EXECUTIONS
    )
    # Indicate if email notifications are enabled
    email_notifications = models.BooleanField(default=True)
    # Indicate if Telegram notifications are enabled
    telegram_notifications = models.BooleanField(default=False)

    USERNAME_FIELD = "username"  # Generic user configuration
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]
    objects = RekonoUserManager()  # Model manager
    _encrypted_field = "_mfa_key"

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return self.email
