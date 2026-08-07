"""Models of the Telegram configuration and of the linked chats.

Typical usage example:

  settings = TelegramSettings.objects.first()
  settings.secret = "..."  # encrypted into _token on save
  settings.save()
"""

from django.db import models
from django.db.models import Q

from framework.models import BaseEncrypted, BaseModel
from rekono.settings import AUTH_USER_MODEL
from security.authorization.roles import Role
from security.validators.input_validator import FutureDatetimeValidator, Regex, Validator


class TelegramSettings(BaseEncrypted):
    """Configuration of the Telegram bot, of which only one instance exists."""

    _token = models.TextField(
        max_length=200, validators=[Validator(Regex.SECRET, code="api_token")], null=True, blank=True, db_column="token"
    )

    _encrypted_field = "_token"


class TelegramChat(BaseModel):
    """Telegram chat that the bot talks to.

    A chat is created the first time that somebody writes to the bot, and it can
    only be used once it's linked to a Rekono account.

    Attributes:
        user: Rekono account that the chat is linked to.
        chat_id: Identifier that the chat has in Telegram.
        creation: Date when the chat wrote to the bot for the first time.
        otp: Code that the users need to link the chat to their account.
        otp_expiration: Date when that code stops being valid.
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
    otp = models.TextField(max_length=200, blank=True, null=True)
    otp_expiration = models.DateTimeField(
        blank=True,
        null=True,
        validators=[FutureDatetimeValidator(code="otp_expiration")],
    )

    def is_auditor(self) -> bool:
        """Check if the user of the chat can do more than read the data.

        Returns:
            Whether the user has the Auditor or the Admin role. False for a chat
            that isn't linked to any account yet.
        """
        return (
            self.user.groups.filter(Q(name=str(Role.AUDITOR)) | Q(name=str(Role.ADMIN))).exists()
            if self.user
            else False
        )

    def __str__(self) -> str:
        """Return the user of the chat and the chat identifier."""
        return f"{self.user.__str__()} - {self.chat_id}"
