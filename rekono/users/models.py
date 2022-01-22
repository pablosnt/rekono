from typing import Any, cast

from django.contrib.auth.models import AbstractUser, Group, UserManager
from django.db import models
from rest_framework.authtoken.models import Token
from security.authorization.roles import Role
from security.crypto import generate_otp
from users.enums import Notification
from users.mail import send_invitation_to_new_user, send_password_reset
from users.utils import get_token_expiration

# Create your models here.


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
        # 'update_fields' not specified because this function is probably called after User creation
        user.save()
        api_token = Token.objects.create(user=user)                             # Create a new API token for the user
        # 'update_fields' not specified because this function is called after Token creation
        api_token.save()

    def create_user(self, email: str, role: Role) -> Any:
        '''Create a new user.

        Args:
            email (str): New user email
            role (Role): New user role

        Returns:
            Any: Created user
        '''
        # Create new user including an OTP. The user will be inactive while invitation is not accepted
        user = User.objects.create(email=email, otp=generate_otp(), is_active=False)
        self.initialize(user, role)                                             # Initialize user
        send_invitation_to_new_user(user)                                       # Send email invitation to the user
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
        user = super().create_superuser(username, email, password, **extra_fields)      # Create new superuser
        self.initialize(user, cast(Role, Role.ADMIN))                           # Initialize user
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
        user.save(update_fields=['groups'])
        return user

    def enable_user(self, user: Any, role: Role) -> Any:
        '''Enable disabled user, assigning it a new role.

        Args:
            user (Any): User to enable
            role (Role): Role to assign to the user

        Returns:
            Any: Enabled user
        '''
        user.is_active = True                                                   # Enable user
        user.otp = generate_otp()                                               # Generate its OTP
        user.otp_expiration = get_token_expiration()                            # Set OTP expiration
        self.initialize(user, role)                                             # Initialize user
        send_password_reset(user)                                               # Send email to establish its password
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
        user.groups.clear()                                                     # Clear its groups
        # 'update_fields' not specified because can be unknown changes within 'set_unusable_password' method
        user.save()
        try:
            token = Token.objects.get(user=user)                                # Get user API token
            token.delete()                                                      # Delete user API token
        except Token.DoesNotExist:
            pass
        return user

    def request_password_reset(self, user: Any) -> Any:
        '''Request a password reset for an user.

        Args:
            user (Any): User that requests its password reset

        Returns:
            Any: User after request password reset
        '''
        user.otp = generate_otp()                                               # Generate its OTP
        user.otp_expiration = get_token_expiration()                            # Set OTP expiration
        user.save(update_fields=['otp', 'otp_expiration'])
        send_password_reset(user)                                               # Send password reset email
        return user


class User(AbstractUser):
    '''User model.'''

    # Main user data
    username = models.TextField(max_length=150, unique=True, blank=True, null=True)
    first_name = models.TextField(max_length=150, blank=True, null=True)
    last_name = models.TextField(max_length=150, blank=True, null=True)
    email = models.EmailField(max_length=150, unique=True)

    # One Time Password used for invite and enable users, or reset passwords
    otp = models.TextField(max_length=200, unique=True, blank=True, null=True)
    # Expiration date for the OTP
    otp_expiration = models.DateTimeField(default=get_token_expiration, blank=True, null=True)

    notification_scope = models.TextField(                                      # User notification preferences
        max_length=18,
        choices=Notification.choices,
        default=Notification.OWN_EXECUTIONS
    )
    # Indicate if email notifications are enabled
    email_notification = models.BooleanField(default=True)
    # Indicate if Telegram notifications are enabled
    telegram_notification = models.BooleanField(default=False)
    # Telegram chat Id between the Rekono bot and the user. It will be used to send Telegram notifications
    telegram_id = models.IntegerField(blank=True, null=True)

    USERNAME_FIELD = 'username'                                                 # Generic user configuration
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']
    objects = RekonoUserManager()                                               # Model manager

    class Meta:
        '''Model metadata.'''

        ordering = ['-id']                                                      # Default ordering for pagination

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return self.email

    def get_project(self) -> Any:
        '''Get the related project for the instance. This will be used for authorization purposes.

        Returns:
            Any: Related project entity
        '''
        return None
