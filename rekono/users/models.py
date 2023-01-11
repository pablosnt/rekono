import logging
from typing import Any, cast

from django.contrib.auth.models import AbstractUser, Group, UserManager
from django.db import models
from email_notifications.sender import (user_enable_account, user_invitation,
                                        user_password_reset)
from rest_framework.authtoken.models import Token
from security.authorization.roles import Role
from security.input_validation import validate_name
from security.otp import generate, get_expiration

from users.enums import Notification

# Create your models here.

logger = logging.getLogger()                                                    # Rekono logger


class RekonoUserManager(UserManager):
    '''Manager for the User model.'''

    def initialize(self, user: Any, role: Role) -> None:
        '''Initialize user, assigning it a role and creating its API token.

        Args:
            user (Any): User to initialize
            role (Role): Role to assign
        '''
        group = Group.objects.get(name=role.value)                              # Get user group related to the role
        user.groups.clear()                                                     # Clean user groups
        user.groups.set([group])                                                # Set user group
        if not Token.objects.filter(user=user).exists():
            Token.objects.create(user=user)                                     # Create a new API token for the user

    def create_user(self, email: str, role: Role) -> Any:
        '''Create a new user.

        Args:
            email (str): New user email
            role (Role): New user role

        Returns:
            Any: Created user
        '''
        # Create new user including an OTP. The user will be inactive while invitation is not accepted
        user = User.objects.create(email=email, otp=generate(), is_active=None)
        self.initialize(user, role)                                             # Initialize user
        user_invitation(user)                                                   # Send email invitation to the user
        logger.info(f'[User] User {user.id} has been invited with role {role}')
        return user

    def create_superuser(self, username: str, email: str, password: str, **extra_fields: Any) -> Any:
        '''Create a new superuser (Admin role, platform administrator and staff).

        Args:
            username (str): New superuser username
            email (str): New superuser email
            password (str): New superuser plain password

        Returns:
            Any: Created superuser
        '''
        extra_fields['is_active'] = True
        user = super().create_superuser(username, email, password, **extra_fields)      # Create new superuser
        self.initialize(user, cast(Role, Role.ADMIN))                           # Initialize user
        logger.info(f'[User] Superuser {user.id} has been created')
        return user

    def change_user_role(self, user: Any, role: Role) -> Any:
        '''Change role for an user.

        Args:
            user (Any): User whose role will be changed
            role (Role): Role to assign to the user

        Returns:
            Any: Updated user
        '''
        group = Group.objects.get(name=role.value)                              # Get user group related to the role
        user.groups.clear()                                                     # Clean user groups
        user.groups.set([group])                                                # Set user group
        logger.info(f'[User] Role for user {user.id} has been changed to {role}')
        return user

    def enable_user(self, user: Any) -> Any:
        '''Enable disabled user, assigning it a new role.

        Args:
            user (Any): User to enable

        Returns:
            Any: Enabled user
        '''
        user.otp = generate()                                                   # Generate its OTP
        user.otp_expiration = get_expiration()                                  # Set OTP expiration
        user.save(update_fields=['otp', 'otp_expiration'])
        if not Token.objects.filter(user=user).exists():
            Token.objects.create(user=user)                                     # Create a new API token for the user
        user_enable_account(user)                                               # Send email to establish its password
        logger.info(f'[User] User {user.id} has been enabled')
        return user

    def disable_user(self, user: Any) -> Any:
        '''Disable user.

        Args:
            user (Any): User to disable

        Returns:
            Any: Disabled user
        '''
        user.is_active = False                                                  # Disable user
        user.set_unusable_password()                                            # Make its password unusable
        user.otp = None                                                         # Remove its OTP
        user.projects.clear()                                                   # Clear its projects
        user.save(update_fields=['otp', 'is_active'])
        try:
            token = Token.objects.get(user=user)                                # Get user API token
            token.delete()                                                      # Delete user API token
        except Token.DoesNotExist:
            pass
        logger.info(f'[User] User {user.id} has been disabled')
        return user

    def request_password_reset(self, user: Any) -> Any:
        '''Request a password reset for an user.

        Args:
            user (Any): User that requests its password reset

        Returns:
            Any: User after request password reset
        '''
        user.otp = generate()                                                   # Generate its OTP
        user.otp_expiration = get_expiration()                                  # Set OTP expiration
        user.save(update_fields=['otp', 'otp_expiration'])
        user_password_reset(user)                                               # Send password reset email
        logger.info(f'[User] User {user.id} requested a password reset', extra={'user': user.id})
        return user


class User(AbstractUser):
    '''User model.'''

    # Main user data
    username = models.TextField(max_length=100, unique=True, blank=True, null=True, validators=[validate_name])
    first_name = models.TextField(max_length=100, blank=True, null=True, validators=[validate_name])
    last_name = models.TextField(max_length=100, blank=True, null=True, validators=[validate_name])
    email = models.EmailField(max_length=150, unique=True)
    is_active = models.BooleanField(null=True, blank=True, default=None)

    # One Time Password used for invite and enable users, or reset passwords
    otp = models.TextField(max_length=200, unique=True, blank=True, null=True)
    # Expiration date for the OTP
    otp_expiration = models.DateTimeField(default=get_expiration, blank=True, null=True)

    notification_scope = models.TextField(                                      # User notification preferences
        max_length=18,
        choices=Notification.choices,
        default=Notification.OWN_EXECUTIONS
    )
    # Indicate if email notifications are enabled
    email_notification = models.BooleanField(default=True)
    # Indicate if Telegram notifications are enabled
    telegram_notification = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'                                                 # Generic user configuration
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']
    objects = RekonoUserManager()                                               # Model manager

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return self.email
