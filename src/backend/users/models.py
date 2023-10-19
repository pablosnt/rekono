import logging
from datetime import datetime, timedelta
from typing import Any, cast

from django.contrib.auth.models import AbstractUser, Group, UserManager
from django.db import models
from django.utils import timezone
from framework.models import BaseModel
from platforms.mail.notifications import SMTP
from rekono.settings import CONFIG
from security.authentication.api import ApiToken
from security.authorization.roles import Role
from security.utils.cryptography import generate_random_value, hash
from security.utils.input_validator import Regex, Validator
from users.enums import Notification

# Create your models here.

logger = logging.getLogger()  # Rekono logger


class RekonoUserManager(UserManager):
    """Manager for the User model."""

    def _generate_otp(self) -> str:
        return hash(generate_random_value(3000))

    def get_otp_expiration_time(self) -> datetime:
        return timezone.now() + timedelta(hours=CONFIG.otp_expiration_hours)

    def assign_role(self, user: Any, role: Role) -> None:
        """Initialize user, assigning it a role and creating its API token.

        Args:
            user (Any): User to initialize
            role (Role): Role to assign
        """
        group = Group.objects.get(name=role.value)  # Get user group related to the role
        user.groups.clear()  # Clean user groups
        user.groups.set([group])  # Set user group
        logger.info(f"[User] Role {role} has been assigned to user {user.id}")
        return user

    def invite_user(self, email: str, role: Role) -> Any:
        """Create a new user.

        Args:
            email (str): New user email
            role (Role): New user role

        Returns:
            Any: Created user
        """
        # Create new user including an OTP. The user will be inactive while invitation is not accepted
        user = User.objects.create(
            email=email,
            otp=self._generate_otp(),
            otp_expiration=self.get_otp_expiration_time(),
            is_active=None,
        )
        self.assign_role(user, role)
        SMTP().invite_user(user)
        logger.info(f"[User] User {user.id} has been invited with role {role}")
        return user

    def create_user(
        self, user: Any, username: str, first_name: str, last_name: str, password: str
    ) -> Any:
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.set_password = password
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

    def create_superuser(
        self, username: str, email: str, password: str, **extra_fields: Any
    ) -> Any:
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
            user (Any): User to enable

        Returns:
            Any: Enabled user
        """
        user.otp = self._generate_otp()  # Generate its OTP
        user.otp_expiration = self.get_otp_expiration_time()  # Set OTP expiration
        user.is_active = True
        user.save(update_fields=["otp", "otp_expiration", "is_active"])
        SMTP().enable_user_account(user)
        logger.info(f"[User] User {user.id} has been enabled")
        return user

    def disable_user(self, user: Any) -> Any:
        """Disable user.

        Args:
            user (Any): User to disable

        Returns:
            Any: Disabled user
        """
        user.is_active = False  # Disable user
        user.set_unusable_password()  # Make its password unusable
        user.otp = None  # Remove its OTP
        user.otp_expiration = None
        user.projects.clear()  # Clear its projects
        user.save(update_fields=["otp", "otp_expiration", "is_active"])
        try:
            ApiToken.objects.filter(user=user).delete()
        except ApiToken.DoesNotExist:
            pass
        logger.info(f"[User] User {user.id} has been disabled")
        return user

    def request_password_reset(self, user: Any) -> Any:
        """Request a password reset for an user.

        Args:
            user (Any): User that requests its password reset

        Returns:
            Any: User after request password reset
        """
        user.otp = self._generate_otp()  # Generate its OTP
        user.otp_expiration = self.get_otp_expiration_time()  # Set OTP expiration
        user.save(update_fields=["otp", "otp_expiration"])
        SMTP().reset_password(user)
        logger.info(
            f"[User] User {user.id} requested a password reset", extra={"user": user.id}
        )
        return user

    def update_password(self, user: Any, password: str) -> Any:
        # nosemgrep: python.django.security.audit.unvalidated-password.unvalidated-password
        user.set_password(password)
        user.save(update_fields=["password"])
        logger.info(
            f"[Security] User {user.id} changed his password",
            extra={"user": user.id},
        )
        return user

    def reset_password(self, user: Any, password: str) -> Any:
        user = self.update_password(user, password)
        user.otp = None
        user.otp_expiration = None
        user.is_active = True
        user.save(update_fields=["otp", "otp_expiration", "is_active"])
        return user


class User(AbstractUser, BaseModel):
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

    # One Time Password used to invite and enable users, or reset passwords
    otp = models.TextField(max_length=200, unique=True, blank=True, null=True)
    otp_expiration = models.DateTimeField(
        blank=True,
        null=True,
    )

    notification_scope = models.TextField(  # User notification preferences
        max_length=18, choices=Notification.choices, default=Notification.OWN_EXECUTIONS
    )
    # Indicate if email notifications are enabled
    email_notifications = models.BooleanField(default=True)
    # Indicate if Telegram notifications are enabled
    telegram_notifications = models.BooleanField(default=False)

    USERNAME_FIELD = "username"  # Generic user configuration
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]
    objects = RekonoUserManager()  # Model manager

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return self.email
