"""Models for Telegram Bot integration with encrypted settings and chat management.

Defines data models for Telegram Bot configuration, user chat relationships,
and secure account linking with One-Time Password verification.
"""

from django.db import models
from django.db.models import Q

from framework.models import BaseEncrypted, BaseModel
from rekono.settings import AUTH_USER_MODEL
from security.authorization.roles import Role
from security.validators.input_validator import FutureDatetimeValidator, Regex, Validator


class TelegramSettings(BaseEncrypted):
    """Model for storing encrypted Telegram Bot configuration settings.

    Represents the global Telegram Bot settings including the encrypted API token
    required for bot authentication with the Telegram Bot API. Only one instance
    of this model should exist in the system.

    Attributes:
        _token (TextField): Encrypted Telegram Bot API token (max 200 chars).
                           Stored with database column name 'token'.
        _encrypted_field (str): Field name that contains encrypted data.

    Example:
        Configure Telegram Bot token:

        ```python
        settings = TelegramSettings.objects.create(
            secret="1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        )
        ```
    """

    _token = models.TextField(
        max_length=200, validators=[Validator(Regex.SECRET, code="api_token")], null=True, blank=True, db_column="token"
    )

    _encrypted_field = "_token"


class TelegramChat(BaseModel):
    """Model representing a Telegram chat linked to a Rekono user account.

    Manages the relationship between Telegram chats and Rekono user accounts,
    including secure account linking through One-Time Passwords (OTP) with
    expiration handling and role-based access control.

    Attributes:
        user (OneToOneField): The linked Rekono user account (optional).
        chat_id (IntegerField): Unique Telegram chat identifier.
        creation (DateTimeField): Timestamp when the chat was first created.
        otp (TextField): One-Time Password for account linking (max 200 chars, optional).
        otp_expiration (DateTimeField): OTP expiration timestamp with future validation.

    Example:
        Create a new Telegram chat for account linking:

        ```python
        chat = TelegramChat.objects.create(
            chat_id=123456789,
            otp="ABC123",
            otp_expiration=datetime.now() + timedelta(minutes=10)
        )
        ```
    """

    user = models.OneToOneField(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="telegram_chat",
        blank=True,
        null=True,
    )
    chat_id = models.IntegerField(unique=True)
    creation = models.DateTimeField(auto_now_add=True)
    # One Time Password to link user account
    otp = models.TextField(max_length=200, blank=True, null=True)
    otp_expiration = models.DateTimeField(
        blank=True,
        null=True,
        validators=[FutureDatetimeValidator(code="otp_expiration")],
    )

    def is_auditor(self) -> bool:
        """Check if the linked user has auditor or admin permissions.

        Returns:
            bool: True if the user has AUDITOR or ADMIN role, False otherwise.
                 Returns False if no user is linked to this chat.
        """
        return (
            self.user.groups.filter(Q(name=str(Role.AUDITOR)) | Q(name=str(Role.ADMIN))).exists()
            if self.user
            else False
        )

    def __str__(self) -> str:
        """Return string representation of the Telegram chat.

        Returns:
            str: Formatted string with user and chat ID information.
        """
        return f"{self.user.__str__()} - {self.chat_id}"
